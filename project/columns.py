import connection as con
import json

# declare variables for connection
team_server = 'PIEREK-PC'
team_database = 'TeamExport'
team_user = 'test'
team_password = 'test'

team_query = """
SELECT
	 C.name
FROM sys.all_columns C
INNER JOIN sys.objects O
	INNER JOIN sys.schemas S
		ON S.schema_id = O.schema_id
		AND S.name = 'export'
	ON O.object_id = C.object_id
	AND O.name = 'product'
WHERE C.name <> 'LastUpdate'
ORDER BY C.column_id
"""

# create variables for json file
products = {}
file = {}
pr = []
newpr = []

####################
# retrieve json file
####################
for row in con.queryresult(database=team_database, server=team_server, user=team_user, password=team_password, query=team_query):
    pr.append(row[0])


newquery = ("SELECT " + ",".join(pr) + " FROM export.product")

for row in con.queryresult(database=team_database, server=team_server, user=team_user, password=team_password, query=newquery):
    for number in range(len(pr)):
        products[pr[number]] = row[number]

    newpr.append(products.copy())

print(newpr[0])

file['items'] = newpr
print(file)
print((file['items'][0]))
with open('testfile.json', 'w') as outfile:
    json.dump(obj=file, fp=outfile, ensure_ascii=False, indent=4, sort_keys=True)


# print(newpr)
# print(file)