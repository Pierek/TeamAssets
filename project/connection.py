import pyodbc

def datatofile(server, database, user, password, query):
    cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+user+';PWD='+password)
    cursor = cnxn.cursor()
    cursor.execute(query)
    return cursor.fetchall()