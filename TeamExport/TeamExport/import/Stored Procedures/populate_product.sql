﻿--- <summary>Move Product data from enova to TeamExport</summary>
--- <event author="Piotr Purwin" date="2017-10-16" project="TEAM">Procedure created</event>
CREATE PROCEDURE [import].populate_product

AS

BEGIN

	SET	XACT_ABORT, NOCOUNT ON

	/* declare constants */
	DECLARE  @DEBUG bit
			,@PROCEDURE_NAME sysname
			,@SCHEMA_NAME sysname

	/* declare variables */
	DECLARE	 @EventMessage nvarchar(MAX)
			,@EventParams nvarchar(MAX)
			,@EventRowcount int

	BEGIN TRY
		/* initialise constants */
		SET	@PROCEDURE_NAME = ISNULL(OBJECT_NAME(@@PROCID),'Debug')
		SET @SCHEMA_NAME = ISNULL(OBJECT_SCHEMA_NAME(@@PROCID),'Debug')


		/* log start */
		EXEC dbo.EventHandler
			 @ProcedureName = @PROCEDURE_NAME,@SchemaName = @SCHEMA_NAME
			,@EventMessage = 'Started'

		/* merge data */

		MERGE [data].product T
		USING [import].product S
		ON (T.product_code = S.product_code) 
		WHEN MATCHED AND ( 

				 T.product_id <> S.product_id OR (T.product_id IS NULL AND S.product_id IS NOT NULL) OR (T.product_id IS NOT NULL AND S.product_id IS NULL)
		OR		 T.product_description <> S.product_description OR (T.product_description IS NULL AND S.product_description IS NOT NULL) OR (T.product_description IS NOT NULL AND S.product_description IS NULL)
		OR		 T.promo <> S.promo OR (T.promo IS NULL AND S.promo IS NOT NULL) OR (T.promo IS NOT NULL AND S.promo IS NULL)
		OR		 T.ean <> S.ean OR (T.ean IS NULL AND S.ean IS NOT NULL) OR (T.ean IS NOT NULL AND S.ean IS NULL)
		OR		 T.integral_code <> S.integral_code OR (T.integral_code IS NULL AND S.integral_code IS NOT NULL) OR (T.integral_code IS NOT NULL AND S.integral_code IS NULL)
		OR		 T.series <> S.series OR (T.series IS NULL AND S.series IS NOT NULL) OR (T.series IS NOT NULL AND S.series IS NULL)
		OR		 T.category <> S.category OR (T.category IS NULL AND S.category IS NOT NULL) OR (T.category IS NOT NULL AND S.category IS NULL)
		OR		 T.brand <> S.brand OR (T.brand IS NULL AND S.brand IS NOT NULL) OR (T.brand IS NOT NULL AND S.brand IS NULL)
		OR		 T.range <> S.range OR (T.range IS NULL AND S.range IS NOT NULL) OR (T.range IS NOT NULL AND S.range IS NULL)
		OR		 T.product_description_en <> S.product_description_en OR (T.product_description_en IS NULL AND S.product_description_en IS NOT NULL) OR (T.product_description_en IS NOT NULL AND S.product_description_en IS NULL)
		OR		 T.category_en <> S.category_en OR (T.category_en IS NULL AND S.category_en IS NOT NULL) OR (T.category_en IS NOT NULL AND S.category_en IS NULL)
		OR		 T.box_capacity <> S.box_capacity OR (T.box_capacity IS NULL AND S.box_capacity IS NOT NULL) OR (T.box_capacity IS NOT NULL AND S.box_capacity IS NULL)
		OR		 T.dimension_h <> S.dimension_h OR (T.dimension_h IS NULL AND S.dimension_h IS NOT NULL) OR (T.dimension_h IS NOT NULL AND S.dimension_h IS NULL)
		OR		 T.dimension_w <> S.dimension_w OR (T.dimension_w IS NULL AND S.dimension_w IS NOT NULL) OR (T.dimension_w IS NOT NULL AND S.dimension_w IS NULL)
		OR		 T.dimension_l <> S.dimension_l OR (T.dimension_l IS NULL AND S.dimension_l IS NOT NULL) OR (T.dimension_l IS NOT NULL AND S.dimension_l IS NULL)
		OR		 T.pallete_capacity <> S.pallete_capacity OR (T.pallete_capacity IS NULL AND S.pallete_capacity IS NOT NULL) OR (T.pallete_capacity IS NOT NULL AND S.pallete_capacity IS NULL)
		OR		 T.box_dimension_h <> S.box_dimension_h OR (T.box_dimension_h IS NULL AND S.box_dimension_h IS NOT NULL) OR (T.box_dimension_h IS NOT NULL AND S.box_dimension_h IS NULL)
		OR		 T.box_dimension_w <> S.box_dimension_w OR (T.box_dimension_w IS NULL AND S.box_dimension_w IS NOT NULL) OR (T.box_dimension_w IS NOT NULL AND S.box_dimension_w IS NULL)
		OR		 T.box_dimension_l <> S.box_dimension_l OR (T.box_dimension_l IS NULL AND S.box_dimension_l IS NOT NULL) OR (T.box_dimension_l IS NOT NULL AND S.box_dimension_l IS NULL)
		OR		 T.rep_state <> S.rep_state OR (T.rep_state IS NULL AND S.rep_state IS NOT NULL) OR (T.rep_state IS NOT NULL AND S.rep_state IS NULL)
		OR		 T.rep_state_www <> S.rep_state_www OR (T.rep_state_www IS NULL AND S.rep_state_www IS NOT NULL) OR (T.rep_state_www IS NOT NULL AND S.rep_state_www IS NULL)
		OR		 T.kgo <> S.kgo OR (T.kgo IS NULL AND S.kgo IS NOT NULL) OR (T.kgo IS NOT NULL AND S.kgo IS NULL)

		)


		THEN UPDATE
		SET  T.product_id = S.product_id
			,T.product_description = S.product_description
			,T.promo = S.promo
			,T.ean = S.ean
			,T.integral_code = S.integral_code
			,T.series = S.series
			,T.category = S.category
			,T.brand = S.brand
			,T.range = S.range
			,T.product_description_en = S.product_description_en
			,T.category_en = S.category_en
			,T.box_capacity = S.box_capacity
			,T.dimension_h = S.dimension_h
			,T.dimension_w = S.dimension_w
			,T.dimension_l = S.dimension_l
			,T.pallete_capacity = S.pallete_capacity
			,T.box_dimension_h = S.box_dimension_h
			,T.box_dimension_w = S.box_dimension_w
			,T.box_dimension_l = S.box_dimension_l
			,T.rep_state = S.rep_state
			,T.rep_state_www = S.rep_state_www
			,T.kgo = S.kgo
			,T.LastUpdate = S.LastUpdate
			,T.Action = 'PUT' -- when there is a change, next request should be PUT
				
		WHEN NOT MATCHED BY TARGET
		THEN INSERT
		(
			 product_id
			,product_code
			,product_description
			,promo
			,ean
			,integral_code
			,series
			,category
			,brand
			,range
			,product_description_en
			,category_en
			,box_capacity
			,dimension_h
			,dimension_w
			,dimension_l
			,pallete_capacity
			,box_dimension_h
			,box_dimension_w
			,box_dimension_l
			,rep_state
			,rep_state_www
			,kgo
			,LastUpdate
			,Action
		)
		VALUES
		(
			 S.product_id
			,S.product_code
			,S.product_description
			,S.promo
			,S.ean
			,S.integral_code
			,S.series
			,S.category
			,S.brand
			,S.range
			,S.product_description_en
			,S.category_en
			,S.box_capacity
			,S.dimension_h
			,S.dimension_w
			,S.dimension_l
			,S.pallete_capacity
			,S.box_dimension_h
			,S.box_dimension_w
			,S.box_dimension_l
			,S.rep_state
			,S.rep_state_www
			,S.kgo
			,S.LastUpdate
			,'POST' -- when there is a new object, next request should be POST
		)

		WHEN NOT MATCHED BY SOURCE AND T.DeletedOn IS NULL
		THEN UPDATE
		SET  T.DeletedOn = GETDATE()
			,T.Action = CASE WHEN T.ResponseCode IS NULL THEN NULL -- when object does not exist anymore but havent been published yet then set action to NULL
							 ELSE 'DELETE' END; -- when object does not exist anymore, next request should be DELETE

		SET @EventRowcount = @@ROWCOUNT

		EXEC dbo.EventHandler
			 @ProcedureName = @PROCEDURE_NAME,@SchemaName = @SCHEMA_NAME
			,@EventRowcount = @EventRowcount
			,@EventMessage = 'Rowcount'
			,@EventParams = 'product'

		/* log complete */
		EXEC dbo.EventHandler
			 @ProcedureName = @PROCEDURE_NAME,@SchemaName = @SCHEMA_NAME
			,@EventMessage = 'Completed'

	END TRY
	BEGIN CATCH
		IF @@TRANCOUNT > 0 ROLLBACK TRAN
		EXEC dbo.EventHandler /* this will reraise error and cause to bomb out in global try/catch */
			 @ProcedureName = @PROCEDURE_NAME,@SchemaName = @SCHEMA_NAME
			,@EventMessage = 'Unable to populate table data.product'
	END CATCH

END