#! /usr/bin/python2.7

import pandas as pd
import requests
import bs4
import datetime as dt
import sqlite3

db_name = '/home/pavel/rtStockPrices/rtPrices.db'

#db_name = 'C:/Users/Pavel/Desktop/rtPrices.db'

def get_earning_data(num_days):
    '''Pulls all the companies that report earnings within a time window
    Original, unmodified source:
    https://stackoverflow.com/questions/28913442/scraping-yahoo-earning-calendar
    
    Args:
        num_days (int): Number of days from present to pull earnings

    Returns:
        Dataframe with the name, earningsDate, etc for stocks reporting soon

    '''

    quotes = []
    today = dt.datetime.today()
    date_list = [today + dt.timedelta(days=x) for x in range(0, num_days)]    
    for date in date_list:        
        date = date.strftime('%Y%m%d')
        url = "https://biz.yahoo.com/research/earncal/{}.html".format(date)
        html = requests.get(url).text
        soup = bs4.BeautifulSoup(html, "lxml") 
        for tr in soup.find_all("tr"):
            con = tr.contents
            if len(con) > 3 and len(con[1].contents) > 0:
                if con[1].contents[0].name == "a":
                    if con[1].contents[0]["href"].startswith("http://finance.yahoo.com/q?s="):
                        quotes.append({"name"  : con[0].text
                                        ,"symbol": con[1].contents[0].text
                                        #,"url"   : con[1].contents[0]["href"]
                                        ,"eps"   : con[2].text
                                        ,"earningsTime"  : con[3].text
                                        ,"earningsDate"  : date
                                       })
    return pd.DataFrame(quotes)

# Pull all earnings information for the next 16 days
df = get_earning_data(16)
df['earningsDate'] = pd.to_datetime(df['earningsDate'])
# Sort the future earnings by date
df.sort_values(by = 'earningsDate', inplace = True)
    
# Open database connection
con = sqlite3.connect(db_name)
# Insert the length of the watchlist back into the database
df.to_sql('earningsReports', con, index = False, if_exists = 'append')
# Close the database connection
con.close()