import qry
import json
import requests
import pyodbc


team_server = 'PIEREK-PC'
team_database = 'TeamExport'
team_user = 'test'
team_password = 'test'
tablename = 'export.product'

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

# create variables for json file
products = {}
file = {}
pr = []
newpr = []

####################
# retrieve json file
####################
for row in qry.queryresult(database=team_database, server=team_server, user=team_user, password=team_password, query=columns):
    pr.append(row[0])

newquery = ("SELECT " + ",".join(pr) + " FROM " + tablename)

for row in qry.queryresult(database=team_database, server=team_server, user=team_user, password=team_password, query=newquery):
    for number in range(len(pr)):
        products[pr[number]] = row[number]
    newpr.append(products.copy())

file['items'] = newpr

jsondata = json.dumps(obj=file, ensure_ascii=False, indent=4, sort_keys=True)
print(jsondata)
# print(newpr)



headers = {"Token": "eyJhbGciOiJIUzI1NiIsImlhdCI6MTUxMTQ2ODM2OCwiZXhwIjoxNTExNDcxOTY4fQ.eyJjb25maXJtIjoyfQ.5D7dBFgbw0wzcfC8dAIoZoA-Egtn3zZG2JTj7sIHLYo"
    ,"Content-Type": "application/json"}

response = requests.put("http://54.187.225.165:8080/api/products/", headers=headers, json=jsondata)
print(response.status_code)

print(response.content)

# returnjson = json.dumps(obj=newpr, ensure_ascii=False, indent=4, sort_keys=True)
#
# # print(returnjson)
#
#
# listjson = json.loads(returnjson)
# # print(listjson[0])
#
# data ={"product_code":"2-OC13/01 WORKI", 'kgo':300}
#
#
# print(data)
# server = 'PIEREK-PC'
# database = 'TeamExport'
# user = 'test'
# password = 'test'
#
#
# cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + user + ';PWD=' + password)
# cursor = cnxn.cursor()
#
# cursor.execute("""
# UPDATE export.product
#     SET kgo = (?)
# WHERE product_code = (?)
# """, data['kgo'], data['product_code'])
# # cursor.commit()

