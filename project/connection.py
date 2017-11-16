import pyodbc
import json

def queryresult(server, database, user, password, query):
    cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+user+';PWD='+password)
    cursor = cnxn.cursor()
    cursor.execute(query)
    return cursor.fetchall()



def jsonresult(tablename, server, database, user, password):
    columns = """
    SELECT C.name
    FROM sys.all_columns C
    INNER JOIN sys.objects O
        ON O.object_id = C.object_id
    INNER JOIN sys.schemas S
        ON S.schema_id = O.schema_id
    WHERE S.name + '.' + O.name = '""" + tablename + """'
        AND C.name <> 'LastUpdate'
    ORDER BY c.column_id
    """

    products = {}
    file = {}
    pr = []
    newpr = []
    print(server)
    print(database)
    print(password)
    print(user)

    for row in queryresult(database=server, server=database, user=user, password=password, query=columns):
        pr.append(row[0])

    newquery = ("SELECT " + ",".join(pr) + " FROM " + tablename)

    for row in queryresult(database=server, server=database, user=user, password=password, query=newquery):
        for number in range(len(pr)):
            products[pr[number]] = row[number]
        newpr.append(products.copy())

    file['items'] = newpr

    return file

# jsonresult(tablename= 'export.product', server='PIEREK-PC', database='TeamExport', user='test', password='test')