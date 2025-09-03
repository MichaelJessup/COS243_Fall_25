from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "hello world"}

@app.get("/items")
async def items():
    return {"message": "LIST OF ITEMS"}
