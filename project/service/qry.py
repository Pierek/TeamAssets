import pyodbc
import os
import service.config
import logging

class Cursor:

    def __init__(self):
        app_settings = os.getenv('APP_SETTINGS', 'DevelopmentConfig')
        app_config = getattr(service.config, app_settings)
        try:
            cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=' + app_config.TEAM_SERVER +
                                  ';DATABASE=' + app_config.TEAM_DATABASE +
                                  ';UID=' + app_config.TEAM_USER +
                                  ';PWD=' + app_config.TEAM_PWD)
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

