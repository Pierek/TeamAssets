﻿--- <summary>Move stock data from TeamExport to TeamAssets</summary>
--- <event author="Piotr Purwin" date="2017-11-07" project="TEAM">View created</event>
CREATE VIEW export.stock

AS

SELECT 
	 P.product_code
	,CD.client_code
	,S.quantity
	,S.stock_type_code
	,S.Action
	,S.ResponseCode
	,S.ResponseDate
FROM data.stock S
INNER JOIN data.product P
	ON P.product_id = S.product_id
LEFT JOIN data.client_dict CD
	ON CD.client_id = S.client_id
WHERE S.Action IS NOT NULL