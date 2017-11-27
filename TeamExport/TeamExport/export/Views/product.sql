--- <summary>Move product data from TeamExport to json</summary>
--- <event author="Piotr Purwin" date="2017-11-07" project="TEAM">View created</event>
CREATE VIEW export.product

AS

SELECT 
	-- [product_id]
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
	,[pallete_capacity]
	,[box_dimension_h] = CONVERT(nvarchar(8),dimension_h)
	,[box_dimension_w] = CONVERT(nvarchar(8),dimension_w)
	,[box_dimension_l] = CONVERT(nvarchar(8),dimension_l)
	,[rep_state]
	,[rep_state_www]
	,[kgo] = CONVERT(nvarchar(10),kgo)
	--,[LastUpdate]
	--,[DeletedOn]
FROM data.product
WHERE DeletedOn IS NULL