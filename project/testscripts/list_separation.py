from project.service.config import DevelopmentConfig
from project.service.qry import queryresult
from project.api.model import Product

# query = [
#     {'product': 'a', 'action': 'POST'},
#     {'product': 'b', 'action': 'PUT'},
#     {'product': 'c', 'action': 'DEL'},
#     {'product': 'd', 'action': 'POST'},
#     {'product': 'e', 'action': 'PUT'},
#     {'product': 'f', 'action': 'DEL'}
#         ]


# print(query)
#
# for row in query:
#     print({'product': 'a'} in query)


query = "SELECT * FROM export.product"

team_server = DevelopmentConfig.TEAM_SERVER
team_database = DevelopmentConfig.TEAM_DATABASE
team_user = DevelopmentConfig.TEAM_USER
team_password = DevelopmentConfig.TEAM_PWD

a = queryresult(database=team_database, server=team_server, user=team_user, password=team_password, query=query)

print(a)

lista = []
for row in a:
    lista = Product(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19], row[20], row[21])
    lista.append()

lista[0].print_product

