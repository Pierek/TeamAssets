﻿--- <summary>Move PriceClientDict data from enova to TeamExport</summary>
--- <event author="Piotr Purwin" date="2017-11-02" project="TEAM">View created</event>
CREATE VIEW [import].price_client_dict

AS

SELECT 
	 [price_client_id] = ID
	,[price_client_code] = LTRIM(RTRIM(Nazwa))
	,[LastUpdate] = GETDATE()
	,[LastUser] = CURRENT_USER
FROM TEAM.dbo.DefinicjeCen