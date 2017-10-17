USE TeamExport


IF OBJECT_ID('tempdb..#Prod') IS NOT NULL DROP TABLE #Prod
SELECT
	 T.[Id]
	,[product_code] = T.[Kod]
	,[product_description] = T.[Nazwa]
	,[promo] = FPROM.Data
	,[ean] = T.[EAN]
	,[integral_code] = FIntref.Data
	,[series] = FSerie.Data
	,[category] = FPOD.Data
	,[brand] = Fbrand.Data
	,[Pojemnosc_Opakowania] = FPojOp.Data
	,[dimension_h] = Fwys.Data
	,[dimension_w] = Fszer.Data
	,[dimension_l] = Fd³.Data
	,[Max_Na_Palecie] = FMAX.Data
	,[Karton_Wysokosc] = FKwys.Data
	,[Karton_Szerokosc] = FKszer.Data
	,[Karton_Dlugosc] = FKd³.Data
	,[description] = Fdesc.Data
	,[category_en] = FPODen.Data
	,[rap_state] = FRS.Data
	,[rap_state_www] = FRSWWW.Data
	,[kgo] = NULL
INTO #Prod
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
	AND FPROM.ParentType = N'Towary' AND FRS.Name = N'Promocja'


TRUNCATE TABLE dbo.tblProduct

INSERT INTO dbo.tblProduct
(
	 [Id]
	,[product_code]
	,[product_description]
	,[ean]
	,[integral_code]
	,[series]
	,[category]
	,[brand]
	,[Pojemnosc_Opakowania]
	,[dimension_h]
	,[dimension_w]
	,[dimension_l]
	,[Max_Na_Palecie]
	,[Karton_Wysokosc]
	,[Karton_Szerokosc]
	,[Karton_Dlugosc]
	,[description]
	,[category_en]
	,[rap_state]
	,[rap_state_www]
	,[kgo]
	,[LastUpdate]
	,[LastUser]
)
SELECT 
	 Id
	,[product_code] = LTRIM(RTRIM(product_code))
	,[product_description] = LTRIM(RTRIM(product_description))
	,[ean] =  CASE WHEN LTRIM(RTRIM(ean)) = '' THEN NULL ELSE LTRIM(RTRIM(ean)) END
	,[integral_code] = CASE WHEN LTRIM(RTRIM(integral_code)) = '' THEN NULL ELSE LTRIM(RTRIM(integral_code)) END
	,[series] = CASE WHEN LTRIM(RTRIM(series)) = '' THEN NULL ELSE LTRIM(RTRIM(series)) END
	,[category] = CASE WHEN LTRIM(RTRIM(category)) = '' THEN NULL ELSE LTRIM(RTRIM(category)) END
	,[brand] = LTRIM(RTRIM(brand))
	,[Pojemnosc_Opakowania] = CONVERT(smallint,LTRIM(RTRIM(Pojemnosc_Opakowania)))
	,[dimension_h] = /* CASE WHEN CONVERT(decimal(10,2),LTRIM(RTRIM(dimension_h))) < 1.00 THEN CONVERT(decimal(7,2),LTRIM(RTRIM(dimension_h))) * 100 ELSE */ CONVERT(decimal(7,3),LTRIM(RTRIM(REPLACE(dimension_h,',','.')))) --END
	,[dimension_w] = /* CASE WHEN CONVERT(decimal(10,2),LTRIM(RTRIM(dimension_w))) < 1.00 THEN CONVERT(decimal(7,2),LTRIM(RTRIM(dimension_w))) * 100 ELSE */ CONVERT(decimal(7,3),LTRIM(RTRIM(REPLACE(dimension_w,',','.')))) --END
	,[dimension_l] = /* CASE WHEN CONVERT(decimal(10,2),LTRIM(RTRIM(dimension_l))) < 1.00 THEN CONVERT(decimal(7,2),LTRIM(RTRIM(dimension_l))) * 100 ELSE */ CONVERT(decimal(7,3),LTRIM(RTRIM(REPLACE(dimension_l,',','.')))) --END
	,[Max_Na_Palecie] = CONVERT(int,LTRIM(RTRIM(Max_Na_Palecie)))
	,[Karton_Wysokosc] = CONVERT(decimal(7,3),LTRIM(RTRIM(REPLACE(Karton_Wysokosc,',','.'))))
	,[Karton_Szerokosc] = CONVERT(decimal(7,3),LTRIM(RTRIM(REPLACE(Karton_Szerokosc,',','.'))))
	,[Karton_Dlugosc] = CONVERT(decimal(7,3),LTRIM(RTRIM(REPLACE(Karton_Dlugosc,',','.'))))
	,[description] = CASE WHEN LTRIM(RTRIM(description)) = '' THEN NULL ELSE LTRIM(RTRIM(description)) END
	,[category_en] = CASE WHEN LTRIM(RTRIM(category_en)) = '' THEN NULL ELSE LTRIM(RTRIM(category_en)) END
	,[rap_state] = CONVERT(bit,LTRIM(RTRIM(rap_state)))
	,[rap_state_www] = CONVERT(bit,LTRIM(RTRIM(rap_state_www)))
	,[kgo]
	,[LastUpdate] = GETDATE()
	,[LastUser] = CURRENT_USER
INTO  #TEST
FROM #Prod


--SELECT * FROM #Prod WHERE [rap_state] <> LTRIM(RTRIM([rap_state]))
--SELECT * FROM #Prod WHERE [rap_state] IS NULL
--SELECT * FROM #Prod WHERE LTRIM(RTRIM([rap_state])) = ''





