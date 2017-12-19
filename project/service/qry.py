import pyodbc
from project.service.config import DevelopmentConfig


class Query:

    def __init__(self, query):
        self.query = query

    def queryresult(self):
        cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+DevelopmentConfig.TEAM_SERVER +
                              ';DATABASE='+DevelopmentConfig.TEAM_DATABASE +
                              ';UID='+DevelopmentConfig.TEAM_USER +
                              ';PWD='+DevelopmentConfig.TEAM_PWD)
        cursor = cnxn.cursor()
        cursor.execute(self.query)
        return cursor.fetchall()

    def querycommit(self):
        cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+DevelopmentConfig.TEAM_SERVER +
                              ';DATABASE='+DevelopmentConfig.TEAM_DATABASE +
                              ';UID='+DevelopmentConfig.TEAM_USER +
                              ';PWD='+DevelopmentConfig.TEAM_PWD)
        cursor = cnxn.cursor()
        cursor.execute(self.query)
        cursor.commit()