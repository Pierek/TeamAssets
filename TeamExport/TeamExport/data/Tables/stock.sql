CREATE TABLE [data].stock
(
	 [product_id]      int NOT NULL
	,[client_id]       int NULL
	,[quantity]        int NOT NULL
	,[stock_type_code] nvarchar(4) NOT NULL
	,[LastUpdate]      datetime NOT NULL
	,[ResponseCode]    varchar(3) NULL
	,[ResponseDate]    datetime NULL
	,[DeletedOn]       datetime NULL
	,[Action]          varchar(10) NULL
);