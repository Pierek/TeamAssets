CREATE TABLE [data].stock
(
	 [product_id] int NOT NULL
	,[client_id]  int NULL
	,[quantity]   int NOT NULL
	,[stock_dict] nvarchar(40) NOT NULL
	,[LastUpdate] datetime NOT NULL
	,[LastUser]   varchar(100) NOT NULL
	,[DeletedOn]  datetime NULL
);