#! /usr/bin/python2.7

import pandas as pd
import re
import bs4
import requests
import base64
import logging
import os

import io_util

mainDir = os.path.dirname(os.path.abspath(__file__))
logFile = mainDir + 'watchlistEarnings.log'

# Set up the logging settings
logging.basicConfig(filename = logFile, 
                    level = logging.WARNING, 
                    format = '%(asctime)s - %(levelname)s - %(message)s')

def nasdaq_earnings_date(ticker=''):
    """Get the earnings date for the given ticker symbol. Perform a request to the
    nasdaq url and parse the response to find the earnings date.

    Args:
        ticker (str): The stock symbol/ticker to use for the lookup
    Return:
        String containing the earnings date
    """

    try:
        earnings_url = 'http://old.nasdaq.com/earnings/report/' + ticker.lower()
        request = requests.get(earnings_url)
        soup = bs4.BeautifulSoup(request.text, 'html.parser')
        tag = soup.find(text=re.compile('Earnings announcement*'))
        return tag[tag.index(':') + 1:].strip()
    except:
        logging.exception("Pulling data failed")        
        

watch_list = \
[
    'UVXY', 
    'AAPL', 
    'DB', 
    'AMD', 
    'NFLX', 
    'TSLA', 
    'SNAP'
]

dates_dict = {sym:nasdaq_earnings_date(sym) for sym in watch_list}

df = pd.DataFrame.from_dict(dates_dict, orient='index')
df.columns = ['Date']

username, account, password = io_util.get_creds('serverone-g')

# Send out an email with the next earnings date for watch_list symbols
io_util.send_email(user = username,
            pwd = base64.b64decode(password).decode('utf-8'),
            recipient = account,
            body = df.sort_values(by = 'Date')
            )
