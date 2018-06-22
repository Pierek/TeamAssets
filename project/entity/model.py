import service.qry as qry
from api.request import api_request
import logging

class Job:

    # retrieve all data from the table
    def __init__(self, token):
        self.log_row = qry.Cursor().queryresult(
                                            """ SELECT TOP 1
                                                     job_id
                                                    ,CONVERT(varchar(24),start_datetime,120)
                                                    ,CONVERT(varchar(24),finish_datetime,120)
                                                    ,status
                                                FROM log.job_log ORDER BY job_id DESC """)
        self.token = token

    
    def sync_error(self):
        """send sync process error"""      
     
        items = {}
        list_of_items = []
        each_item = {}

        # create json-like dictionary
        if self.log_row:  # check if list is not empty
            each_item['id'] = self.log_row[0][0]
            each_item['start_datetime'] = self.log_row[0][1]
            each_item['finish_datetime'] = self.log_row[0][2]
            each_item['status'] = 'Sync - Error'
            list_of_items.append(each_item.copy())

            # items is a final dictionary with a chunk data
            items['items'] = list_of_items

            # send request
            api_request(token=self.token, jsondata=items, action='post', api_entity='api/job/')


    def data_error(self):
        """send sql process error"""      
     
        items = {}
        list_of_items = []
        each_item = {}

        # create json-like dictionary
        if self.log_row:  # check if list is not empty
            each_item['id'] = self.log_row[0][0]
            each_item['start_datetime'] = self.log_row[0][1]
            each_item['finish_datetime'] = self.log_row[0][2]
            each_item['status'] = 'Data - Error'
            list_of_items.append(each_item.copy())

            # items is a final dictionary with a chunk data
            items['items'] = list_of_items

            # send request
            api_request(token=self.token, jsondata=items, action='post', api_entity='api/job/')



    def sync_success(self):
        """send sync process success"""      
     
        items = {}
        list_of_items = []
        each_item = {}

        # create json-like dictionary
        if self.log_row:  # check if list is not empty
            each_item['id'] = self.log_row[0][0]
            each_item['start_datetime'] = self.log_row[0][1]
            each_item['finish_datetime'] = self.log_row[0][2]
            each_item['status'] = 'Sync - Success'
            list_of_items.append(each_item.copy())

            # items is a final dictionary with a chunk data
            items['items'] = list_of_items

            # send request
            api_request(token=self.token, jsondata=items, action='post', api_entity='api/job/')



    def status(self):
        return str(self.log_row[0][3])


def product(token, action):
    """send product data request from database to the server"""

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
        for chunk in chunk_items:  # for each chunk (100 rows) send post/pu/delete request and update back the table
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
                    each_item['price_zero'] = row[22]
                    each_item['price_zero_mod_date'] = row[23]
                    each_item['tkg'] = row[24]
                    each_item['full_cont_del'] = row[25]
                    list_of_items.append(each_item.copy())

            elif action == 'delete':
                for row in chunk:
                    each_item['product_code'] = row[0]
                    list_of_items.append(each_item.copy())

            # items is a final dictionary with a chunk data
            items['items'] = list_of_items

            # reset list_of_items
            list_of_items = []

            # send request and receive response
            server_response = api_request(token=token, jsondata=items, action=action, api_entity='api/product/')

            # create a connection to db
            update_commit = qry.Cursor()

            if action in ('post', 'put'):
                for row in server_response:
                    update_item = """
                    UPDATE export.product
                    SET  ResponseCode = """+str(row['status'])+"""
                        ,ResponseDate = GETDATE()
                        ,Action = CASE WHEN """+str(row['status'])+""" = 200 THEN NULL ELSE Action END
                    WHERE product_code = '"""+row['product_code']+"'"

                    update_commit.querycommit(update_item)  # commit every transaction
            elif action == 'delete':
                for row in server_response:
                    update_item = """
                    UPDATE export.product
                    SET  ResponseCode = """+str(row['status'])+"""
                        ,ResponseDate = GETDATE()
                        ,Action = CASE WHEN """+str(row['status'])+""" = 200 THEN NULL ELSE Action END
                        ,DeletedOn = CASE WHEN """+str(row['status'])+""" = 200 THEN GETDATE() ELSE NULL END
                    WHERE product_code = '"""+row['product_code']+"'"

                    update_commit.querycommit(update_item)  # commit every transaction

    logging.info('Product finished - {0}, count - {1} rows'.format(action, str(len(all_items))))


def client_dict(token, action):
    """send client_dict data request from database to the server"""

    # retrieve all data from the table
    all_items = qry.Cursor().queryresult("SELECT * FROM export.client_dict WHERE Action = '" + action.upper() + "'")

    # divide all rows into 1000 row chunks (1000 for clients)
    chunk_items = [all_items[i:i+1000] for i in range(0, len(all_items), 1000)]

    # create empty objects
    items = {}
    list_of_items = []
    each_item = {}

    # create json-like dictionary
    if chunk_items:  # check if list is not empty
        for chunk in chunk_items:  # for each chunk (1000 rows) send post/pu/delete request and update back the table
            if action in ('post', 'put'):
                for row in chunk:
                    each_item['client_code'] = row[0]
                    each_item['client_description'] = row[1]
                    list_of_items.append(each_item.copy())

            elif action == 'delete':
                for row in chunk:
                    each_item['client_code'] = row[0]
                    list_of_items.append(each_item.copy())

            # items is a final dictionary with a chunk data
            items['items'] = list_of_items

            # reset list_of_items
            list_of_items = []

            # send request and receive response
            server_response = api_request(token=token, jsondata=items, action=action, api_entity='api/client/')

            # create a connection to db
            update_commit = qry.Cursor()

            if action in ('post', 'put'):
                for row in server_response:
                    update_item = """
                    UPDATE export.client_dict
                    SET  ResponseCode = """+str(row['status'])+"""
                        ,ResponseDate = GETDATE()
                        ,Action = CASE WHEN """+str(row['status'])+""" = 200 THEN NULL ELSE Action END
                    WHERE client_code = '"""+row['client_code'].replace("'", "''")+"'"

                    # print(update_item)
                    update_commit.querycommit(update_item)  # commit every transaction
            elif action == 'delete':
                for row in server_response:
                    update_item = """
                    UPDATE export.client_dict
                    SET  ResponseCode = """+str(row['status'])+"""
                        ,ResponseDate = GETDATE()
                        ,Action = CASE WHEN """+str(row['status'])+""" = 200 THEN NULL ELSE Action END
                        ,DeletedOn = CASE WHEN """+str(row['status'])+""" = 200 THEN GETDATE() ELSE NULL END
                    WHERE client_code = '"""+row['client_code'].replace("'", "''")+"'"

                    # print(update_item)
                    update_commit.querycommit(update_item)  # commit every transaction

    logging.info('Client-dict finished - {0}, count - {1} rows'.format(action, str(len(all_items))))


#### price_client_code and client_price_code are mismatched!!!!! has to set only one name (db is price_client, apiserver is client_price)
def price_client_dict(token, action):
    """send price_client_dict data request from database to the server"""

    # retrieve all data from the table
    all_items = qry.Cursor().queryresult("SELECT * FROM export.price_client_dict WHERE Action = '" + action.upper() + "'")

    # divide all rows into 1000 row chunks (1000 for price_clients)
    chunk_items = [all_items[i:i+1000] for i in range(0, len(all_items), 1000)]

    # create empty objects
    items = {}
    list_of_items = []
    each_item = {}

    # create json-like dictionary
    if chunk_items:  # check if list is not empty
        for chunk in chunk_items:  # for each chunk (1000 rows) send post/pu/delete request and update back the table
            if action in ('post', 'put'):
                for row in chunk:
                    each_item['client_price_code'] = row[0]
                    each_item['client_price_description'] = row[1]
                    list_of_items.append(each_item.copy())

            elif action == 'delete':
                for row in chunk:
                    each_item['client_price_code'] = row[0]
                    list_of_items.append(each_item.copy())

            # items is a final dictionary with a chunk data
            items['items'] = list_of_items

            # reset list_of_items
            list_of_items = []

            # send request and receive response
            server_response = api_request(token=token, jsondata=items, action=action, api_entity='api/client/price/')

            # create a connection to db
            update_commit = qry.Cursor()

            if action in ('post', 'put'):
                for row in server_response:
                    update_item = """
                    UPDATE export.price_client_dict
                    SET  ResponseCode = """+str(row['status'])+"""
                        ,ResponseDate = GETDATE()
                        ,Action = CASE WHEN """+str(row['status'])+""" = 200 THEN NULL ELSE Action END
                    WHERE price_client_code = '"""+row['client_price_code']+"'"

                    update_commit.querycommit(update_item)  # commit every transaction
            elif action == 'delete':
                for row in server_response:
                    update_item = """
                    UPDATE export.price_client_dict
                    SET  ResponseCode = """+str(row['status'])+"""
                        ,ResponseDate = GETDATE()
                        ,Action = CASE WHEN """+str(row['status'])+""" = 200 THEN NULL ELSE Action END
                        ,DeletedOn = CASE WHEN """+str(row['status'])+""" = 200 THEN GETDATE() ELSE NULL END
                    WHERE price_client_code = '"""+row['client_price_code']+"'"

                    update_commit.querycommit(update_item)  # commit every transaction

    logging.info('Price-client-dict finished - {0}, count - {1} rows'.format(action, str(len(all_items))))


def stock(token, action):
    """send stock data request from database to the server"""

    # retrieve all data from the table
    all_items = qry.Cursor().queryresult("SELECT * FROM export.stock WHERE Action = '" + action.upper() + "'")

    # divide all rows into 1000 row chunks (1000 for stock)
    chunk_items = [all_items[i:i+1000] for i in range(0, len(all_items), 1000)]

    # create empty objects
    items = {}
    list_of_items = []
    each_item = {}

    # create json-like dictionary
    if chunk_items:  # check if list is not empty
        for chunk in chunk_items:  # for each chunk (1000 rows) send post/pu/delete request and update back the table
            if action in ('post', 'put'):
                for row in chunk:
                    each_item['product_code'] = row[0]
                    each_item['client_code'] = row[1]
                    each_item['stock'] = row[2]
                    each_item['stock_type_code'] = row[3]
                    list_of_items.append(each_item.copy())

            ####elif action == 'delete':
            ####    for row in chunk:
            ####        each_item['product_code'] = row[0]
            ####        each_item['client_code'] = row[1]
            ####        each_item['stock_type_code'] = row[3]
            ####        list_of_items.append(each_item.copy())

            # items is a final dictionary with a chunk data
            items['items'] = list_of_items

            # reset list_of_items
            list_of_items = []

            # send request and receive response
            server_response = api_request(token=token, jsondata=items, action=action, api_entity='api/product/stock/')

            # create a connection to db
            update_commit = qry.Cursor()


            if action in ('post', 'put'):
                for row in server_response:
                    update_item = """
                    UPDATE export.stock
                    SET  ResponseCode = """+str(row['status'])+"""
                        ,ResponseDate = GETDATE()
                        ,Action = CASE WHEN """+str(row['status'])+""" = 200 THEN NULL ELSE Action END
                    WHERE product_code = '"""+row['product_code']+"'"+"""
                        AND ISNULL(client_code,'') = '"""+(row['client_code'] if row['client_code'] is not None else '')+"'"+"""
                        AND stock_type_code = '"""+row['stock_type_code']+"'"

                    update_commit.querycommit(update_item)  # commit every transaction

            ####elif action == 'delete':
            ####    for row in server_response:
            ####        update_item = """
            ####        UPDATE export.stock
            ####        SET  ResponseCode = """+str(row['status'])+"""
            ####            ,ResponseDate = GETDATE()
            ####            ,Action = CASE WHEN """+str(row['status'])+""" = 200 THEN NULL ELSE Action END
            ####            ,DeletedOn = CASE WHEN """+str(row['status'])+""" = 200 THEN GETDATE() ELSE NULL END 
            ####        WHERE product_code = '"""+row['product_code']+"'"+"""
            ####            AND ISNULL(client_code,'') = '"""+(row['client_code'] if row['client_code'] is not None else '')+"'"+"""
            ####            AND stock_type_code = '"""+row['stock_type_code']+"'"

            ####        update_commit.querycommit(update_item)  # commit every transaction

    logging.info('Stock finished - {0}, count - {1} rows'.format(action, str(len(all_items))))


def price(token, action):
    """send price data request from database to the server"""

    # retrieve all data from the table
    all_items = qry.Cursor().queryresult("SELECT * FROM export.price WHERE Action = '" + action.upper() + "'")

    # divide all rows into 5000 row chunks (5000 for price)
    chunk_items = [all_items[i:i+5000] for i in range(0, len(all_items), 5000)]

    # create empty objects
    items = {}
    list_of_items = []
    each_item = {}

    # create json-like dictionary
    if chunk_items:  # check if list is not empty
        for chunk in chunk_items:  # for each chunk (5000 rows) send post/put request and update back the table
            if action in ('post', 'put'):
                for row in chunk:
                    each_item['product_code'] = row[0]
                    each_item['client_price_code'] = row[1]
                    each_item['price'] = row[2]
                    each_item['currency_code'] = row[3]
                    list_of_items.append(each_item.copy())

            # items is a final dictionary with a chunk data
            items['items'] = list_of_items

            # reset list_of_items
            list_of_items = []

            # send request and receive response
            server_response = api_request(token=token, jsondata=items, action=action, api_entity='api/product/price/')

            # create a connection to db
            update_commit = qry.Cursor()


            if action in ('post', 'put'):
                for row in server_response:
                    update_item = """
                    UPDATE export.price
                    SET  ResponseCode = """+str(row['status'])+"""
                        ,ResponseDate = GETDATE()
                        ,Action = CASE WHEN """+str(row['status'])+""" = 200 THEN NULL ELSE Action END
                    WHERE product_code = '"""+row['product_code']+"'"+"""
                        AND price_client_code = '"""+row['client_price_code']+"'"

                    update_commit.querycommit(update_item)  # commit every transaction

    logging.info('Price finished - {0}, count - {1} rows'.format(action, str(len(all_items))))
