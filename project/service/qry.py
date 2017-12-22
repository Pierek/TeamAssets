import pyodbc
from service.config import DevelopmentConfig


class Cursor:

    def __init__(self):
        cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=' + DevelopmentConfig.TEAM_SERVER +
                              ';DATABASE=' + DevelopmentConfig.TEAM_DATABASE +
                              ';UID=' + DevelopmentConfig.TEAM_USER +
                              ';PWD=' + DevelopmentConfig.TEAM_PWD)
        self.cursor = cnxn.cursor()

    def queryresult(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def querycommit(self, query):
        self.cursor.execute(query)
        self.cursor.commit()
