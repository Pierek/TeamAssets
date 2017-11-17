--- <summary>Move client_dict data from TeamExport to json</summary>
--- <event author="Piotr Purwin" date="2017-11-07" project="TEAM">View created</event>
CREATE VIEW export.client_dict

AS

SELECT 
	 [client_id]
	,[client_code]
	,[client_description]
	,[LastUpdate]
	,[DeletedOn]
FROM data.client_dict