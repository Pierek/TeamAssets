CREATE TABLE [data].price
(
	 [product_id]      int NOT NULL
	,[price_client_id] int NOT NULL
	,[price_value]     int NOT NULL
	,[LastUpdate]      datetime NOT NULL
	,[LastUser]        varchar(100) NOT NULL
);