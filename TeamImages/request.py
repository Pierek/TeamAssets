# project/request

import json
import requests
import os
#import service.config
import logging


# this module refreshes and returns a token for the server authentication
def token_refresh():
    API_USERNAME = os.getenv('APP_SETTINGS_API_USERNAME')
    API_PWD = os.getenv('APP_SETTINGS_API_PWD')
    URL = os.getenv('APP_SETTINGS_URL')
    if not API_USERNAME:
        raise ValueError(logging.warning('You must have "APP_SETTINGS_API_USERNAME" variable'))
    if not API_PWD:
        raise ValueError(logging.warning('You must have "APP_SETTINGS_API_PWD" variable'))
    if not URL:
        raise ValueError(logging.warning('You must have "APP_SETTINGS_URL" variable'))

    #app_settings = os.getenv('APP_SETTINGS', 'DevelopmentConfig')
    #app_config = getattr(service.config, app_settings)
    headers = {"Username": API_USERNAME, "Password": API_PWD}
    try:
        response = requests.post(URL + "api/auth/", headers=headers)
    except requests.exceptions.RequestException as e:
        logging.warning(e)
        raise

    json_data = json.loads(response.text)
    if json_data['token']:
        logging.info('Token refreshed')
        return json_data['token']
    else:
        raise ValueError('missing token')






# this module after applying token, jsondata (which is json with products, clients data etc.),
# action (post, put, delete) and api_entity (api/products/ for example) returns a dictionary with
# the table key and a responsecode
def api_request(token, jsondata, action, api_entity):
    URL = os.getenv('APP_SETTINGS_URL')
    if not URL:
        raise ValueError(logging.warning('You must have "URL" variable'))
    #app_settings = os.getenv('APP_SETTINGS', 'DevelopmentConfig')
    #app_config = getattr(service.config, app_settings)
    headers = {"Token": token, "Content-Type": "application/json"}
    action_method = getattr(requests, action)
    try:
        response = action_method(URL + api_entity, headers=headers, json=jsondata)
    except requests.exceptions.RequestException as e:
        logging.warning(e)
        raise

    return json.loads(response.text)
