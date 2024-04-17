from transformers import pipeline
import fmpsdk as fmp
from dotenv import load_dotenv
import os
import pandas as pd
from typing import Union, List

load_dotenv()
pipe = pipeline("text-classification", model="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis")

def sentiment_score(tickers :Union[str, List]=""):

    """
    Retrieves sentiment scores for given stock tickers based on recent financial news.

    Args:
        tickers (Union[str, List]): Single stock ticker or list of stock tickers. Defaults to "".

    Returns:
        dict: A dictionary containing sentiment scores for each stock ticker.
              Keys are stock tickers, and values are the difference between the counts of positive and negative sentiment labels.
              Positive values indicate overall positive sentiment, negative values indicate overall negative sentiment, and zero indicates neutral sentiment.
    """

    fmp_key = os.getenv('fmp_key')
    news = pd.DataFrame(fmp.stock_news(apikey=fmp_key, tickers=tickers, limit= len(tickers)*10))
    sentiment_data ={}

    for i in tickers:
        sentiment_data[i] = news[(news["symbol"] == i)][["text"]].iloc[:5]
        

    score = {}
    for key, df in sentiment_data.items():
        labels = []
        for row in df["text"]:
            [result] = pipe.predict(row)
            labels.append(result["label"])
        df["sentiment"] = labels
        neutral = labels.count("neutral")
        positive = labels.count("positive")
        negative = labels.count("negative")
        score[key] = positive-negative

    return score