CREATE TABLE [data].[product]
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
	,[kgo]                    float NULL
	,[LastUpdate]             datetime NOT NULL
	,[ResponseCode]           varchar(3) NULL
	,[ResponseDate]           datetime NULL
	,[DeletedOn]              datetime NULL
	,[Action]                 nvarchar(10) NULL
	,CONSTRAINT [PK_product] PRIMARY KEY CLUSTERED([product_id])
	,CONSTRAINT [NX1_product] UNIQUE NONCLUSTERED([product_code])
);