CREATE TABLE [data].[currency]
(
	 [currency_id]          int NOT NULL
	,[currency_code]        varchar(10) NOT NULL
	,[currency_description] nvarchar(20) NOT NULL
	,[LastUpdate]           datetime NOT NULL
	,[DeletedOn]            datetime NULL
	,CONSTRAINT [PK_currency] PRIMARY KEY CLUSTERED([currency_id])
	,CONSTRAINT [NX1_currency] UNIQUE NONCLUSTERED([currency_code])
)