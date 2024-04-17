import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense,LSTM,Dropout
import yfinance as yf
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow import keras
import joblib
import datetime as dt



start_time = dt.datetime.now().date() -dt.timedelta(days=100)
data = yf.download("^GSPC",start=start_time)[["Close","Volume"]]

input_scaler = joblib.load("./model_components/x_scaler.joblib")
output_scaler = joblib.load("./model_components/y_scaler.joblib")
model = load_model("./model_components/lstm.h5")

input_scaled = input_scaler.transform(data.iloc[-60:,:]).reshape((1,60,2))


