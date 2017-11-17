import qry
import json
import requests


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


headers = {
     "Token": "eyJleHAiOjE1MTA5NTkwNTMsImFsZyI6IkhTMjU2IiwiaWF0IjoxNTEwOTU1NDUzfQ.eyJjb25maXJtIjoyfQ.ehohBbaPcwofarFNRC95nbhjor8aatTt0taHoeCF5Hs"
    ,"Content-Type": "application/json"
            }

response = requests.post("http://54.187.225.165:8080/api/products/", headers=headers, json=jsondata)
print(response)