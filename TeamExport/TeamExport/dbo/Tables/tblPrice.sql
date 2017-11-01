CREATE TABLE dbo.tblPrice
(
	 [product_id]      int NOT NULL
	,[price_client_id] int NOT NULL
	,[price_value]     int NOT NULL
	,[LastUpdate]      datetime NOT NULL
	,[LastUser]        varchar(100) NOT NULL
	--,CONSTRAINT PK_tblProduct PRIMARY KEY CLUSTERED([Id])
	--,CONSTRAINT NX1_tblProduct UNIQUE NONCLUSTERED([product_code])
);