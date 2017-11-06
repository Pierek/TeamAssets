--- <summary>Move ClientDict data from enova to TeamExport</summary>
--- <event author="Piotr Purwin" date="2017-11-02" project="TEAM">View created</event>
CREATE VIEW [import].client_dict

AS

SELECT 
	 [client_id] = ID
	,[client_code] = LTRIM(RTRIM(Kod))
	,[client_description] = LTRIM(RTRIM(Nazwa))
	,[LastUpdate] = GETDATE()
	,[LastUser] = CURRENT_USER
FROM TEAM.dbo.Kontrahenci