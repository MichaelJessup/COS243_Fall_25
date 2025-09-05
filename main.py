from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import HTMLResponse

templates = Jinja2Templates(directory="templates")
app = FastAPI()

class Card(BaseModel):
    id: int
    question: str
    answer: str

cards = [
        Card(id = 1, question = "What is your quest?", answer = "To seek the Holy Grail!"),
        Card(id = 2, question = "What is your favorite color?", answer = "Green!"),
        Card(id = 3, question = "What is 2^2^2", answer = "16"),
        ]

#items_list = ["apple", "orange", "key lime"]

@app.get("/", response_class=HTMLResponse)
async def root(request:Request):
    return templates.TemplateResponse(
        request=request, name="index.html"
    )

#@app.get("/items")
#async def items():
#    return items_list

@app.get("/cards")
async def getCard(q:str = ""):
    search_results = []
    for card in cards:
        if q.lower() in card.question.lower():
            search_results.append(card)
    return search_results

@app.get("/cards/{card_id}")
async def getCardById(card_id:int):
    for i in range(len(cards)):
        if cards[i].id == card_id:
            return cards[i]
    return None

@app.post("/card/add")
async def addCard(card:Card):
    cards.append(card)
    return cards