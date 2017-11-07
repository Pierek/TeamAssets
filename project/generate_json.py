import connection as rtt
import json

products = {}
pr = []
file = {}

for row in rtt.datatofile(database='test', server='.', user='test', password='test', query=
                          """
SELECT 
	 ENGP_ENGNRG_PART_R
	,FUNC_KEY
	,VEHTYPE_CODE
	,EVL_VEHICLE_LINE_C
	,PFTRC_COMBINATN_C
	,MFTRC_COMBINATIN_C
	,[EVA_PER_USAGE_Q] = CONVERT(nvarchar(10),EVA_PER_USAGE_Q)
	,EFFIOP_EFF_IN_C
	,N_USAGE_C
FROM dbo.TestTable"""):
    products['ENGP_ENGNRG_PART_R'] = row[0]
    products['FUNC_KEY'] = row[1]
    products['VEHTYPE_CODE'] = row[2]
    products['EVL_VEHICLE_LINE_C'] = row[3]
    products['PFTRC_COMBINATN_C'] = row[4]
    products['MFTRC_COMBINATIN_C'] = row[5]
    products['EVA_PER_USAGE_Q'] = row[6]
    products['EFFIOP_EFF_IN_C'] = row[7]
    products['N_USAGE_C'] = row[8]

    pr.append(products.copy())

file['items'] = pr
print(pr)
print(file)
with open('testfile.json', 'w') as outfile:
    json.dump(obj=file, fp=outfile, ensure_ascii=False, indent=4, sort_keys=True)