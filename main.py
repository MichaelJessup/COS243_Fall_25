from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Field, Session, SQLModel, Relationship, select
from contextlib import asynccontextmanager
from db.session import create_db_and_tables, SessionDep, engine
from random import choice
import json

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

templates = Jinja2Templates(directory="templates")
app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

class Set(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    cards: list["Card"] = Relationship(back_populates="set")

class Card(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    front: str
    back: str
    set_id: int | None = Field(default=None, foreign_key="set.id")
    set: Set | None = Relationship(back_populates="cards")

class User(BaseModel):
    id: int
    name: str
    email: str

cards = [
        Card(id = 1, front = "What is your quest?", back = "To seek the Holy Grail!", attempts = 0, correct = 0),
        Card(id = 2, front = "What is your favorite color?", back = "Green!", attempts = 0, correct = 0),
        Card(id = 3, front = "What is 2^2^2", back = "16", attempts = 0, correct = 0),
        Card(id = 4, front = "A trolley is speeding down to a fork in the track uncontrollably! A madman has tied a gopher onto one track, but, if you pull the conveniently placed lever, you can stop this crazy man's scheme! But wait! There's an endangered species of beetle on the other track! What should you do?", back = "Do nothing! That species of beetle is crucial to the ecosystem it is in! If you jeopardize its safety then the entire ecosystem could collapse!", attempts = 0, correct = 0),
        Card(id = 5, front = "A trolley is speeding down to a fork in the track uncontrollably! A madman has tied a train stop onto one track, but, if you pull the conveniently placed lever, you can stop this crazy man's scheme! What should you do?", back = "Do nothing! The train stop was set up to prevent the out of control trolley car from getting into a potentially dangerous accident!", attempts = 0, correct = 0),
        ]

users = [
        User(id = 1, name = "Jeffe Jefferson", email = "jjefferson@gmail.com"),
        User(id = 2, name = "Jeffe Jefferson III", email = "tresfetresferson@hotmail.com")
        ]

@app.get("/", response_class=HTMLResponse)
async def root(request:Request):
    #cards = session.exec(select(Card).order_by(Card.set_id)).all()
    return templates.TemplateResponse(
        request=request, name="index.html", context={"cards": cards}
    )

@app.get("/cards")
async def getCard(q:str = ""):
    #cards = session.exec(select(Card)).all()
    search_results = []
    for card in cards:
        if q.lower() in card.front.lower():
            search_results.append(card)
    return search_results

@app.get("/sets")
async def getSets(request:Request):
    with Session(engine) as session:
        sets = session.exec(select(Set).order_by(Set.name)).all()
        return templates.TemplateResponse(
            request=request, name="sets.html", context={"sets": sets}
        )

@app.get("/users")
async def getUsers(request:Request):
    #users = session.exec(select(User).order_by(User.name)).all()
    return templates.TemplateResponse(
        request=request, name="users.html", context={"users": users}
    )

@app.get("/cards/{card_id}", name="get_card")
async def getCardById(request:Request, card_id:int):
    for card in cards:
        if card.id == card_id:
            return templates.TemplateResponse(
                request=request, name="card.html", context={"card": card}
            )
    return None

@app.get("/sets/{set_id}", name="get_set")
async def getSetById(request:Request, set_id:int):
    with Session(engine) as session:
        set = session.exec(select(Set).where(Set.id == set_id)).first()
        return templates.TemplateResponse(
            request=request, name="set.html", context={"name": set.name, "cards": set.cards}
        )

@app.get("/play", response_class=HTMLResponse)
async def play(request:Request):
    return templates.TemplateResponse(
        request=request, name="play.html", context={"card": getRandomCard()}
    )

@app.post("/card/add")
async def addCard(card:Card):
    with Session(engine) as session:
        db_card = Card(front=card.front, back=card.back, set_id=card.set_id)
        session.add(db_card)
        session.commit()
        session.refresh(db_card)
        return db_card
    
@app.post("/sets/add")
async def addSet(session: SessionDep, set:Set):
    with Session(engine) as session:
        db_set = Set(name=set.name)
        session.add(db_set)
        session.commit()
        session.refresh(db_set)
        return db_set

#helper functions
def getRandomCard():
    return choice(cards)