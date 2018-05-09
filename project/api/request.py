# project/request

import json
import requests
import os
import service.config
import logging


# this module refreshes and returns a token for the server authentication
def token_refresh():
    app_settings = os.getenv('APP_SETTINGS', 'DevelopmentConfig')
    app_config = getattr(service.config, app_settings)
    headers = {"Username": app_config.API_USERNAME, "Password": app_config.API_PWD}
    try:
        response = requests.post(app_config.URL + "api/auth/", headers=headers)
    except requests.exceptions.RequestException as e:
        logging.warning(e)
        raise

    json_data = json.loads(response.text)
    if json_data['token']:
        return json_data['token']
    else:
        raise ValueError('missing token')




# this module after applying token, jsondata (which is json with products, clients data etc.),
# action (post, put, delete) and api_entity (api/products/ for example) returns a dictionary with
# the table key and a responsecode
def api_request(token, jsondata, action, api_entity):
    app_settings = os.getenv('APP_SETTINGS', 'DevelopmentConfig')
    app_config = getattr(service.config, app_settings)
    headers = {"Token": token, "Content-Type": "application/json"}
    action_method = getattr(requests, action)
    try:
        response = action_method(app_config.URL + api_entity, headers=headers, json=jsondata)
    except requests.exceptions.RequestException as e:
        logging.warning(e)
        raise

    return json.loads(response.text)
