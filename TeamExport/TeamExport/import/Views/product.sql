--- <summary>Move product data from enova to TeamExport</summary>
--- <event author="Piotr Purwin" date="2017-10-16" project="TEAM">View created</event>
CREATE VIEW import.product

AS

SELECT 
	 [product_id] = T.ID
	,[product_code] = LTRIM(RTRIM(T.Kod))
	,[product_description] = LTRIM(RTRIM(T.Nazwa))
	,[promo] = CASE WHEN LTRIM(RTRIM(FPROM.Data)) = '' THEN NULL ELSE LTRIM(RTRIM(FPROM.Data)) END
	,[ean] =  CASE WHEN LTRIM(RTRIM(ean)) = '' THEN NULL ELSE LTRIM(RTRIM(T.EAN)) END
	,[integral_code] = CASE WHEN LTRIM(RTRIM(FIntref.Data)) = '' THEN NULL ELSE LTRIM(RTRIM(FIntref.Data)) END
	,[series] = CASE WHEN LTRIM(RTRIM(FSerie.Data)) = '' THEN NULL ELSE LTRIM(RTRIM(FSerie.Data)) END 
	,[category] = CASE WHEN LTRIM(RTRIM(FPOD.Data)) = '' THEN NULL ELSE LTRIM(RTRIM(FPOD.Data)) END
	,[brand] = LTRIM(RTRIM(Fbrand.Data))
	,[range] = CONVERT(bit,LTRIM(RTRIM(Frange.Data)))
	,[product_description_en] = CASE WHEN LTRIM(RTRIM(Fdesc.Data)) = '' THEN NULL ELSE LTRIM(RTRIM(Fdesc.Data)) END
	,[category_en] = CASE WHEN LTRIM(RTRIM(FPODen.Data)) = '' THEN NULL ELSE LTRIM(RTRIM(FPODen.Data)) END
	,[box_capacity] = CONVERT(smallint,LTRIM(RTRIM(FPojOp.Data)))
	,[dimension_h] = CONVERT(decimal(7,3),LTRIM(RTRIM(REPLACE(Fwys.Data,',','.'))))
	,[dimension_w] = CONVERT(decimal(7,3),LTRIM(RTRIM(REPLACE(Fszer.Data,',','.'))))
	,[dimension_l] = CONVERT(decimal(7,3),LTRIM(RTRIM(REPLACE(Fdł.Data,',','.'))))
	,[pallete_capacity] = CONVERT(int,LTRIM(RTRIM(FMAX.Data)))
	,[box_dimension_h] = CONVERT(decimal(7,3),LTRIM(RTRIM(REPLACE(FKwys.Data,',','.'))))
	,[box_dimension_w] = CONVERT(decimal(7,3),LTRIM(RTRIM(REPLACE(FKszer.Data,',','.'))))
	,[box_dimension_l] = CONVERT(decimal(7,3),LTRIM(RTRIM(REPLACE(FKdł.Data,',','.'))))
	,[rep_state] = CONVERT(bit,LTRIM(RTRIM(FRS.Data)))
	,[rep_state_www] = CONVERT(bit,LTRIM(RTRIM(FRSWWW.Data)))
	,[kgo] = (CONVERT(float,LTRIM(RTRIM(FKGO.Data))) * 0.09) -- kgo wartosc jest wyliczana jako wartosc KGO WAGA * 0,09 zgadza sie dla wszystkich produktów
	,[LastUpdate] = GETDATE()
	,[LastUser] = CURRENT_USER
FROM TEAM.dbo.Towary T
LEFT JOIN TEAM.dbo.Features FSerie ON FSerie.Parent = T.ID
	AND FSerie.ParentType = N'Towary' AND FSerie.Name = N'Serie'
LEFT JOIN TEAM.dbo.Features FPOD ON FPOD.Parent = T.ID
	AND FPOD.ParentType = N'Towary' AND FPOD.Name = N'Podgrupa'
LEFT JOIN TEAM.dbo.Features FIntref ON FIntref.Parent = T.ID
	AND FIntref.ParentType = N'Towary' AND FIntref.Name = N'Integral ref'
LEFT JOIN TEAM.dbo.Features Fbrand ON Fbrand.Parent = T.ID
	AND Fbrand.ParentType = N'Towary' AND Fbrand.Name = N'brand'
LEFT JOIN TEAM.dbo.Features FMAX ON FMAX.Parent = T.ID
	AND FMAX.ParentType = N'Towary' AND FMAX.Name = N'max na palecie'
LEFT JOIN TEAM.dbo.Features FPojOp ON FPojOp.Parent = T.ID
	AND FPojOp.ParentType = N'Towary' AND FPojOp.Name = N'Pojemność opakowania'
LEFT JOIN TEAM.dbo.Features Fwys ON Fwys.Parent = T.ID
	AND Fwys.ParentType = N'Towary' AND Fwys.Name = N'wys'
LEFT JOIN TEAM.dbo.Features Fszer ON Fszer.Parent = T.ID
	AND Fszer.ParentType = N'Towary' AND Fszer.Name = N'szer'
LEFT JOIN TEAM.dbo.Features Fdł ON Fdł.Parent = T.ID
	AND Fdł.ParentType = N'Towary' AND Fdł.Name = N'dł'
LEFT JOIN TEAM.dbo.Features FKdł ON FKdł.Parent = T.ID
	AND FKdł.ParentType = N'Towary' AND FKdł.Name = N'karton dł'
LEFT JOIN TEAM.dbo.Features FKszer ON FKszer.Parent = T.ID
	AND FKszer.ParentType = N'Towary' AND FKszer.Name = N'karton szer'
LEFT JOIN TEAM.dbo.Features FKwys ON FKwys.Parent = T.ID
	AND FKwys.ParentType = N'Towary' AND FKwys.Name = N'karton wys'
LEFT JOIN TEAM.dbo.Features Fdesc ON Fdesc.Parent = T.ID
	AND Fdesc.ParentType = N'Towary' AND Fdesc.Name = N'description'
LEFT JOIN TEAM.dbo.Features FPODen ON FPODen.Parent = T.ID
	AND FPODen.ParentType = N'Towary' AND FPODen.Name = N'PodgrupaE'
LEFT JOIN TEAM.dbo.Features FRSWWW ON FRSWWW.Parent = T.ID
	AND FRSWWW.ParentType = N'Towary' AND FRSWWW.Name = N'rap stany www'
LEFT JOIN TEAM.dbo.Features FRS ON FRS.Parent = T.ID
	AND FRS.ParentType = N'Towary' AND FRS.Name = N'rap stany'
LEFT JOIN TEAM.dbo.Features FPROM ON FPROM.Parent = T.ID
	AND FPROM.ParentType = N'Towary' AND FPROM.Name = N'Promocja'
LEFT JOIN TEAM.dbo.Features Frange ON Frange.Parent = T.ID
	AND Frange.ParentType = N'Towary' AND Frange.Name = N'range'
LEFT JOIN TEAM.dbo.Features FKGO ON FKGO.Parent = T.ID
	AND FKGO.ParentType = N'Towary' AND FKGO.Name = N'KGO WAGA'