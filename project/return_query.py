import json

from service.config import DevelopmentConfig
from api.request import ApiRequest
from service import qry

team_server = DevelopmentConfig.TEAM_SERVER
team_database = DevelopmentConfig.TEAM_DATABASE
team_user = DevelopmentConfig.TEAM_USER
team_password = DevelopmentConfig.TEAM_PWD
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
data = {}
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

print(newpr)
data['items'] = newpr

jsondata = json.dumps(obj=data, ensure_ascii=False, indent=4, sort_keys=True)
print(jsondata)
print(data)
# print(newpr)
# data = {'items':[{'product_code': 'WK22-SCHOTT'}]}

# call API Server #
api_username = DevelopmentConfig.API_USERNAME
api_pwd = DevelopmentConfig.API_PWD
api_url = DevelopmentConfig.API_URL

api = ApiRequest(api_username, api_pwd, api_url)
response_jsondata = api.put_product(data)
print(response_jsondata)

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

