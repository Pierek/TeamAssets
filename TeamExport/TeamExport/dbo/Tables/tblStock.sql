CREATE TABLE dbo.tblStock
(
	 [product_id]     int NOT NULL
	,[client_id]      int NOT NULL
	,[stock_physical] int NULL
	,[stock_ordered]  int NULL
	,[stock_reserved] int NULL
	,[LastUpdate]     datetime NOT NULL
	,[LastUser]       varchar(100) NOT NULL
	--,CONSTRAINT PK_tblProduct PRIMARY KEY CLUSTERED([Id])
	--,CONSTRAINT NX1_tblProduct UNIQUE NONCLUSTERED([product_code])
);