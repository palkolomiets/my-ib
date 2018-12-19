#! /usr/bin/python2.7

from Robinhood import Robinhood
import pandas as pd
import datetime
import sys
import smtplib
import base64
import sqlite3
import logging
import netrc


mainDir = ('/home/ubuntu/rtStockPrices/')
logFile = mainDir + 'rtPrices.log'
dbName = mainDir + 'rtPrices.db'

#==============================================================================
# mainDir = ('C:/Users/Pavel/Desktop/')
# logFile = mainDir + 'rtPrices.log'
# dbName = mainDir + 'rtPrices.db'
#==============================================================================

# Set up the logging settings
logging.basicConfig(filename = logFile
                    , level = logging.WARNING
                    , format = '%(asctime)s - %(levelname)s - %(message)s')

# List of stocks to collect data on
watch_list = \
[
    'SDS'
    ,'AAPL'
    ,'DB'
    ,'AMD'
    ,'NFLX'
    ,'TSLA'
    ,'SNAP'
    ,'APRN'
]

# List of relevant columns
cols = \
[
    'updated_at',
    'symbol',
    'last_trade_price',
    'adjusted_previous_close'
]

"""
con.execute('''CREATE TABLE IF NOT EXISTS robinhood(
                    updated_at TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    last_trade_price REAL NOT NULL,
                    adjusted_previous_close REAL NOT NULL)''')
"""

my_trader = Robinhood()

creds = netrc.netrc('/home/ubuntu/.netrc')
username_rh, account_rh, password_rh = creds.authenticators('serverone-rh')
username, account, password = creds.authenticators('serverone-g')

logged_in = my_trader.login(username=username_rh,
                            password=base64.b64decode(password_rh).decode('ascii'))


try:
    try:     
        # Open database connection
        con = sqlite3.connect(dbName)
        ## Load the existing stock prices file
        oldPrices = pd.read_sql('select * from robinhood', con)
        ## Pull the real time data into a dataframe
        pre = pd.DataFrame(my_trader.quotes_data(watch_list))
        ## Keep relevant columns
        rtp = oldPrices.append(pre[cols])
        
    except IOError:
        pre = pd.DataFrame(my_trader.quotes_data(watch_list))
        ## Keep relevant columns
        rtp = pre[cols]
         
    rtp['updated_at'] = pd.to_datetime(rtp['updated_at'])
    
    # TODO Calculate the velocity and acceleration of the price
    # Insert the length of the watchlist back into the database
    rtp.tail(len(watch_list)).to_sql('robinhood', 
                                    con, 
                                    index = False, 
                                    if_exists = 'append')
    con.close()
    # Set the last trade time as the index
    rtp.set_index('updated_at', inplace = True)

except: # catch all exceptions
    logging.exception("Pulling data failed:")

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


## Sending a text if the price satisfies a certain condition
for symbol in watch_list:
    # Add .copy to remove copy on a slice from dataframe warning
    symPrice = rtp[rtp['symbol'] == symbol].copy()

    # Change the last_trade_price from an object to a number
    symPrice['last_trade_price'] = pd.to_numeric(symPrice['last_trade_price'])
    # Select relevent columns in new df
    symPrice = symPrice[['symbol', 'last_trade_price']].tail(15)
    # Drop duplicate rows
    symPrice.drop_duplicates(inplace = True)
    # Find the percent change between current period and previous period
    symPrice['priceChange'] = symPrice['last_trade_price'].pct_change()
    #rtp2['priceChange2'] = rtp2['LastTradePrice'].pct_change(periods = 2)
    # TODO adjust for stock splits to reduce unnecessary text messages
    
    lastTime = symPrice[symPrice.index == symPrice.index.max()]
    # Send a text if the price change in the latest period was greater than 2%
    # Use iloc to compare the actual value rather than the entire series
    if abs(lastTime['priceChange'].iloc[0]) >= 0.02: 
        # Send a text with the current price and the price change
        send_email(user = username,
                    pwd = base64.b64decode(password),
                    recipient = account, 
                    body = (lastTime['symbol'].iloc[0] 
                        + ' 5 Min % Change:' 
                        + '\n'
                        + str(round(lastTime['priceChange'].iloc[0], 2)))
                    )

# Name the current time
now = datetime.datetime.now()
# Name one day in the past
yday = now - datetime.timedelta(days = 1)
# Set the hours the report will be sent out
for reportHour in [10, 12, 15]:
    if now.hour == reportHour and now.minute <= 4:
        watched = rtp[['symbol', 'last_trade_price']].tail(len(watchList))
        try:
            ydayDf = rtp[rtp.index <= yday][['symbol', 'last_trade_price']]
        except:
            ydayDf = pd.DataFrame()
        
        toTxt = ydayDf.append(watched)
        # Change the last_trade_price from an object to a number
        toTxt['last_trade_price'] = pd.to_numeric(toTxt['last_trade_price'])      
        # Reset index to compute pct change on subsequent rows
        # Need to do this because the timestamps dont match
        toTxt.reset_index(inplace = True)
        # Percent change by stock symbol
        symGroup = toTxt.groupby('symbol')['last_trade_price']
        toTxt['dayPct'] = symGroup.pct_change().round(decimals = 3) * 100
        
        sendCols = ['symbol', 'last_trade_price', 'dayPct']
        toTxt = toTxt[sendCols].tail(len(watchList))
        toTxt.columns = ['Stock', 'Price', 'Percent']
        toTxt.set_index('Stock', inplace = True)

        # Send out an email with the last prices of watchlist stocks
        send_email(user = username,
                    pwd = base64.b64decode(password),
                    recipient = account,
                    #, (watched.iloc[:, 0].tail(len(watchList)))
                    body = toTxt
                    )

#TODO find the stock price from the previous day and compare to current prices           
#rtp[['StockSymbol', 'LastTradePrice']][rtp.index.day < now.day].tail(len(watchList))