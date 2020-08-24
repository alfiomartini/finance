import os
import requests
import urllib.parse
from pprint import pprint as pp
from datetime import datetime

# https://iexcloud.io/docs/api/#historical-prices
def chart(symbol, range):
    # accepted range string values : '1m', '6m', '5d'

    # Contact API
    try:
        api_key = os.environ.get("FINANCE_KEY")
        json_response = requests.get(f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/chart/{range}?token={api_key}")
        json_response.raise_for_status()
    except requests.RequestException:
        return None
    else:
        # response is in json notation. json() is a json decoder, i.e,
        # maps json back to object format
        # see https://requests.readthedocs.io/en/master/user/quickstart/
        return json_response
        
         
json_resp = chart('FB','5d')
json_obj = json_resp.json()
chart = {}
labels = []
data = []
for item in json_obj:
    date = datetime.strptime(item['date'], '%Y-%m-%d')
    date_str = date.strftime('%m/%d')
    # print(date_str)
    labels.append(date_str)
    data.append(item['close'])
chart['labels'] = labels
chart['data'] = data
print(chart)