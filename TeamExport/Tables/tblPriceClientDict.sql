CREATE TABLE dbo.tblPriceClientDict
(
	 [price_client_id]   int NULL
	,[price_client_code] varchar(100) NOT NULL
	,[LastUpdate]        datetime NOT NULL
	,[LastUser]          varchar(100) NOT NULL
	--,CONSTRAINT PK_tblProduct PRIMARY KEY CLUSTERED([Id])
	--,CONSTRAINT NX1_tblProduct UNIQUE NONCLUSTERED([product_code])
);