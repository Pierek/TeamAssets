# project/api/model.py
from sqlalchemy import create_engine
from project.service.qry import Query
from project.api.request import ApiRequest
import requests
import json
#
# class Engine:
#     def __init__(self, user, password, server, database, query):
#         self.user = user
#         self.password = password
#         self.server = server
#         self.database = database
#         self.query = query
#
#     def return_query(self):
#         engine = create_engine("mssql+pyodbc://"+self.user+":"+self.password+"@"+self.server+"/"+self.database+"?driver=SQL+Server")
#         return engine.execute(self.query)
#
# class Product:
#
#     def __init__(self, product_code, product_description, promo, ean, integral_code, series, category, brand, range
#                  , product_description_en, category_en, box_capacity, dimension_h, dimension_w, dimension_l
#                  , pallete_capacity, box_dimension_h, box_dimension_w, box_dimension_l, rep_state, rep_state_www, kgo):
#
#         self.product_code = product_code
#         self.product_description = product_description
#         self.promo = promo
#         self.integral_code = integral_code
#         self.ean = ean
#         self.series = series
#         self.category = category
#         self.brand = brand
#         self.range = range
#         self.product_description_en = product_description_en
#         self.category_en = category_en
#         self.box_capacity = box_capacity
#         self.dimension_h = dimension_h
#         self.dimension_w = dimension_w
#         self.dimension_l = dimension_l
#         self.pallete_capacity = pallete_capacity
#         self.box_dimension_h = box_dimension_h
#         self.box_dimension_w = box_dimension_w
#         self.box_dimension_l = box_dimension_l
#         self.rep_state = rep_state
#         self.rep_state_www = rep_state_www
#         self.kgo = kgo
#
#     def print_product(self):
#         return self.product_description


class Product1:

    def post(self):
        post_items = Query("SELECT * FROM export.product WHERE Action = 'POST'").queryresult()
        items = {}
        list_of_items = []
        each_item = {}
        if post_items:  # check if list is not empty
            for row in post_items:
                each_item['product_code'] = row[0]
                each_item['product'] = row[1]
                each_item['ean'] = row[2]
                each_item['integral_code'] = row[3]
                each_item['series'] = row[4]
                each_item['category'] = row[5]
                each_item['brand'] = row[6]
                each_item['range'] = row[7]
                each_item['product_description_en'] = row[8]
                each_item['category_en'] = row[9]
                each_item['box_capacity'] = row[10]
                each_item['dimension_h'] = row[11]
                each_item['dimension_w'] = row[12]
                each_item['dimension_l'] = row[13]
                each_item['pallete_capacity'] = row[14]
                each_item['box_dimension_h'] = row[15]
                each_item['box_dimension_w'] = row[16]
                each_item['box_dimension_l'] = row[17]
                each_item['rep_state'] = row[18]
                each_item['rep_state_www'] = row[19]
                each_item['kgo'] = row[20]
                list_of_items.append(each_item.copy())

            items['items'] = list_of_items

            token = ApiRequest('a@pi.com', 'api123', 'http://54.187.225.165/api/').get_token()
            headers = {"Token": token, "Content-Type": "application/json"}
            response = requests.post('http://54.187.225.165/api/' + "products/", headers=headers, json=items)

            new_response = response.text


            for row in new_response:
                update_item = """
                UPDATE data.product
                SET  ResponseCode = CONVERT(int,"""+str(row['response'])+""")
                    ,ResponseDate = GETDATE()
                    ,Action = CASE WHEN """+str(row['response'])+""" = '200' THEN NULL ELSE Action END
                WHERE product_code = """+row['product_code']
                Query(update_item).querycommit()




        else:
            print('no items to post')

