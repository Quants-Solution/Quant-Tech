import pandas as pd 
import numpy as np
import datetime
import quandl as ql


def yields_data():
    yields = ql.get("USTREASURY/YIELD")
    yields_data = yields.loc["2000-01-01":]
    yields_monthly = yields_data.resample("ME").mean()
    return yields_monthly