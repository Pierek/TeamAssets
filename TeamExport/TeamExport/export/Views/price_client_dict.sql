--- <summary>Move price_client_dict data from TeamExport to TeamAssets</summary>
--- <event author="Piotr Purwin" date="2017-12-07" project="TEAM">View created</event>
CREATE VIEW export.price_client_dict

AS

SELECT 
	 [price_client_code]
	,[price_client_description]
	,[Action]
	,[ResponseCode]
	,[ResponseDate]
	,[DeletedOn]
FROM data.price_client_dict
WHERE Action IS NOT NULL