from fastapi import APIRouter, Depends, Request, Form, HTTPException
from sqlmodel import select
from ..db.session import get_session, SessionDep
from ..db.models import Card, Set, User
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter(prefix="/users")

templates = Jinja2Templates(directory="templates")

@router.get("/")
async def getUsers(request:Request, session:SessionDep):
    users = session.exec(select(User).order_by(User.name)).all()
    return templates.TemplateResponse(
        request=request, name="users/users.html", context={"users":users}
    )

@router.get("/add")
async def userForm(request:Request, session:SessionDep):
    return templates.TemplateResponse(
        request=request, name="users/add.html"
    )

@router.post("/add")
async def addUser(session:SessionDep, name:str=Form(...), email:str=Form(...)):
    db_user = User(name=name, email=email)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return RedirectResponse(url=f"/users/", status_code=302)

@router.post("/edit")
async def editUser(session:SessionDep, name:str=Form(...), email:str=Form(...), id:int=Form(...)):
    db_user = session.exec(select(User).where(User.id==id)).first()
    db_user.name = name
    db_user.email = email
    session.commit()
    session.refresh(db_user)
    return RedirectResponse(url=f"/users/", status_code=302)

@router.get("/{user_id}/edit")
async def userEditForm(request:Request, session:SessionDep, user_id:int):
    user = session.exec(select(User).where(User.id==user_id)).first()
    return templates.TemplateResponse(
        request=request, name="users/add.html", context={"user":user}
    )

@router.post("/{user_id}/delete")
async def userDelete(request:Request, session:SessionDep, user_id:int):
    db_user = session.exec(select(User).where(User.id==user_id)).first()
    session.delete(db_user)
    session.commit()
    return RedirectResponse(url=f"/users/", status_code=302)
