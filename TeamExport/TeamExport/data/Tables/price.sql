CREATE TABLE [data].price
(
	 [product_id]      int NOT NULL
	,[price_client_id] int NOT NULL
	,[price_value]     int NOT NULL
	,[price_currency]  varchar(10) NOT NULL
	,[LastUpdate]      datetime NOT NULL
	,[LastUser]        varchar(100) NOT NULL
	,CONSTRAINT [PK_price] PRIMARY KEY CLUSTERED(product_id, price_client_id, price_value)
);