from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi import Request, HTTPException, status
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
