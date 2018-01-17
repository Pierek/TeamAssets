--- <summary>Move PriceClientDict data from enova to TeamExport</summary>
--- <event author="Piotr Purwin" date="2017-11-02" project="TEAM">View created</event>
CREATE VIEW [import].price_client_dict

AS

SELECT 
	 [price_client_id] = ID
	,[price_client_code] = 'PC_' + CONVERT(nvarchar(4), ID)
	,[price_client_description] = LTRIM(RTRIM(Nazwa))
	,[LastUpdate] = GETDATE()
FROM TEAM.dbo.DefinicjeCen