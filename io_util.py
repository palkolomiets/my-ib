#! /home/pavel/rtStockPrices/python3-env/bin/python

# TODO: Load from sqlite database
import base64
import netrc
import os
import smtplib

from Robinhood import Robinhood

def send_email(user, pwd, recipient, body):
    '''Sending an email or text message via gmail smtp
    Source:
    (https://stackoverflow.com/questions/10147455/how-to-send-an-email
    -with-gmail-as-provider-using-python)
    TODO: add args, returns
    '''
    recipients = recipient if type(recipient) is list else [recipient]

    # Format message
    message = """From: {0}\nTo: {1}\n\n{2}
              """.format(user, ", ".join(recipients), body)

    # Connect to gmail smtp server
    server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server_ssl.ehlo() # optional, called by login()
    server_ssl.login(user, pwd)  
    # ssl server doesn't support or need tls,
    # so don't call server_ssl.starttls() 
    server_ssl.sendmail(user, recipients, message)
    #server_ssl.quit()
    server_ssl.close()
    #print 'successfully sent message'
        

def robin_login():
    '''TODO: add docstring
    '''
    my_trader = Robinhood()
    qr = 'PQZJUCVO4CNVUWYP'
    username, _, password = get_creds('serverone-rh')

    my_trader.login(username=username,
                    password=base64.b64decode(password).decode('ascii'),
                    qr_code=qr)

    return my_trader

def get_creds(key):
    '''TODO: add docstring
    '''
    main_dir = os.path.dirname(os.path.abspath(__file__))
    user_dir = os.path.dirname(main_dir)
    creds = netrc.netrc(user_dir + '/.netrc')
    username, account, password = creds.authenticators(key)

    return username, account, password