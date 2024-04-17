import fmpsdk as fmp
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()



def get_company_data(symbol, duration="quarter"):
    load_dotenv("./scripts/.env")
    fmp_key = os.environ.get("FMP_KEY")
    """
    Retrieve financial data for a company.

    Parameters:
        symbol (str): The stock symbol of the company.
        duration (str): The duration of the financial data ('annual' or 'quarterly').

    Returns:
        tuple: A tuple containing two pandas DataFrames:
            - The first DataFrame contains health-related financial metrics.
            - The second DataFrame contains valuation-related financial metrics.
    """
    if isinstance(symbol, str):
            symbols = [symbol]
    elif isinstance(symbol, list):
            symbols = symbol
    else:
        raise ValueError("Symbol must be a string or a list of strings")
    # Retrieve company profile

    health_dataframes = []
    valuation_dataframe = []
    for symbol in symbols:
        company_profile = fmp.company_profile(apikey=fmp_key, symbol=symbol)
        last = company_profile[0]['price']
        mcap = company_profile[0]['mktCap']
        # industry = company_profile[0]['industry']
        
        # Retrieve key metrics
        key_metrics = fmp.key_metrics_ttm(apikey=fmp_key, symbol=symbol)
        eps_ttm = round(key_metrics[0]['netIncomePerShareTTM'], 2)
        pe_ttm = round(key_metrics[0]['peRatioTTM'], 2)
        
        # Retrieve income statement
        inc_statement = fmp.income_statement(apikey=fmp_key, symbol=symbol, period=duration)
        shares = inc_statement[0]['weightedAverageShsOut']
        net_income = inc_statement[0]['netIncome']
        
        # Retrieve balance sheet
        financials = fmp.balance_sheet_statement(apikey=fmp_key, symbol=symbol, period=duration)
        current_assets = financials[0]['cashAndShortTermInvestments'] + financials[0]['inventory'] + \
                        (financials[0]['netReceivables'] / 2) + financials[0]['otherCurrentAssets']
        cash_share = round(financials[0]['cashAndCashEquivalents'] / shares, 2)
        total_ratio = round(financials[0]['totalAssets'] / financials[0]['totalLiabilities'], 2)
        net_current_assets = current_assets - financials[0]['totalCurrentLiabilities']
        liability_share = round(financials[0]['totalCurrentLiabilities'] / shares, 2)
        tangible_assets = (financials[0]['propertyPlantEquipmentNet'] / 2) + net_current_assets
        inv_yield = round(net_income / mcap, 3)
        operating_margin = inc_statement[0]['operatingIncomeRatio']
        bvps = round(tangible_assets / shares, 2)
        bvps_price = bvps / last
        current_ratio = round(financials[0]['totalCurrentAssets'] / financials[0]['totalCurrentLiabilities'], 2)
        
        # Retrieve earnings surprise
        earnings = fmp.earnings_surprises(apikey=fmp_key, symbol=symbol)
        earning = pd.DataFrame.from_dict(earnings)
        earning.index = earning['date']
        earning = earning.drop(columns='date')
        earning = earning.sort_index()
        fq_eps = earning.iloc[-5:, 1].mean()
        
        # Create data frames
        company_health = {'BVPS': [bvps], 'Cash/share': [cash_share], 'liability_share': [liability_share],
                        'EPS_ttm': [eps_ttm], 'fq_eps': [fq_eps],}
        company_valuation = {'BVPS/Price': [bvps_price], 'P/E': [pe_ttm], 'Inv_Yield': [inv_yield],
                            'Current_ratio': [current_ratio], 'Total_Ratio': [total_ratio], }
        
        health_df = pd.DataFrame(company_health, index=[symbol]).T
        health_dataframes.append(health_df)
        valuation_df = pd.DataFrame(company_valuation, index=[symbol]).T
        valuation_dataframe.append(valuation_df)
    health = pd.concat(health_dataframes)
    valuation = pd.concat(valuation_dataframe)
    
    return health, valuation


def profitabilty(symbol, duration="quarter"):
    load_dotenv("./scripts/.env")
    fmp_key = os.environ.get("FMP_KEY")

    if isinstance(symbol, str):
            symbols = [symbol]
    elif isinstance(symbol, list):
            symbols = symbol
    else:
        raise ValueError("Symbol must be a string or a list of strings")
    # Retrieve company profile

    revenue_data = {}
    for symbol in symbols:
        revenue = pd.DataFrame(fmp.income_statement(symbol=symbol, apikey=fmp_key,period="quarter"))[["date","revenue"]]
        inventory = pd.DataFrame(fmp.cash_flow_statement(symbol=symbol ,apikey=fmp_key,period="quarter"))[['date','inventory']]
        revenue[symbol] = revenue["revenue"] / inventory["inventory"]
        revenue_data[symbol] = revenue
    # data = pd.DataFrame(revenue_data)
    combined_data = pd.DataFrame()
    for i, x in revenue_data.items():
        date = x["date"]
        combined_data = pd.concat([combined_data, x[[i]]],axis=1,join="outer")
    combined_data["date"] =  date
    return combined_data
