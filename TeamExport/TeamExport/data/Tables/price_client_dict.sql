CREATE TABLE [data].price_client_dict
(
	 [price_client_id]   int NOT NULL
	,[price_client_code] varchar(30) NOT NULL
	,[LastUpdate]        datetime NOT NULL
	,[LastUser]          varchar(100) NOT NULL
	,CONSTRAINT [PK_price_client_dict] PRIMARY KEY CLUSTERED([price_client_id])
	,CONSTRAINT [NX1_price_client_dict] UNIQUE NONCLUSTERED([price_client_code])
);