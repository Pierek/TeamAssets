CREATE TABLE [data].price_client_dict
(
	 [price_client_id]          int NOT NULL
	,[price_client_code]        varchar(30) NOT NULL
	,[price_client_description] varchar(30) NOT NULL
	,[LastUpdate]               datetime NOT NULL
	,[ResponseCode]             varchar(3) NULL
	,[ResponseDate]             datetime NULL
	,[DeletedOn]                datetime NULL
	,CONSTRAINT [PK_price_client_dict] PRIMARY KEY CLUSTERED([price_client_id])
	,CONSTRAINT [NX1_price_client_dict] UNIQUE NONCLUSTERED([price_client_code])
);