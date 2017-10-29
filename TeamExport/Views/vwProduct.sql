--- <summary>Move product data from enova to TeamExport</summary>
--- <event author="Piotr Purwin" date="2017-10-16" project="TEAM">View created</event>
CREATE VIEW dbo.vwProduct

AS

SELECT 
	 [Id] = T.ID
	,[product_code] = LTRIM(RTRIM(T.Kod)) /* COLLATE Latin1_General_100_BIN2 */
	,[product_description] = LTRIM(RTRIM(T.Nazwa)) /* COLLATE Latin1_General_100_BIN2 */
	,[promo] = CASE WHEN LTRIM(RTRIM(FPROM.Data)) = '' THEN NULL ELSE LTRIM(RTRIM(FPROM.Data)) END
	,[ean] =  CASE WHEN LTRIM(RTRIM(ean)) /* COLLATE Latin1_General_100_BIN2 */ = '' THEN NULL ELSE LTRIM(RTRIM(T.EAN)) /* COLLATE Latin1_General_100_BIN2 */ END
	,[integral_code] = CASE WHEN LTRIM(RTRIM(FIntref.Data)) /* COLLATE Latin1_General_100_BIN2 */ = '' THEN NULL ELSE LTRIM(RTRIM(FIntref.Data)) /* COLLATE Latin1_General_100_BIN2 */ END
	,[series] = CASE WHEN LTRIM(RTRIM(FSerie.Data)) /* COLLATE Latin1_General_100_BIN2 */ = '' THEN NULL ELSE LTRIM(RTRIM(FSerie.Data)) /* COLLATE Latin1_General_100_BIN2 */ END 
	,[category] = CASE WHEN LTRIM(RTRIM(FPOD.Data)) /* COLLATE Latin1_General_100_BIN2 */ = '' THEN NULL ELSE LTRIM(RTRIM(FPOD.Data)) /* COLLATE Latin1_General_100_BIN2 */ END
	,[brand] = LTRIM(RTRIM(Fbrand.Data)) /* COLLATE Latin1_General_100_BIN2 */
	,[range] = CONVERT(bit,LTRIM(RTRIM(Frange.Data))) /* COLLATE Latin1_General_100_BIN2 */
	,[product_description_en] = CASE WHEN LTRIM(RTRIM(Fdesc.Data)) /* COLLATE Latin1_General_100_BIN2 */ = '' THEN NULL ELSE LTRIM(RTRIM(Fdesc.Data)) /* COLLATE Latin1_General_100_BIN2 */ END
	,[category_en] = CASE WHEN LTRIM(RTRIM(FPODen.Data)) /* COLLATE Latin1_General_100_BIN2 */ = '' THEN NULL ELSE LTRIM(RTRIM(FPODen.Data)) /* COLLATE Latin1_General_100_BIN2 */ END
	,[box_capacity] = CONVERT(smallint,LTRIM(RTRIM(FPojOp.Data)))
	,[dimension_h] = CONVERT(decimal(7,3),LTRIM(RTRIM(REPLACE(Fwys.Data,',','.')))) --END
	,[dimension_w] = CONVERT(decimal(7,3),LTRIM(RTRIM(REPLACE(Fszer.Data,',','.')))) --END
	,[dimension_l] = CONVERT(decimal(7,3),LTRIM(RTRIM(REPLACE(Fd³.Data,',','.')))) --END
	,[pallete_capacity] = CONVERT(int,LTRIM(RTRIM(FMAX.Data)))
	,[box_dimension_h] = CONVERT(decimal(7,3),LTRIM(RTRIM(REPLACE(FKwys.Data,',','.'))))
	,[box_dimension_w] = CONVERT(decimal(7,3),LTRIM(RTRIM(REPLACE(FKszer.Data,',','.'))))
	,[box_dimension_l] = CONVERT(decimal(7,3),LTRIM(RTRIM(REPLACE(FKd³.Data,',','.'))))
	,[rep_state] = CONVERT(bit,LTRIM(RTRIM(FRS.Data)))
	,[rep_state_www] = CONVERT(bit,LTRIM(RTRIM(FRSWWW.Data)))
	,[kgo] = (CONVERT(decimal(7,3),LTRIM(RTRIM(FKGO.Data))) * 0.09) -- kgo wartosc jest wyliczana jako wartosc KGO WAGA * 0,09 zgadza sie dla wszystkich produktów
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
	AND FPojOp.ParentType = N'Towary' AND FPojOp.Name = N'Pojemnoœæ opakowania'
LEFT JOIN TEAM.dbo.Features Fwys ON Fwys.Parent = T.ID
	AND Fwys.ParentType = N'Towary' AND Fwys.Name = N'wys'
LEFT JOIN TEAM.dbo.Features Fszer ON Fszer.Parent = T.ID
	AND Fszer.ParentType = N'Towary' AND Fszer.Name = N'szer'
LEFT JOIN TEAM.dbo.Features Fd³ ON Fd³.Parent = T.ID
	AND Fd³.ParentType = N'Towary' AND Fd³.Name = N'd³'
LEFT JOIN TEAM.dbo.Features FKd³ ON FKd³.Parent = T.ID
	AND FKd³.ParentType = N'Towary' AND FKd³.Name = N'karton d³'
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