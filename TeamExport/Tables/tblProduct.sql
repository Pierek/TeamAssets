USE TeamExport;

CREATE TABLE tblProduct
(
	 [Id]                   int NOT NULL
	,[product_code]         varchar(100) NOT NULL
	,[product_description]  nvarchar(200) NOT NULL
	,[ean]                  varchar(14) NULL
	,[integral_code]        varchar(30) NULL
	,[series]               varchar(30) NULL
	,[category]             nvarchar(50) NULL
	,[brand]                varchar(20) NULL
	,[Pojemnosc_Opakowania] smallint NULL
	,[dimension_h]          decimal(6,2) NULL
	,[dimension_w]          decimal(6,2) NULL
	,[dimension_l]          decimal(6,2) NULL
	,[Max_Na_Palecie]       int NULL
	,[Karton_Wysokosc]      smallint NULL
	,[Karton_Szerokosc]     smallint NULL
	,[Karton_Dlugosc]       smallint NULL
	,[description]          varchar(100) NULL
	,[category_en]          varchar(70) NULL
	,[rap_state]            bit NULL
	,[rap_state_www]        bit NULL
	,[kgo]                  varchar(100) NULL
	,[LastUpdate]           datetime NOT NULL
	,[LastUser]             varchar(100) NOT NULL
	,CONSTRAINT PK_tblProduct PRIMARY KEY CLUSTERED([Id])
	,CONSTRAINT NX1_tblProduct UNIQUE NONCLUSTERED([product_code])
);