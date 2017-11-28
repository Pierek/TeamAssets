# project/request

import requests
import json

class ApiRequest():
    '''Class to handle token authentication'''
    token = ''

    def get_token(self):
        '''Return valid token'''
        headers = {"Username": self.username, "Password": self.pwd}
        response = requests.post(self.url+"auth/", headers=headers)
        json_data = json.loads(response.text)
        if json_data['token']:
            return json_data['token']
        else:
            raise ValueError('missing token')

    def __init__(self, username, pwd, url):
        '''Setup connection metadata in constructor'''
        self.username = username
        self.pwd = pwd
        self.url = url
        self.token = self.get_token()

    def put_product(self, jsondata):
        ''' Put product '''
        headers = {"Token": self.token, "Content-Type": "application/json"}
        response = requests.put(self.url+"products/", headers=headers, json=jsondata)
        return json.loads(response.text)


