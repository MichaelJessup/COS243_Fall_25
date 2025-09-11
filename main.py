from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from random import choice

templates = Jinja2Templates(directory="templates")
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

class Card(BaseModel):
    id: int
    question: str
    answer: str
    attempts: int
    correct: int

class Set(BaseModel):
    id: int
    cards: list[Card]

class User(BaseModel):
    id: int
    name: str
    email: str
    sets: list[Set]

cards = [
        Card(id = 1, question = "What is your quest?", answer = "To seek the Holy Grail!", attempts = 0, correct = 0),
        Card(id = 2, question = "What is your favorite color?", answer = "Green!", attempts = 0, correct = 0),
        Card(id = 3, question = "What is 2^2^2", answer = "16", attempts = 0, correct = 0),
        Card(id = 4, question = "A trolley is speeding down to a fork in the track uncontrollably! A madman has tied a gopher onto one track, but, if you pull the conveniently placed lever, you can stop this crazy man's scheme! But wait! There's an endangered species of beetle on the other track! What should you do?", answer = "Do nothing! That species of beetle is crucial to the ecosystem it is in! If you jeopardize its safety then the entire ecosystem could collapse!", attempts = 0, correct = 0),
        Card(id = 5, question = "A trolley is speeding down to a fork in the track uncontrollably! A madman has tied a train stop onto one track, but, if you pull the conveniently placed lever, you can stop this crazy man's scheme! What should you do?", answer = "Do nothing! The train stop was set up to prevent the out of control trolley car from getting into a potentially dangerous accident!", attempts = 0, correct = 0),
        ]

sets =  [
        Set(id = 1, cards = cards[0:2]),
        Set(id = 2, cards = cards[2:])
        ]

users = [
        User(id = 1, name = "Jeffe Jefferson", email = "jjefferson@gmail.com", sets = [sets[0]]),
        User(id = 2, name = "Jeffe Jefferson III", email = "tresfetresferson@hotmail.com", sets = [sets[1]])
        ]

@app.get("/", response_class=HTMLResponse)
async def root(request:Request):
    return templates.TemplateResponse(
        request=request, name="index.html", context={"cards": cards}
    )

@app.get("/cards")
async def getCard(q:str = ""):
    search_results = []
    for card in cards:
        if q.lower() in card.question.lower():
            search_results.append(card)
    return search_results

@app.get("/sets")
async def getSets(request:Request):
    return templates.TemplateResponse(
        request=request, name="sets.html", context={"sets": sets}
    )

@app.get("/users")
async def getUsers(request:Request):
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

@app.post("/card/add")
async def addCard(card:Card):
    cards.append(card)
    return cards
    
@app.get("/play", response_class=HTMLResponse)
async def play(request:Request):
    return templates.TemplateResponse(
        request=request, name="play.html", context={"card": getRandomCard()}
    )

#helper functions
def getRandomCard():
    return choice(cards)