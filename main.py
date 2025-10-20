from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi import Request, HTTPException, status, WebSocket, WebSocketDisconnect, Cookie, Form, HTTPException
from sqlmodel import select, Session
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Field, Session, SQLModel, Relationship, select
from contextlib import asynccontextmanager
from .db.session import create_db_and_tables, SessionDep, engine, get_session
from .db.models import Card, Set, User
from .routers import cards, play, sets, users
import json

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

templates = Jinja2Templates(directory="templates")
app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(cards.router)
app.include_router(sets.router)
app.include_router(users.router)
app.include_router(play.router)

@app.get("/", response_class=HTMLResponse)
async def root(request:Request, session:SessionDep):
    cards = session.exec(select(Card).order_by(Card.set_id)).all()
    return templates.TemplateResponse(
        request=request, name="index.html", context={"cards": cards}
    )

@app.get("/lorem", response_class=HTMLResponse)
async def lorem(request:Request):
    return templates.TemplateResponse(
        request=request, name="lorem.html"
    )

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.current_game: bool = False
        self.current_cards: list[Card] = []
        self.current_sets: list[Set] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.get("/game", response_class=HTMLResponse)
async def game_room(request:Request, session:SessionDep):
    sets = manager.current_sets
    cards = manager.current_cards
    return templates.TemplateResponse(
        request=request, name="play/game_room.html", context={"sets":sets, "cards":cards}
    )

@app.post("/game/start", response_class=HTMLResponse)
async def start_game(request:Request, session:SessionDep, data: str=Form(...)):
    jdata = json.loads(data)
    user_name = jdata["user_name"]
    set_ids = jdata["sets"]
    card_ids = jdata["cards"]

    sets = session.exec(select(Set).where(Set.id.in_(set_ids)).order_by(Set.name)).all()
    cards = session.exec(select(Card).where(Card.id.in_(card_ids)).order_by(Card.set_id)).all()

    manager.current_game = True
    manager.current_sets = sets
    manager.current_cards = cards

    return templates.TemplateResponse(
        request=request, name="play/game_room.html", context={"user_name":user_name, "sets":sets, "cards":cards}
    )

@app.post("/game/login")
async def enter_play(request:Request, session:SessionDep, response_class=HTMLResponse, user_name: str=Form(...)):
    sets = manager.current_sets
    cards = manager.current_cards
    response = templates.TemplateResponse(
        request=request, name="play/game_room.html", context={"user_name":user_name, "sets":sets, "cards":cards}
    )
    response.set_cookie(key="user_name",value=user_name, httponly=False)
    return response

@app.post("/game/setup")
async def game_setup(request:Request, session:SessionDep, response_class=HTMLResponse, user_name: str=Form(...)):
    sets = session.exec(select(Set).order_by(Set.name)).all()
    cards = session.exec(select(Card).order_by(Card.set_id)).all()
    response = templates.TemplateResponse(
        request=request, name="play/game_setup.html", context={"user_name":user_name, "sets":sets, "cards":cards}
    )
    response.set_cookie(key="user_name",value=user_name, httponly=False)
    return response

@app.get("/game/inactive")
async def say_if_there_is_a_game(request:Request, session:SessionDep):
    return manager.current_game

# Define a WebSocket endpoint at the path /ws/{client_id}
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str, session: SessionDep):
    
    # Accept the WebSocket connection and register it with the connection manager
    await manager.connect(websocket)

    try:
        # Keep the connection open and listen for incoming messages
        while True:           
            # Wait for a JSON message from the client
            data = await websocket.receive_json()
            
            if 'answer' in data['payload']:
                await manager.broadcast(f"{data['payload']}")
            elif 'start' in data['payload']:
                await manager.broadcast(f"{data['payload']}")
            elif 'end' in data['payload']:
                # Broadcast to user
                manager.current_game = False
                manager.current_sets = []
                manager.current_cards = []
                await manager.broadcast(f"{data['payload']}")
            elif 'secret' in data['payload']:
                # Broadcast to user
                await manager.send_personal_message(f"{data['payload']['secret']}", websocket)
            else:
                # Broadcast the chat message to all connected clients
                await manager.broadcast(f"{client_id} says: {data['payload']['message']}")

    # Handle client disconnects
    except WebSocketDisconnect:
        # Remove the client from the connection manager
        manager.disconnect(websocket)
        
        # Notify other clients that this client has left
        await manager.broadcast(f"Client #{client_id} left the chat")
