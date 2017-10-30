CREATE TABLE dbo.tblProduct
(
	 [product_id]             int NOT NULL
	,[product_code]           varchar(100) NOT NULL
	,[product_description]    nvarchar(200) NOT NULL
	,[promo]                  nvarchar(20) NULL
	,[ean]                    varchar(14) NULL
	,[integral_code]          varchar(30) NULL
	,[series]                 varchar(30) NULL
	,[category]               nvarchar(50) NULL
	,[brand]                  varchar(20) NULL
	,[range]                  bit NULL
	,[product_description_en] varchar(100) NULL
	,[category_en]            varchar(70) NULL
	,[box_capacity]           smallint NULL
	,[dimension_h]            decimal(7,3) NULL
	,[dimension_w]            decimal(7,3) NULL
	,[dimension_l]            decimal(7,3) NULL
	,[pallete_capacity]       int NULL
	,[box_dimension_h]        decimal(7,3) NULL
	,[box_dimension_w]        decimal(7,3) NULL
	,[box_dimension_l]        decimal(7,3) NULL
	,[rep_state]              bit NULL
	,[rep_state_www]          bit NULL
	,[kgo]                    decimal(6,4) NULL
	,[LastUpdate]             datetime NOT NULL
	,[LastUser]               varchar(100) NOT NULL
	,CONSTRAINT PK_tblProduct PRIMARY KEY CLUSTERED([Id])
	,CONSTRAINT NX1_tblProduct UNIQUE NONCLUSTERED([product_code])
);