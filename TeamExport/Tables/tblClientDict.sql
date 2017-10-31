CREATE TABLE dbo.tblClientDict
(
	 [client_id]          int NOT NULL
	,[client_code]        varchar(100) NOT NULL
	,[client_description] varchar(100) NOT NULL
	,[LastUpdate]         datetime NOT NULL
	,[LastUser]           varchar(100) NOT NULL
	--,CONSTRAINT PK_tblProduct PRIMARY KEY CLUSTERED([Id])
	--,CONSTRAINT NX1_tblProduct UNIQUE NONCLUSTERED([product_code])
);