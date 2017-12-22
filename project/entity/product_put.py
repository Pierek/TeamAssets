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
cursor.execute("SELECT * FROM export.product WHERE Action = 'PUT'")
all_items = cursor.fetchall()
put_items = [all_items[i:i+100] for i in range(0,len(all_items),100)]

items = {}
list_of_items = []
each_item = {}

# create json-like dictionary
if put_items:  # check if list is not empty
    for chunk in put_items:
        for row in chunk:
            each_item['product_code'] = row[0]
            each_item['product_description'] = row[1]
            each_item['promo'] = row[2]
            each_item['ean'] = row[3]
            each_item['integral_code'] = row[4]
            each_item['series'] = row[5]
            each_item['category'] = row[6]
            each_item['brand'] = row[7]
            each_item['range'] = row[8]
            each_item['product_description_en'] = row[9]
            each_item['category_en'] = row[10]
            each_item['box_capacity'] = row[11]
            each_item['dimension_h'] = row[12]
            each_item['dimension_w'] = row[13]
            each_item['dimension_l'] = row[14]
            each_item['pallete_capacity'] = row[15]
            each_item['box_dimension_h'] = row[16]
            each_item['box_dimension_w'] = row[17]
            each_item['box_dimension_l'] = row[18]
            each_item['rep_state'] = row[19]
            each_item['rep_state_www'] = row[20]
            each_item['kgo'] = row[21]
            list_of_items.append(each_item.copy())

        items['items'] = list_of_items

        print(items)
        print(json.dumps(items))

        # get token
        token_headers = {"Username": 'a@pi.com', "Password": 'api123'}
        token_response = requests.post('http://127.0.0.1:5000/api/auth/', headers=token_headers)
        token = json.loads(token_response.text)

        print(token['token'])


        # send put request
        headers = {"Token": token['token'], "Content-Type": "application/json"}
        response = requests.put('http://127.0.0.1:5000/api/products/', headers=headers, json=items)

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
            WHERE product_code = '"""+row['product_code']+"'"

            print(update_item)
            cursor.execute(update_item)
            cursor.commit()
