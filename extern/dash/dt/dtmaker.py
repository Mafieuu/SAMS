import pandas as pd
import numpy as np
from datetime import date, timedelta
import os

from extern import fetch as f

start = "19950101"
end = date.today() - timedelta(days=2)
end = end.strftime("%Y%m%d")

def getData(key: str):
    return f.dtDict[key]

def transform(key: str):
    dates = pd.date_range(start=start, end=end, freq='D')
    df = pd.DataFrame(index=dates)
    params = getData(key)["data"]["properties"]["parameter"]
    for param, values in params.items():
        param_data = pd.Series(values)
        param_data.index = pd.to_datetime(param_data.index, format='%Y%m%d')
        df[param] = param_data

    df.replace(-999, np.nan, inplace=True)
    return df

def getLastNDays(key: str, n: int = 30, dec: int = 0):
    df = transform(key)
    return df.iloc[-7-int(n)-dec:-7]

def getCountryData(lat: float, lon: float, var: str, tech: str, year: str, type: str = "country"):
    if type == "country":
        chunks = []
        key = f.getKey(var, tech, year)
        for chunk in pd.read_csv(f.getKeyData(key), chunksize=10000, encoding="ISO-8859-1"):
            if year == "2010":
                filtered = chunk[chunk["iso3"] == f.getCountryFromPoint(lat, lon, year)]
            else:
                filtered = chunk[(chunk["FIPS0"] == f.getCountryFromPoint(lat, lon, year)[0]) | (chunk["ADM0_NAME"] == f.getCountryFromPoint(lat, lon, year)[1])]
            chunks.append(filtered)
        
        dt = pd.concat(chunks, ignore_index=True)
        return dt
    else:
        key = f.getKey(var, tech, year)
        return pd.read_csv(f.getKeyData(key), encoding="ISO-8859-1")





