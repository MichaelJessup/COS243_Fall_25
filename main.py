from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi import Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Field, Session, SQLModel, Relationship, select
from contextlib import asynccontextmanager
from .db.session import create_db_and_tables, SessionDep, engine, get_session
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

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str

@app.get("/", response_class=HTMLResponse)
async def root(request:Request):
    with Session(engine) as session:
        cards = session.exec(select(Card).order_by(Card.set_id)).all()
        return templates.TemplateResponse(
            request=request, name="index.html", context={"cards": cards}
        )

@app.get("/cards")
async def getCard(q:str = ""):
    with Session(engine) as session:
        cards = session.exec(select(Card).order_by(Card.set_id)).all()
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
    with Session(engine) as session:
        users = session.exec(select(User).order_by(User.name)).all()
        return templates.TemplateResponse(
            request=request, name="users.html", context={"users": users}
        )

@app.get("/cards/{card_id}", name="get_card")
async def getCardById(request:Request, card_id:int):
    with Session(engine) as session:
        cards = session.exec(select(Card).order_by(Card.set_id)).all()
        for card in cards:
            if card.id == card_id:
                return templates.TemplateResponse(
                    request=request, name="card.html", context={"card": card}
                )
        return templates.TemplateResponse(
            request=request, name="card.html", context={"card": Card(front="", back="", set_id=0)}
        )

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
@app.get("/lorem", response_class=HTMLResponse)
async def play(request:Request):
    return templates.TemplateResponse(
        request=request, name="lorem.html"
    )

@app.post("/card/add")
async def addCard(session:SessionDep, card:Card):
    with Session(engine) as session:
        db_card = Card(front=card.front, back=card.back, set_id=card.set_id)
        session.add(db_card)
        session.commit()
        session.refresh(db_card)
        return db_card
    
@app.post("/sets/add")
async def addSet(session:SessionDep, set:Set):
    with Session(engine) as session:
        db_set = Set(name=set.name)
        session.add(db_set)
        session.commit()
        session.refresh(db_set)
        return db_set

@app.post("/users/add")
async def addUser(session:SessionDep, user:User):
    with Session(engine) as session:
        db_user = User(name=user.name, email=user.email)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user

#helper functions
def getRandomCard():
    with Session(engine) as session:
        cards = session.exec(select(Card).order_by(Card.set_id)).all()
        return choice(cards)