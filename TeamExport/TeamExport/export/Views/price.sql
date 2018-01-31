--- <summary>Move price data from TeamExport to TeamAssets</summary>
--- <event author="Piotr Purwin" date="2018-01-29" project="TEAM">View created</event>
CREATE VIEW export.price

AS

SELECT 
	 P.product_code
	,PCD.price_client_code
	,[netto_price] = CONVERT(varchar(10),S.netto_price)
	--,S.brutto_price
	,S.currency_code
	,S.Action
	,S.ResponseCode
	,S.ResponseDate
FROM data.price S
INNER JOIN data.product P
	ON P.product_id = S.product_id
LEFT JOIN data.price_client_dict PCD
	ON PCD.price_client_id = S.price_client_id
WHERE S.Action IS NOT NULL