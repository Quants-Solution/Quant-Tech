import pandas as pd, numpy as np, yfinance as yf
from .subpackages.daily_data import daily_close_returns ,beta,benchmark_data
import requests
import os
from dotenv import load_dotenv
import fmpsdk as fmp
import datetime
load_dotenv()

def sector_strength():
    fmp_key = os.getenv('fmp_key')
    sectors = ['XLK','XLY','XLC','XLE','XLB','XLP','XLV','XLI']
    closing_prices,returns = daily_close_returns(sectors,per = '5mo')
    allocations = 1/len(sectors)
    w = [0.125,0.125,0.125,0.125,0.125,0.125,0.125,0.125]
    bench_mark_product = returns.dot(w)
    bench_mark = (1+bench_mark_product).cumprod()
    bench_mark = bench_mark.dropna()
    
    
    all_sector_cumulation = []
    for i in returns:
        a = (1+returns[i]).cumprod()
        all_sector_cumulation.append(a)
    sector_cumulation = pd.concat(all_sector_cumulation,axis =1, join= 'inner')
    
    relative_strength = []
    for i in sector_cumulation:
        a = sector_cumulation[i]/bench_mark
        relative_strength.append(a)
    rs = pd.concat(relative_strength,axis = 1, join ='inner')
    rs.columns = closing_prices.columns
    rs = rs.dropna()
    
    r_strength = rs.rolling(window=5).mean().dropna()
    all_strength = pd.concat([r_strength,bench_mark],axis = 1,join = 'inner')
    all_strength= all_strength.rename(columns = {0:'b_mark'})
    
    today = datetime.date.today()
    strongest = []
    weakest = []
    for i in all_strength:
        if all_strength.loc[all_strength.index[-1],i] > all_strength.loc[all_strength.index[-1],'b_mark']:
            strongest.append(i)
        elif all_strength.loc[all_strength.index[-1],i] < all_strength.loc[all_strength.index[-1],'b_mark']:
            weakest.append(i)
    
    strongest.append('b_mark')
    weakest.append('b_mark')
    
    # strong = all_strength[strongest].hvplot(width=1000,height=600,logy=True)
    # weak =all_strength[weakest].hvplot(width=1000,height=600,logy=True)
    strong = all_strength[strongest]
    weak =all_strength[weakest]
    return strong,weak