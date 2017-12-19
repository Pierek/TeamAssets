# from sqlalchemy import create_engine
#
#
# engine = create_engine("mssql+pyodbc://test:test@PIEREK-PC/TeamExport?driver=SQL+Server")
#
#
# result = engine.execute("SELECT * FROM export.product")
#
#
# a = result.fetchall()
#
# print(a)

# from project.api.model import Engine
# from project.service.qry import queryresult

# result = Engine('test', 'test', 'PIEREK-PC', 'TeamExport', 'SELECT * FROM export.product').return_query()
#
# print(result.fetchall())

# result = queryresult('SELECT * FROM export.product')
#
# print(result)

# print("SELECT * FROM export.product WHERE Action = 'POST'")
#
# from project.api.request import ApiRequest
#
# a = ApiRequest('a@pi.com', 'api123', 'http://54.187.225.165:8080/api/').get_token()
#
# print(a)

# from project.service.qry import Query
#
# a = "UPDATE data.product SET ResponseCode = 300 WHERE product_code = 'Z3 ZESTAW test'"
# print(a)
#
# Query(a).querycommit()

# b = "SELECT * FROM data.product WHERE product_code = 'Z3 ZESTAW test'"
# print(b)
#
# print(Query(b).queryresult())

# import pyodbc
# from project.service.config import DevelopmentConfig
#
#
# cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=' + DevelopmentConfig.TEAM_SERVER +
#                       ';DATABASE=' + DevelopmentConfig.TEAM_DATABASE +
#                       ';UID=' + DevelopmentConfig.TEAM_USER +
#                       ';PWD=' + DevelopmentConfig.TEAM_PWD)
# cursor = cnxn.cursor()
# cursor.execute("UPDATE data.product SET ResponseCode = 203 WHERE product_code = 'Z3 ZESTAW test'")
# cursor.commit()


print("Hello")