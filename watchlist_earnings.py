#! /usr/bin/python2.7

import pandas as pd
import re
import bs4
import requests
import base64
import sys
import smtplib
import logging
import netrc


mainDir = ('/home/pavel/earningsCalendar/')
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
        earnings_url = 'http://www.nasdaq.com/earnings/report/' + ticker.lower()
        request = requests.get(earnings_url)
        soup = bs4.BeautifulSoup(request.text, 'html.parser')
        tag = soup.find(text=re.compile('Earnings announcement*'))
        return tag[tag.index(':') + 1:].strip()
    except:
        logging.exception("Pulling data failed")        
        

watch_list = ['UVXY', 
            'AAPL', 
            'DB', 
            'AMD', 
            'NFLX', 
            'TSLA', 
            'SNAP']

dates_dict = {sym:nasdaq_earnings_date(sym) for sym in watch_list}

df = pd.DataFrame.from_dict(dates_dict, orient='index')
df.columns = ['Date']

def send_email(user, pwd, recipient, body):
    '''Sending an email or text message via gmail smtp
    Code Source:
    (https://stackoverflow.com/questions/10147455/how-to-send-an-email
    -with-gmail-as-provider-using-python)

    TODO: add args, returns

    '''


    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    TEXT = body

    # Prepare actual message
    message = """From: %s\nTo: %s\n\n%s
    """ % (FROM, ", ".join(TO), TEXT)
    try:
        # SMTP_SSL Example
        server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server_ssl.ehlo() # optional, called by login()
        server_ssl.login(user, pwd)  
        # ssl server doesn't support or need tls,
        # so don't call server_ssl.starttls() 
        server_ssl.sendmail(FROM, TO, message)
        #server_ssl.quit()
        server_ssl.close()
        #print 'successfully sent message'
    except:
        logging.exception("Failed to send text")

creds = netrc.netrc('/home/pavel/.netrc')
username, account, password = creds.authenticators('serverone-g')

# Send out an email with the last prices of watchlist stocks
send_email(usr = username, 
            pwd = base64.b64decode(password), 
            recipient = account, 
            body = df.sort_values(by = 'Date')
            )

# TODO: add boilerplate