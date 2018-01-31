CREATE TABLE [data].price
(
	 [product_id]      int NOT NULL
	,[price_client_id] int NOT NULL
	,[netto_price]     decimal(10,2) NOT NULL
	--,[brutto_price]    decimal(10,2) NOT NULL
	,[currency_code]   varchar(4) NOT NULL
	,[LastUpdate]      datetime NOT NULL
	,[ResponseCode]    varchar(3) NULL
	,[ResponseDate]    datetime NULL
	,[DeletedOn]       datetime NULL
	,[Action]          varchar(10) NULL
	,CONSTRAINT [PK_price] PRIMARY KEY CLUSTERED(product_id, price_client_id) --pytanie czy może być dla tego samego klienta i produktu cena pln i eur
);