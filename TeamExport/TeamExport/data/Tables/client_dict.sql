CREATE TABLE [data].client_dict
(
	 [client_id]          int NOT NULL
	,[client_code]        varchar(30) NOT NULL
	,[client_description] nvarchar(200) NOT NULL
	,[LastUpdate]         datetime NOT NULL
	,[ResponseCode]       varchar(3) NULL
	,[ResponseDate]       datetime NULL
	,[DeletedOn]          datetime NULL
	,CONSTRAINT [PK_client_dict] PRIMARY KEY CLUSTERED([client_id])
	,CONSTRAINT [NX1_client_dict] UNIQUE NONCLUSTERED([client_code])
);