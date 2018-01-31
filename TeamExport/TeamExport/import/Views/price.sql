--- <summary>Move price data from enova to TeamExport</summary>
--- <event author="Piotr Purwin" date="2018-01-29" project="TEAM">View created</event>
CREATE VIEW [import].[price]

AS

SELECT
	 P.product_id
	,PCD.price_client_id
	,[netto_price] = CONVERT(decimal(10,2),C.NettoValue)
	--,[brutto_price] = CONVERT(decimal(10,2),C.BruttoValue)
	,[currency_code] = CASE WHEN C.NettoSymbol = 'LN' THEN 'PLN' ELSE C.NettoSymbol END -- to jest temporary raczej, powinni to poprawić
	,[LastUpdate] = GETDATE()
FROM TEAM.dbo.Ceny C
INNER JOIN data.product P
	ON P.product_id = C.Towar
INNER JOIN data.price_client_dict PCD
	ON PCD.price_client_id = C.Definicja