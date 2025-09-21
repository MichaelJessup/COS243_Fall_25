from fastapi import APIRouter, Depends, Request, Form, HTTPException
from sqlmodel import select
from ..db.session import get_session, SessionDep
from ..db.models import Card, Set
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter(prefix="/sets")

templates = Jinja2Templates(directory="templates")

@router.get("/")
async def getSets(request:Request, session:SessionDep):
    sets = session.exec(select(Set).order_by(Set.name)).all()
    return templates.TemplateResponse(
        request=request, name="sets/sets.html", context={"sets":sets}
    )

@router.get("/add")
async def setForm(request:Request, session:SessionDep):
    return templates.TemplateResponse(
        request=request, name="sets/add.html"
    )

@router.post("/add")
async def addSet(session:SessionDep, name:str=Form(...)):
    db_set = Set(name=name)
    session.add(db_set)
    session.commit()
    session.refresh(db_set)
    return RedirectResponse(url=f"/sets/{db_set.id}", status_code=302)

@router.post("/edit")
async def editSet(session:SessionDep, name:str=Form(...), id:int=Form(...)):
    db_set = session.exec(select(Set).where(Set.id==id)).first()
    db_set.name = name
    session.commit()
    session.refresh(db_set)
    return RedirectResponse(url=f"/sets/{db_set.id}", status_code=302)

@router.get("/{set_id}", name="get_set")
async def getSetById(request:Request, set_id:int, session:SessionDep):
    set = session.exec(select(Set).where(Set.id == set_id)).first()
    return templates.TemplateResponse(
        request=request, name="sets/set.html", context={"id":set.id, "name":set.name, "cards":set.cards}
    )

@router.get("/{set_id}/edit")
async def setEditForm(request:Request, session:SessionDep, set_id:int):
    set = session.exec(select(Set).where(Set.id==set_id)).first()
    return templates.TemplateResponse(
        request=request, name="sets/add.html", context={"set":set}
    )

@router.post("/{set_id}/delete")
async def cardEditForm(request:Request, session:SessionDep, set_id:int):
    db_set = session.exec(select(Set).where(Set.id==set_id)).first()
    cards = session.exec(select(Card))
    for card in cards:
        if card.set_id == set_id:
            session.delete(card)
            session.commit()
    session.delete(db_set)
    session.commit()
    return RedirectResponse(url=f"/", status_code=302)
