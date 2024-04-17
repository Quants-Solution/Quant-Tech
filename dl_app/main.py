from fastapi import FastAPI
from scripts import sentiment
from typing import List

app = FastAPI()

@app.get("/sentiment")
async def home():
    return {"text":"hello"}


@app.post("/sentiment")
async def sentiment_data(data: dict):
    symbols = data.get("data")
    score  = sentiment.sentiment_score(symbols)
    return score
