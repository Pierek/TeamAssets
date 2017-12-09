from service.config import DevelopmentConfig
from service import qry

query = [
    {'product': 'a', 'action': 'POST'},
    {'product': 'b', 'action': 'PUT'},
    {'product': 'c', 'action': 'DEL'},
    {'product': 'd', 'action': 'POST'},
    {'product': 'e', 'action': 'PUT'},
    {'product': 'f', 'action': 'DEL'}
        ]


# print(query)
#
# for row in query:
#     print({'product': 'a'} in query)


query = "SELECT * FROM export.product"

team_server = DevelopmentConfig.TEAM_SERVER
team_database = DevelopmentConfig.TEAM_DATABASE
team_user = DevelopmentConfig.TEAM_USER
team_password = DevelopmentConfig.TEAM_PWD

a = qry.queryresult(database=team_database, server=team_server, user=team_user, password=team_password, query=query)



print(a)