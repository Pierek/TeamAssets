﻿--- <summary>Move product data from TeamExport to TeamAssets</summary>
--- <event author="Piotr Purwin" date="2017-11-07" project="TEAM">View created</event>
CREATE VIEW export.product

AS

SELECT 
	 [product_code]
	,[product_description]
	,[promo]
	,[ean]
	,[integral_code]
	,[series]
	,[category]
	,[brand]
	,[range]
	,[product_description_en]
	,[category_en]
	,[box_capacity]
	,[dimension_h] = CONVERT(nvarchar(8),dimension_h)
	,[dimension_w] = CONVERT(nvarchar(8),dimension_w)
	,[dimension_l] = CONVERT(nvarchar(8),dimension_l)
	,[palette_capacity] = CONVERT(nvarchar(25),palette_capacity)
	,[box_dimension_h] = CONVERT(nvarchar(8),dimension_h)
	,[box_dimension_w] = CONVERT(nvarchar(8),dimension_w)
	,[box_dimension_l] = CONVERT(nvarchar(8),dimension_l)
	,[rep_state]
	,[rep_state_www]
	,[kgo] = CONVERT(nvarchar(10),kgo)
	,[price_zero] = CONVERT(nvarchar(9), price_zero)
	,[price_zero_mod] = CONVERT(nvarchar(10), price_zero_mod)
	,[tkg]
	,[full_cont_del]
	,[weight_net] = CONVERT(nvarchar(25), weight_net)
	,[weight_gross] = CONVERT(nvarchar(25), weight_gross)
	,[Action]
	,[ResponseCode]
	,[ResponseDate]
	,[DeletedOn]
FROM data.product
WHERE Action IS NOT NULL