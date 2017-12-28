# project/request

import requests
import json
from service.config import DevelopmentConfig as DC

# class ApiRequest():
#     '''Class to handle token authentication'''
#     token = ''
#
#     def get_token(self):
#         '''Return valid token'''
#         headers = {"Username": self.username, "Password": self.pwd}
#         response = requests.post(self.url+"auth/", headers=headers)
#         json_data = json.loads(response.text)
#         if json_data['token']:
#             return json_data['token']
#         else:
#             raise ValueError('missing token')
#
#     def __init__(self, username, pwd, url):
#         '''Setup connection metadata in constructor'''
#         self.username = username
#         self.pwd = pwd
#         self.url = url
#         self.token = self.get_token()
#
#     def put_product(self, jsondata):
#         ''' Put product '''
#         headers = {"Token": self.token, "Content-Type": "application/json"}
#         response = requests.put(self.url+"products/", headers=headers, json=jsondata)
#         return json.loads(response.text)
#


# this module refreshes and returns a token for the server authentication
def token_refresh():
    headers = {"Username": DC.API_USERNAME, "Password": DC.API_PWD}
    response = requests.post(DC.URL + "api/auth/", headers=headers)
    json_data = json.loads(response.text)
    if json_data['token']:
        return json_data['token']
    else:
        raise ValueError('missing token')


# this module after applying token, jsondata (which is json with products, clients data etc.),
# action (post, put, delete) and api_entity (api/products/ for example) returns a dictionary with
# the table key and a responsecode
def api_request(token, jsondata, action, api_entity):
    headers = {"Token": token, "Content-Type": "application/json"}
    action_method = getattr(requests, action)
    response = action_method(DC.URL + api_entity, headers=headers, json=jsondata)
    return json.loads(response.text)
