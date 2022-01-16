import requests
import datetime as dt
import os
from twilio.rest import Client

STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"
API_KEY = os.environ.get("API_KEY")

SMS_NUMBER = os.environ.get("SMS_NUMBER")
SMS_TARGET_NUMBER = os.environ.get("SMS_TARGET_NUMBER")
SMS_SID = os.environ.get("SMS_SID")
SMS_AUTH = os.environ.get("SMS_AUTH")

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

# When stock price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
stock_params = {
    'function': 'TIME_SERIES_DAILY',
    'symbol': STOCK_NAME,
    'apikey': API_KEY
}

news_param = {
    'apiKey': '326e0eff3aa84e07896e2443629959b7',
    'qInTitle': COMPANY_NAME
}

def get_stock_data():
    global STOCK_ENDPOINT, stock_params
    response = requests.get(STOCK_ENDPOINT, params=stock_params)
    data = response.json()['Time Series (Daily)']
    return data

stock_data = get_stock_data()
value_list = [value for (key, value) in stock_data.items()]
yesterday_value = value_list[0]['4. close']
prior_yesterday_value = value_list[1]['4. close']

delta = float(yesterday_value) - float(prior_yesterday_value)
if delta > 0:
    up_down = "🔥"
else:
    up_down = "🔻"

percent_delta = round((delta / float(prior_yesterday_value)) * 100)

if percent_delta > 5:
    r = requests.get(NEWS_ENDPOINT, params=news_param)
    news_data = r.json()
    articles = news_data['articles']
    top_three_articles = articles[:3]

    article_list = [f"{STOCK_NAME}: {up_down}{percent_delta}%\nHeadline: {article['title']}.\nBrief: {article['description']}" for article in top_three_articles]

    client = Client(SMS_SID, SMS_AUTH)

    for article in article_list:
        message = client.messages.create(
            body=article,
            from_=SMS_NUMBER,
            to=SMS_TARGET_NUMBER,
        )
else:
    print('Not newsworthy')