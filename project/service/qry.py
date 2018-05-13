import pyodbc
import os
import service.config
import logging

class Cursor:

    def __init__(self):
        TEAM_SERVER = os.getenv('APP_SETTINGS_TEAM_SERVER')
        TEAM_DATABASE = os.getenv('APP_SETTINGS_TEAM_DATABASE')
        TEAM_USER = os.getenv('APP_SETTINGS_TEAM_USER')
        TEAM_PWD = os.getenv('APP_SETTINGS_TEAM_PWD')
        if not TEAM_SERVER:
            raise ValueError(logging.warning('You must have "APP_SETTINGS_TEAM_SERVER" variable'))
        if not TEAM_DATABASE:
            raise ValueError(logging.warning('You must have "APP_SETTINGS_TEAM_DATABASE" variable'))
        if not TEAM_USER:
            raise ValueError(logging.warning('You must have "APP_SETTINGS_TEAM_USER" variable'))
        if not TEAM_PWD:
            raise ValueError(logging.warning('You must have "APP_SETTINGS_TEAM_PWD" variable'))
        #app_settings = os.getenv('APP_SETTINGS', 'DevelopmentConfig')
        #app_config = getattr(service.config, app_settings)

        try:
            cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=' + TEAM_SERVER +
                                  ';DATABASE=' + TEAM_DATABASE +
                                  ';UID=' + TEAM_USER +
                                  ';PWD=' + TEAM_PWD)
            self.cursor = cnxn.cursor()
        except pyodbc.Error as e:
            logging.warning(e.args[1].encode('utf-8'))
            raise


    def queryresult(self, query):
        try:
            self.cursor.execute(query)
        except pyodbc.Error as e:
            logging.warning(e.args[1].encode('utf-8'))
            raise

        return self.cursor.fetchall()

    def querycommit(self, query):
        try:
            self.cursor.execute(query)
            self.cursor.commit()
        except pyodbc.Error as e:
            logging.warning(e.args[1].encode('utf-8'))
            raise

