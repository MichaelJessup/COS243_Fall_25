from fastapi import APIRouter, Depends, Request, Form, HTTPException
from sqlmodel import select, Session
from ..db.session import get_session, SessionDep
from ..db.models import Card, Set
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from random import choice

router = APIRouter(prefix="/play")

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def play(request:Request, session:SessionDep):
    return templates.TemplateResponse(
        request=request, name="play/play.html", context={"card": getRandomCard(session)}
    )

#helper function
def getRandomCard(session:SessionDep):
    cards = session.exec(select(Card).order_by(Card.set_id)).all()
    return choice(cards)
