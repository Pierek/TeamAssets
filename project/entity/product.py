import service.qry as qry
from service.config import DevelopmentConfig as DC
import requests
import json


def product(token, action):

    # retrieve all data from the table
    all_items = qry.Cursor().queryresult("SELECT * FROM export.product WHERE Action = '" + action.upper() + "'")

    # divide all rows into 100 row chunks
    chunk_items = [all_items[i:i+100] for i in range(0, len(all_items), 100)]

    # create empty objects
    items = {}
    list_of_items = []
    each_item = {}

    # create json-like dictionary
    if chunk_items:  # check if list is not empty
        for chunk in chunk_items:
            if action in ('post', 'put'):
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

            elif action == 'delete':
                for row in chunk:
                    each_item['product_code'] = row[0]
                    list_of_items.append(each_item.copy())

            items['items'] = list_of_items

            print(items)

            # send request
            headers = {"Token": token, "Content-Type": "application/json"}
            action_method = getattr(requests, action)
            response = action_method(DC.URL + '/api/products/', headers=headers, json=items)

            # print response from the server
            print(response.text)
            server_response = json.loads(response.text)

            # create a connection to db
            update_commit = qry.Cursor()

            for row in server_response:
                update_item = """
                UPDATE export.product
                SET  ResponseCode = """+str(row['status'])+"""
                    ,ResponseDate = GETDATE()
                    ,Action = CASE WHEN """+str(row['status'])+""" = 200 THEN NULL ELSE Action END
                WHERE product_code = '"""+row['product_code']+"'"

                print(update_item)
                update_commit.querycommit(update_item)

