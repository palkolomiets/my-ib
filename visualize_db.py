#! /home/pavel/rtStockPrices/python3-env/bin/python

import sqlite3
import pandas as pd
import os
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
plt.switch_backend('agg')

mainDir = os.path.dirname(os.path.abspath(__file__))
dbName = mainDir + '/rtPrices.db'

# Open database connection
con = sqlite3.connect(dbName)

## Load the existing stock prices file
old_prices = pd.read_sql('select * from robinhood where symbol = "SDS"', con)
con.close()

old_prices['updated_at'] = pd.to_datetime(old_prices['updated_at'])
old_prices['last_trade_price'] = pd.to_numeric(old_prices['last_trade_price'])

# Set the last trade time as the index
old_prices.set_index('updated_at', inplace = True)


def raw_plot(df, var_name, vis_dir='visualizations'):
    '''Save raw time series plots of modeled and non-modeled queues

    Args:
        df (pandas dataframe): Dataframe that houses the timeseries to plot
        var_name (str): Name of the column to plot
        modeled (bool): If True plot stored in modeled folder

    Returns:
        None

    '''
    plt.figure(figsize=(9,7))
    df[var_name].plot()
    plt.title(var_name)

    if not os.path.exists(vis_dir):
        os.makedirs(vis_dir)

    os.chdir(vis_dir)
    plt.savefig('raw_series.png', 
                bbox_inches='tight')
    plt.close()

os.chdir(mainDir)

raw_plot(old_prices, 'last_trade_price')