CREATE TABLE [data].[currency]
(
	 [currency_id]          int NOT NULL
	,[currency_code]        varchar(10) NOT NULL
	,[currency_description] nvarchar(20) NOT NULL
	,[LastUpdate]           datetime NOT NULL
	,[LastUser]             varchar(100) NOT NULL
	,CONSTRAINT [PK_currency] PRIMARY KEY CLUSTERED([currency_id])
	,CONSTRAINT [NX1_currency] UNIQUE NONCLUSTERED([currency_code])
)