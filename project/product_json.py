import connection as con
import json

# declare variables for connection
team_server = '.'
team_database = 'test'
team_user = 'test'
team_password = 'test'

# declare query
team_query = """
SELECT 
	 Id
	,product_code
	,product_description
	,promo
	,ean
	,integral_code
	,series
	,category
	,brand
	,range
	,product_description_en
	,category_en
	,box_capacity
	,dimension_h
	,dimension_w
	,dimension_l
	,pallete_capacity
	,box_dimension_h
	,box_dimension_w
	,box_dimension_l
	,rep_state
	,rep_state_www
	,kgo
FROM export.product
"""

# create variables for json file
products = {}
file = {}
pr = []

####################
# retrieve json file
####################
for row in con.datatofile(database=team_database, server=team_server, user=team_user, password=team_password, query=team_query):
    products['product_code'] = row[1]
    products['product_description'] = row[2]
    products['promo'] = row[3]
    products['ean'] = row[4]
    products['integral_code'] = row[5]
    products['series'] = row[6]
    products['category'] = row[7]
    products['brand'] = row[8]
    products['range'] = row[9]
    products['product_description_en'] = row[10]
    products['category_en'] = row[11]
    products['box_capacity'] = row[12]
    products['dimension_h'] = row[13]
    products['dimension_w'] = row[14]
    products['dimension_l'] = row[15]
    products['pallete_capacity'] = row[16]
    products['box_dimension_h'] = row[17]
    products['box_dimension_w'] = row[18]
    products['box_dimension_l'] = row[19]
    products['rep_state'] = row[20]
    products['rep_state_www'] = row[21]
    products['kgo'] = row[22]

    pr.append(products.copy())

file['items'] = pr

jfile = json.dumps(obj=file, ensure_ascii=False)

print(jfile)
