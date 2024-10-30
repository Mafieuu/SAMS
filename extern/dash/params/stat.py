# stat.py
# Statistics on parameters

import numpy as np
import pandas as pd
from prophet import Prophet

from extern.dash.dt import dtmaker

models = {}


def calcMean(key: str, param: str):
    dt = dtmaker.transform(key)[[param]]
    mean = dt.mean().values
    return np.round(mean, 2)

def calcMin(key: str, param: str):
    dt = dtmaker.transform(key)[[param]]
    min = dt[param].min()
    date = dt[dt[param] == min].index[0]
    return min, date

def calcMax(key: str, param: str):
    dt = dtmaker.transform(key)[[param]]
    max = dt[param].max()
    date = dt[dt[param] == max].index[0]
    return max, date

def calcStd(key: str, param: str):
    dt = dtmaker.transform(key)[[param]]
    std = dt.std().values
    return np.round(std, 2)

def foreCast(key: str, param: str, period: int):
    dt = dtmaker.transform(key)[[param]].dropna(subset=[param])
    dt['ds'] = dt.index
    dt.rename(columns={param: 'y'}, inplace=True)
    model = models.get(f"model_{param}")
    if model is None:
        model = Prophet()
        model.fit(dt)
        models[f"model_{param}"] = model
    
    future = model.make_future_dataframe(periods=period, freq="d")
    fcst = model.predict(future)
    fcst = fcst[fcst['ds'] > dt['ds'].max()]
    return fcst

def showFcstTable(key: str, param: str, period: int):
    fcst = foreCast(key=key, param=param, period=period)
    fcst.rename(columns={'ds': 'Date', 'trend': 'Trend', 'yhat': param, 
                        'yhat_lower': 'Lower', 'yhat_upper': 'Upper'}, inplace=True)
    html = fcst[['Date', param, 'Lower', 'Upper', 'Trend']].round(2).to_html(index=False, escape=False)
    return html

def getCropsData(lat: float, lon: float, var: str, tech: str, year: str, crops: str, type: str = "country"):
    cropsT = f"{crops.lower()}_{tech.lower()}" if crops else []
    dt = dtmaker.getCountryData(lat, lon, var, tech, year, type)
    dt.columns = dt.columns.str.lower()
    dt = dt[['x', 'y', cropsT]]
    dt = dt.rename(columns={cropsT: "crop"})
    return dt


