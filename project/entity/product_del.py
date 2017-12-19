import pyodbc
import requests
import json
from service.config import DevelopmentConfig

# create connection to db and fetch all data from export
cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+DevelopmentConfig.TEAM_SERVER +
                      ';DATABASE='+DevelopmentConfig.TEAM_DATABASE +
                      ';UID='+DevelopmentConfig.TEAM_USER +
                      ';PWD='+DevelopmentConfig.TEAM_PWD)
cursor = cnxn.cursor()
cursor.execute("SELECT * FROM export.product WHERE Action = 'DEL'")
del_items = cursor.fetchall()

items = {}
list_of_items = []
each_item = {}

# create json-like dictionary
if del_items:  # check if list is not empty
    for row in del_items:
        each_item['product_code'] = row[0]
        list_of_items.append(each_item.copy())

    items['items'] = list_of_items

print(items)
print(json.dumps(items))

# get token
token_headers = {"Username": 'a@pi.com', "Password": 'api123'}
token_response = requests.post('http://127.0.0.1:5000/api/auth/', headers=token_headers)
token = json.loads(token_response.text)

print(token['token'])


# send del request
headers = {"Token": token['token'], "Content-Type": "application/json"}
response = requests.delete('http://127.0.0.1:5000/api/products/', headers=headers, json=items)

# print response from the server
print(response.text)
server_response = json.loads(response.text)

print(json.loads(response.text))


# update table in db
cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+DevelopmentConfig.TEAM_SERVER +
                      ';DATABASE='+DevelopmentConfig.TEAM_DATABASE +
                      ';UID='+DevelopmentConfig.TEAM_USER +
                      ';PWD='+DevelopmentConfig.TEAM_PWD)
cursor = cnxn.cursor()
for row in server_response:
    update_item = """
    UPDATE export.product
    SET  ResponseCode = """+str(row['status'])+"""
        ,ResponseDate = GETDATE()
        ,Action = CASE WHEN """+str(row['status'])+""" = 200 THEN NULL ELSE Action END
        ,DeletedOn = CASE WHEN """+str(row['status'])+""" = 200 THEN GETDATE() ELSE NULL END 
    WHERE product_code = '"""+row['product_code']+"'"

    print(update_item)
    cursor.execute(update_item)
    cursor.commit()
