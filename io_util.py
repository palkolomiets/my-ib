#! /home/pavel/rtStockPrices/python3-env/bin/python

# Load from sqlite database
import logging
import smtplib

def send_email(user, pwd, recipient, body):
    '''Sending an email or text message via gmail smtp
    Source:
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