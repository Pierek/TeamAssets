CREATE TABLE dbo.tblStock
(
	 [Id]             int NOT NULL
	,[product_code]   varchar(100) NOT NULL
	,[stock_physical] int NULL
	,[stock_ordered]  int NULL
	,[stock_reserved] int NULL
	,[LastUpdate]     datetime NOT NULL
	,[LastUser]       varchar(100) NOT NULL
	--,CONSTRAINT PK_tblProduct PRIMARY KEY CLUSTERED([Id])
	--,CONSTRAINT NX1_tblProduct UNIQUE NONCLUSTERED([product_code])
);