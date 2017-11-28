﻿CREATE TABLE [data].stock
(
	 [product_id]   int NOT NULL
	,[client_id]    int NULL
	,[quantity]     int NOT NULL
	,[stock_dict]   nvarchar(40) NOT NULL
	,[LastUpdate]   datetime NOT NULL
	,[ResponseCode] varchar(3) NULL
	,[ResponseDate] datetime NULL
	,[DeletedOn]    datetime NULL
);