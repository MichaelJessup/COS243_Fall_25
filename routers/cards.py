from fastapi import APIRouter, Depends, Request, Form, HTTPException
from sqlmodel import select
from ..db.session import get_session, SessionDep
from ..db.models import Card, Set
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter(prefix="/cards")

templates = Jinja2Templates(directory="templates")

@router.get("/")
async def getCards(request:Request, session:SessionDep):
    cards = session.exec(select(Card).order_by(Card.set_id)).all()
    return templates.TemplateResponse(
    	request=request, name="cards/cards.html", context={"cards":cards}
    )

@router.get("/add")
async def cardForm(request:Request, session:SessionDep):
	sets = session.exec(select(Set).order_by(Set.name)).all()
	return templates.TemplateResponse(
		request=request, name="cards/add.html", context={"sets":sets}
	)

@router.post("/add")
async def addCard(session:SessionDep, front:str=Form(...), back:str=Form(...), set_id:int=Form(...)):
    db_card = Card(front=front, back=back, set_id=set_id)
    session.add(db_card)
    session.commit()
    session.refresh(db_card)
    return RedirectResponse(url=f"/cards/{db_card.id}", status_code=302)

@router.post("/edit")
async def editCard(session:SessionDep, front:str=Form(...), back:str=Form(...), set_id:int=Form(...), id:int=Form(...)):
    db_card = session.exec(select(Card).where(Card.id==id)).first()
    db_card.front = front
    db_card.back = back
    db_card.set_id = set_id
    session.commit()
    session.refresh(db_card)
    return RedirectResponse(url=f"/cards/{db_card.id}", status_code=302)

@router.get("/{card_id}", name="get_card")
async def getCardById(request:Request, card_id:int, session:SessionDep):
    cards = session.exec(select(Card).order_by(Card.set_id)).all()
    for card in cards:
        if card.id == card_id:
            return templates.TemplateResponse(
                request=request, name="cards/card.html", context={"card":card}
            )
    return templates.TemplateResponse(
        request=request, name="cards/card.html", context={"card": Card(front="", back="", set_id=0)}
    )

@router.get("/{card_id}/edit")
async def cardEditForm(request:Request, session:SessionDep, card_id:int):
	card = session.exec(select(Card).where(Card.id==card_id)).first()
	sets = session.exec(select(Set).order_by(Set.name)).all()
	return templates.TemplateResponse(
		request=request, name="cards/add.html", context={"card":card, "sets":sets}
	)

@router.post("/{card_id}/delete")
async def cardDelete(request:Request, session:SessionDep, card_id:int):
	db_card = session.exec(select(Card).where(Card.id==card_id)).first()
	session.delete(db_card)
	session.commit()
	return RedirectResponse(url=f"/", status_code=302)
