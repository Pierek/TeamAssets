# project/fullrefresh.py

from api.request import token_refresh
from entity.model import product, client_dict, price_client_dict, stock, price, Job
import logging
import os
import datetime

LOG_LOCATION = os.getenv('APP_SETTINGS_LOG_LOCATION')

#logging.basicConfig(filename=os.getcwd() + '\\refresh_log\\fullrefresh' + datetime.datetime.today().strftime('%Y%m%d%H%M%S') + '.log', format='%(asctime)s %(message)s', level=logging.DEBUG)
logging.basicConfig(filename=LOG_LOCATION + 'fullrefresh' + datetime.datetime.today().strftime('%Y%m%d%H%M%S') + '.log', format='%(asctime)s %(message)s', level=logging.DEBUG)

# get new token here
token = token_refresh()

#create job object
a = Job(token=token)


if a.status() == 'Success':
    try:
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

        #log that process is finished
        a.sync_success()

    except:
        a.sync_error()
        logging.warning('Unexpected error while sending jsons')

else:
    a.data_error()

