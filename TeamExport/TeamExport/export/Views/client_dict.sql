--- <summary>Move client_dict data from TeamExport to TeamAssets</summary>
--- <event author="Piotr Purwin" date="2017-11-07" project="TEAM">View created</event>
CREATE VIEW export.client_dict

AS

SELECT 
	 [client_code]
	,[client_description]
	,[Action]
	,[ResponseCode]
	,[ResponseDate]
	,[DeletedOn]
FROM data.client_dict
WHERE Action IS NOT NULL