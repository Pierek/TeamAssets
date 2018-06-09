# project/fullrefresh.py

from api.request import token_refresh
from entity.model import product, client_dict, price_client_dict, stock, price, job_log
import logging
import os
import datetime

LOG_LOCATION = os.getenv('APP_SETTINGS_LOG_LOCATION')

#logging.basicConfig(filename=os.getcwd() + '\\refresh_log\\fullrefresh' + datetime.datetime.today().strftime('%Y%m%d%H%M%S') + '.log', format='%(asctime)s %(message)s', level=logging.DEBUG)
logging.basicConfig(filename=LOG_LOCATION + 'fullrefresh' + datetime.datetime.today().strftime('%Y%m%d%H%M%S') + '.log', format='%(asctime)s %(message)s', level=logging.DEBUG)

# get new token here
token = token_refresh()

# run job_log request
job_log(token=token)


# run product data
product(token=token, action='delete')
product(token=token, action='put')
product(token=token, action='post')


## run client data
client_dict(token=token, action='delete')
client_dict(token=token, action='put')
client_dict(token=token, action='post')


## run price_client data
price_client_dict(token=token, action='delete')
price_client_dict(token=token, action='put')
price_client_dict(token=token, action='post')


# run stock data
stock(token=token, action='put')
stock(token=token, action='post')


# run price data
price(token=token, action='put')
price(token=token, action='post')

