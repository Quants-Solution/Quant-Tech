# closing_prices :
def daily_close_returns(tickers_list,per):
    import yfinance as yf
    import pandas as pd
    df = []
    for i in tickers_list:
        stock = yf.Ticker(i)
        data = stock.history(period=per)
        data = data.iloc[:,3]
        data = data.to_frame()
        data.columns = [i]
        df.append(data)
    closing_prices = pd.concat(df,axis=1,join='inner')
    returns = closing_prices.pct_change().dropna()
    return closing_prices,returns
# beta:
def beta(stock_daily_returns,bench_mark_returns):
    beta =[]
    for i in stock_daily_returns:
        b = stock_daily_returns[i].cov(bench_mark_returns.iloc[:,0])/bench_mark_returns.iloc[:,0].var()
        beta.append(round(b,2))
    return beta
# sector data:
def benchmark_data(sector):
    import yfinance as yf
    s = yf.Ticker(sector)
    sector_daily_data =s.history(period = '9mo')
    data = sector_daily_data.iloc[:,3].to_frame()
    data.columns = [sector]
    daily_returns = data.pct_change().dropna()
    return data,daily_returns

# ibkr daily data:
def data(Symbol,number_of_days='10 D',time='3 hrs'):
    import pandas as pd
    amd = Stock(Symbol,'SMART','USD')
    amd = ib.reqContractDetails(amd)
    contract_id = 0
    for i in amd:
        contract_id =i.contract.conId
    con_id=contract_id
    sec_contract = Contract(conId=con_id,symbol=Symbol,secIdType='STK',exchange='SMART')
    bars = ib.reqHistoricalData(
        sec_contract,
        endDateTime='',
        durationStr=number_of_days,
        barSizeSetting=time,
        whatToShow='TRADES',
        useRTH=False,
        formatDate=1,
        keepUpToDate=True)
    df =util.df(bars)
    df = df.set_index(df['date'])
    df = df.drop(columns=['date'])
    data_frame = pd.DataFrame(df)
    return data_frame,sec_contract