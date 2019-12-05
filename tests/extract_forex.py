

import requests
import datetime as dt
import re
from collections import defaultdict
import numpy as np
import pandas as pd
import json

begin = dt.date(2018,1,1)
end = dt.date.today()
delta = dt.timedelta(days=1)
columns = [ "CAD",
            "HKD",
            "ISK",
            "PHP",
            "DKK",
            "HUF",
            "CZK",
            "GBP",
            "RON",
            "SEK",
            "IDR",
            "INR",
            "BRL",
            "RUB",
            "HRK",
            "JPY",
            "THB",
            "CHF",
            "EUR",
            "MYR",
            "BGN",
            "TRY",
            "CNY",
            "NOK",
            "NZD",
            "ZAR",
            "USD",
            "MXN",
            "SGD",
            "AUD",
            "ILS",
            "KRW",
            "PLN",
]
d = pd.DataFrame()
while begin<=end:
    param = begin.strftime('%Y-%m-%d')
    url = 'https://api.exchangeratesapi.io/' + param + '?base=HKD'
    txt = requests.get(url=url)
    record = json.loads(txt.text)
    for column in columns:
        if column in record['rates']:
            d.loc[param,column] = record['rates'][column]
        else:
            d.loc[param,column] = np.nan
    begin += delta
    print('Extracting date ', param)

d.to_csv('currency_HKD_based.csv')