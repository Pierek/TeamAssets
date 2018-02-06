import pyodbc
import os
import service.config

class Cursor:

    def __init__(self):
        app_settings = os.getenv('APP_SETTINGS', 'DevelopmentConfig')
        app_config = getattr(service.config, app_settings)
        cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=' + app_config.TEAM_SERVER +
                              ';DATABASE=' + app_config.TEAM_DATABASE +
                              ';UID=' + app_config.TEAM_USER +
                              ';PWD=' + app_config.TEAM_PWD)
        self.cursor = cnxn.cursor()

    def queryresult(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def querycommit(self, query):
        self.cursor.execute(query)
        self.cursor.commit()
