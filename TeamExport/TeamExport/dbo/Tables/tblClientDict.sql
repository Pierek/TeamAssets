CREATE TABLE dbo.tblClientDict
(
	 [client_id]          int NOT NULL
	,[client_code]        varchar(30) NOT NULL
	,[client_description] nvarchar(200) NOT NULL
	,[LastUpdate]         datetime NOT NULL
	,[LastUser]           varchar(100) NOT NULL
	,CONSTRAINT [PK_tblClientDict] PRIMARY KEY CLUSTERED([client_id])
	,CONSTRAINT [NX1_tblClientDict] UNIQUE NONCLUSTERED([client_code])
);