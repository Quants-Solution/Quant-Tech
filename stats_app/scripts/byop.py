import pandas as pd
import numpy as np
from .subpackages.MCForecastTools import MCSimulation
import yfinance as yf
import datetime as dt
from itertools import combinations
import plotly.graph_objs as go
import plotly.io as pio

def make_your_portfolio(symbols):


    """
    Analyzes a portfolio of stocks using historical data and Monte Carlo simulations.

    Args:
        symbols (list): List of stock symbols to analyze.

    Returns:
        tuple: A tuple containing the following elements:
            - stocks_volatility (pd.Series): Volatility of each stock in the portfolio.
            - mc_returns (pd.DataFrame): Monte Carlo simulated cumulative returns of the portfolio.
            - mc_stats (pd.Series): Summary statistics of the Monte Carlo simulated cumulative returns.
            - es (float): Expected shortfall (conditional value-at-risk) of the portfolio.
            - volume_profile (pd.DataFrame): Volume profile of the stocks in the portfolio.

    This function retrieves historical stock data for each symbol provided, calculates the returns and volatility of the stocks,
    optimizes the portfolio by finding the best combination of weights, performs Monte Carlo simulations to forecast the portfolio returns,
    calculates expected shortfall, and analyzes the volume profile of the stocks.
    """


    if isinstance(symbols, str):
            symbols = [symbols]
    elif isinstance(symbols, list):
            symbols = symbols
    else:
        raise ValueError("Symbol must be a string or a list of strings")

    start_time = dt.datetime.now().date() -dt.timedelta(days=5*365)


    close_data = {}
    vol_data = {}
    for i in symbols:
        data = yf.download(i,start=start_time)
        close_data[i] =data[["Close"]]
        close_data[i] = close_data[i].rename(columns = {"Close":i})
        vol_data[i] = data[["Volume"]].rename(columns = {"Volume": i + "_vol"})

    price_data = pd.concat(close_data.values(),axis=1)
    returns = price_data.pct_change().dropna()

    # Volatility:
    stocks_volatility =  round((returns.std()*np.sqrt(7)), 2)
    stocks_volatility = pd.DataFrame({"Tickers" : stocks_volatility})

    def combination_weights(data,initial_investment):
        df = []                                                                      
        possible_combinations = []                                                   
        a = list(np.arange(0.05,1,0.01))                                             
        random_set = [round(i,3) for i in a]                                         
        
        comb = combinations(random_set,len(data.columns))                            

        possible_combinations = [i for i in comb if sum(i) == 1]                     
        daily_returns = data                                  
        for i in possible_combinations:                                              
            possible_returns = daily_returns.dot(i)
            cumulative_final_return = (1 + possible_returns).cumprod()
            final_day_value = cumulative_final_return.iloc[-1]
            final_return = final_day_value*initial_investment
            df.append((final_return,i))
        data_frame = pd.DataFrame(df)                                                
        best_combination = data_frame.rename(columns={0:'Return',1:'Weights'})       
        top = best_combination.nlargest(1,'Return')                                
        return top
    
    weight = combination_weights(returns,1000)
    best_weight = weight["Weights"].iloc[0]

    portfolio = returns.dot(best_weight)

    MC_fiveyear = MCSimulation(
        portfolio_data = price_data,
        weights = best_weight,
        num_simulation = 252,
        num_trading_days = 252*1
    )

    # MC returns to eb plotted:
    mc_returns = MC_fiveyear.calc_cumulative_return()
    traces = []

    # Iterate over each column in the DataFrame
    for column in mc_returns.columns:
        # Create a trace for each column
        trace = go.Scatter(x=mc_returns.index, y=mc_returns[column], mode='lines', name=column)
        traces.append(trace)



    # MC stats to be returned:
    mc_stats = MC_fiveyear.summarize_cumulative_return()
    mc_stats = pd.DataFrame({"stats": mc_stats}).iloc[1:]
    def expected_shortfall(returns, alpha=0.05):
        sorted_returns = np.sort(returns)
        n = len(sorted_returns)
        alpha_index = int(np.floor(alpha * n))
        es = np.mean(sorted_returns[:alpha_index])
        return es
    

    # expexted One day shorfall:
    es = round(expected_shortfall(portfolio) * 100,3)

    # Volume Profile:
    volume = pd.concat(vol_data.values(),axis=1)
    volume_stats = volume.pct_change()
    upper_boud =   volume.mean() + (volume.std())
    lower_boud =    volume.mean() - (volume.std())
    volume_profile = pd.DataFrame({"upper_boud" : upper_boud, "lower_boud" : lower_boud})

    return stocks_volatility, traces, mc_stats, es, volume_profile