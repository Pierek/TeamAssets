CREATE TABLE dbo.tblPriceClientDict
(
	 [price_client_id]   int NOT NULL
	,[price_client_code] varchar(30) NOT NULL
	,[LastUpdate]        datetime NOT NULL
	,[LastUser]          varchar(100) NOT NULL
	,CONSTRAINT [PK_tblPriceClientDict] PRIMARY KEY CLUSTERED([price_client_id])
	,CONSTRAINT [NX1_tblPriceClientDict] UNIQUE NONCLUSTERED([price_client_code])
);