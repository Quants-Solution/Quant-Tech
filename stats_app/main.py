from typing import Union
import pandas as pd
import json
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from scripts import relative_strength, quantitative_analysis, treasuries, byop
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from typing import Union, List, Optional
import requests


templates = Jinja2Templates(directory="templates")
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/meet_the_team")
async def team(request: Request):
    return templates.TemplateResponse("meet_the_team.html", {"request" :request})


@app.get("/solutions")
async def solutions(request: Request):
    return templates.TemplateResponse("solutions.html", {"request": request})

@app.get("/research")
async def research(request: Request):
    a, b = relative_strength.sector_strength()
    fig1 = px.line(a, x=a.index, y=a.columns)
    plot_html1 = fig1.to_html(full_html=False)
    fig = px.line(b, x=b.index, y=b.columns)
    plot_html2 = fig.to_html(full_html=False)

    return templates.TemplateResponse(
        "research.html",
        {
            "request": request,
            "plot1": plot_html1,
            "plot2": plot_html2,
        },
    )


@app.post("/research")
async def research(request: Request, symbol: Optional[str] = Form(...)):

    a, b = relative_strength.sector_strength()
    fig1 = px.line(a, x=a.index, y=a.columns)
    plot_html1 = fig1.to_html(full_html=False)
    fig = px.line(b, x=b.index, y=b.columns)
    plot_html2 = fig.to_html(full_html=False)


    if symbol is None:
        financial_health_html = ""
        valuation_html = ""
        revByinv_fig_html =""
    else:
        if isinstance(symbol, str):
            symbols = [symbol]
        elif isinstance(symbol, list):
            symbols = symbol
        else:
            raise ValueError("Symbol must be a string or a list of strings")
        financial_health_html = ""
        valuation_html = ""
       
        
        symbols = [i for x in symbols for i in x.replace(" ", "").split(",")]
        symbols = [symbol.upper() if not symbol.isupper() else symbol for symbol in symbols]
        print("------------------------------------------")

        response = requests.post("http://dl-app-container/sentiment",json={"data":symbols})
        resp = response.json()

        sentiment = pd.DataFrame(resp,index= ["Symbols"])
    
        print(resp)
        print(symbols)

        rev_by_inv = quantitative_analysis.profitabilty(symbol=symbols)
        financial_health, valuation = quantitative_analysis.get_company_data(
            symbol=symbols
        )

        # Generate bar graphs for financial health and valuation using Plotly
        financial_health_fig = px.bar(
            financial_health,
            x=financial_health.index,
            y=financial_health.columns,
            labels={"x": "Metrics", "y": "Values"},
            title="Financial Health",
            log_y=True,
            barmode="group",
        )
        valuation_fig = px.bar(
            valuation,
            x=valuation.index,
            y=valuation.columns,
            labels={"x": "Metrics", "y": "Values"},
            title="Valuation",
            log_y=True,
            barmode="group",
        )
        revByinv_fig = px.line(
            rev_by_inv,
            x="date",
            y=rev_by_inv.columns,
            labels={"x": "Date", "y": "Revenue/Inventory"},
        )

        sentiment_fig = px.bar(
            sentiment,
            barmode="group",
        )
        sentiment_fig.update_xaxes(title_text="Stocks")


        # Convert the Plotly bar graphs to HTML code
        financial_health_html = financial_health_fig.to_html(full_html=False)
        valuation_html = valuation_fig.to_html(full_html=False)
        revByinv_fig_html = revByinv_fig.to_html(full_html=False)
        sentiment_fig_html = sentiment_fig.to_html(full_html=False)


    return templates.TemplateResponse(
        "research.html",
        {
            "request": request,
            "financial_health": financial_health_html,
            "valuation": valuation_html,
            "RevByInv": revByinv_fig_html,
            "sentiment": sentiment_fig_html,
            "plot1": plot_html1,
            "plot2": plot_html2,
        },
    )


@app.get("/research/yields")
async def yields(request: Request, selection: datetime = None):
    yields_data = treasuries.yields_data()
    datetime_string = ["2000-11-30", "2007-02-28"]
    crash_2000 = yields_data.loc[[datetime_string[0]]].T
    fig_2000 = px.line(crash_2000, x=crash_2000.index, y=datetime_string[0])
    fig_2000_html = fig_2000.to_html(full_html=False)

    crash_2007 = yields_data.loc[[datetime_string[1]]].T
    fig_2007 = px.line(crash_2007, x=crash_2007.index, y=datetime_string[1])
    fig_2007_html = fig_2007.to_html(full_html=False)
  
    if selection is None:
        current_data = yields_data.iloc[[-1]].T
        [y] = current_data.columns
        fig_current = px.line(current_data, x=current_data.index, y=y)
        yield_html = fig_current.to_html(full_html=False)
        
    else:
        # selection = selection.strftime("%Y-%m-%d")
        data = yields_data.loc[[selection]].T
        print(type(selection))
         

        fig = px.line(data, x=data.index, y=selection)
        

        yield_html = fig.to_html(full_html=False)
        
    return templates.TemplateResponse(
        "yields.html",
        {"request": request,
        "dates": yields_data.index, 
        "yields_graph": yield_html,
        "crash_2000": fig_2000_html,
        "crash_2007":fig_2007_html
        },
    )


@app.get("/investments")
async def investments(request: Request, symbol:Optional[str] = None):
    if symbol is None:
        mc_fig_html = ""
        volatility_fig_html =""
        stats_fig_html = ""
        volume_fig_html = ""
    else:
        if isinstance(symbol, str):
            symbols = [symbol]
        elif isinstance(symbol, list):
            symbols = symbol
        else:
            raise ValueError("Symbol must be a string or a list of strings")
        
        symbols = [i for x in symbols for i in x.replace(" ", "").split(",")]
        symbols = [symbol.upper() if not symbol.isupper() else symbol for symbol in symbols]
        stocks_vol, traces, mc_stats, es, volume_prof = byop.make_your_portfolio(symbols)
        layout = go.Layout(title='Time Series Data',
                   xaxis=dict(title='Date'),
                   yaxis=dict(title='Value'))

        mc_fig = go.Figure(data=traces, layout=layout)

        volatility_fig = px.bar(
            stocks_vol,
            x=stocks_vol.index,
            y=stocks_vol.columns,
            labels={"x": "Metrics", "y": "Values"},
            title="Volatility",
            log_y=True,
            barmode="group",
        )

        stats_fig = px.bar(
            mc_stats,
            x=mc_stats.index,
            y=mc_stats.columns,
            labels={"x": "stats", "y": "Values"},
            title="MC Stats.",
            log_y=True,
            barmode="group",
        )
        volume_fig = px.bar(
            volume_prof.T,
            # x=volume_prof.index,
            # y=volume_prof.columns,
            labels={"x": "Ticker", "y": "Values"},
            title="Volume Profile",
            log_y=True,
            barmode="group",
        )


        mc_fig_html = mc_fig.to_html(full_html=False)
        volatility_fig_html = volatility_fig.to_html(full_html=False)
        stats_fig_html = stats_fig.to_html(full_html=False)
        volume_fig_html = volume_fig.to_html(full_html=False) 

    return templates.TemplateResponse("investments.html", 
                                      {"request": request,
                                        "mc_forecast": mc_fig_html,
                                          "volatility": volatility_fig_html,
                                          "stats": stats_fig_html,
                                          "volume_profile": volume_fig_html
                                                            })
    


@app.get("/test")
async def test(request: Request):
    return {"message": "successfull"}
