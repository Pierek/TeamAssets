--- <summary>Move currency data from enova to TeamExport</summary>
--- <event author="Piotr Purwin" date="2017-11-02" project="TEAM">View created</event>
CREATE VIEW [import].currency

AS

SELECT 
	 [currency_id] = ID
	,[currency_code] = LTRIM(RTRIM(Symbol))
	,[currency_description] = LTRIM(RTRIM(Nazwa))
	,[LastUpdate] = GETDATE()
FROM TEAM.dbo.Waluty