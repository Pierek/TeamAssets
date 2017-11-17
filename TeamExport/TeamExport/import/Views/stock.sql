--- <summary>Move stock data from enova to TeamExport</summary>
--- <event author="Piotr Purwin" date="2017-11-02" project="TEAM">View created</event>
CREATE VIEW [import].stock

AS

SELECT
	 P.product_id
	,[client_id] = NULL
	,[quantity] = SUM(Z.IloscValue)
	,[stock_dict] = N'Stan magazynowy'
	,[LastUpdate] = GETDATE()
FROM TEAM.dbo.Zasoby Z
INNER JOIN data.product P
	ON P.product_id = Z.Towar
WHERE Z.Magazyn = 1 -- czy tylko 1?
	AND Z.Okres = 1 -- ??
	-- brak kierunku bo brane sa i 1 i -1
GROUP BY P.product_id

UNION ALL

SELECT
	 P.product_id
	,C.client_id
	,[quantity] = Z.IloscValue
	,[stock_dict] = N'Rezerwacja klienta'
	,[LastUpdate] = GETDATE()
FROM TEAM.dbo.Zasoby Z
INNER JOIN data.product P
	ON P.product_id = Z.Towar
INNER JOIN data.client_dict C
	ON C.client_id = Z.PartiaKontrahent
INNER JOIN TEAM.dbo.DokHandlowe D
	ON D.ID = Z.PartiaDokument
INNER JOIN TEAM.dbo.DefDokHandlowych DF
	ON DF.ID = D.Definicja
	AND DF.Nazwa = N'Rezerwacja odbiorcy'
WHERE Z.Magazyn = 1 -- czy tylko 1?
	AND Z.Okres = 1 -- ??
	AND Z.Kierunek = -1

UNION ALL

SELECT
	 P.product_id
	,C.client_id
	,[quantity] = Z.IloscValue
	,[stock_dict] = N'Zamówienie klienta'
	,[LastUpdate] = GETDATE()
FROM TEAM.dbo.Zasoby Z
INNER JOIN data.product P
	ON P.product_id = Z.Towar
INNER JOIN data.client_dict C
	ON C.client_id = Z.PartiaKontrahent
INNER JOIN TEAM.dbo.DokHandlowe D
	ON D.ID = Z.PartiaDokument
INNER JOIN TEAM.dbo.DefDokHandlowych DF
	ON DF.ID = D.Definicja
	AND DF.Nazwa = N'Zamówienie od odbiorcy'
WHERE Z.Magazyn = 1 -- czy tylko 1?
	AND Z.Okres = 1 -- ??
	AND Z.Kierunek = -1

UNION ALL

SELECT
	 P.product_id
	,[client_id] = NULL
	,[quantity] = SUM(Z.IloscValue)
	,[stock_dict] = N'Stan fizyczny'
	,[LastUpdate] = GETDATE()
FROM TEAM.dbo.Zasoby Z
INNER JOIN data.product P
	ON P.product_id = Z.Towar
WHERE Z.Magazyn = 1 -- czy tylko 1?
	AND Z.Okres = 1 -- ??
	AND Z.Kierunek = 1 -- stan fizyczny na 1
GROUP BY P.product_id
