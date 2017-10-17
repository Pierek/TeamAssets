--- <summary>Move Product data from enova to TeamExport</summary>
--- <event author="Piotr Purwin" date="2017-10-16" project="TEAM">Procedure created</event>
CREATE PROCEDURE [dbo].[uspPopulateProduct]

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
		EXEC dbo.uspEventHandler
			 @ProcedureName = @PROCEDURE_NAME,@SchemaName = @SCHEMA_NAME
			,@EventMessage = 'Started'

		/* merge data */

		MERGE dbo.tblProduct T
		USING dbo.vwProduct S
		ON (T.product_code = S.product_code) 
		WHEN MATCHED AND 
		CHECKSUM(S.product_description,S.ean,S.integral_code,S.series,S.category,S.brand,S.Pojemnosc_Opakowania,S.dimension_h,S.dimension_w,S.dimension_l,S.Max_Na_Palecie,S.Karton_Wysokosc,S.Karton_Szerokosc,S.Karton_Dlugosc,S.description,S.category_en,S.rap_state,S.rap_state_www,S.kgo)
		<>
		CHECKSUM(T.product_description,T.ean,T.integral_code,T.series,T.category,T.brand,T.Pojemnosc_Opakowania,T.dimension_h,T.dimension_w,T.dimension_l,T.Max_Na_Palecie,T.Karton_Wysokosc,T.Karton_Szerokosc,T.Karton_Dlugosc,T.description,T.category_en,T.rap_state,T.rap_state_www,T.kgo)

			THEN UPDATE
				SET  T.product_description = S.product_description
					,T.ean = S.ean
					,T.integral_code = S.integral_code
					,T.series = S.series
					,T.category = S.category
					,T.brand = S.brand
					,T.Pojemnosc_Opakowania = S.Pojemnosc_Opakowania
					,T.dimension_h = S.dimension_h
					,T.dimension_w = S.dimension_w
					,T.dimension_l = S.dimension_l
					,T.Max_Na_Palecie = S.Max_Na_Palecie
					,T.Karton_Wysokosc = S.Karton_Wysokosc
					,T.Karton_Szerokosc = S.Karton_Szerokosc
					,T.Karton_Dlugosc = S.Karton_Dlugosc
					,T.description = S.description
					,T.category_en = S.category_en
					,T.rap_state = S.rap_state
					,T.rap_state_www = S.rap_state_www
					,T.LastUpdate = S.LastUpdate 
					,T.LastUser = S.LastUser 
				
		WHEN NOT MATCHED
			THEN INSERT(Id,product_code,product_description,ean,integral_code,series,category,brand,Pojemnosc_Opakowania,dimension_h,dimension_w,dimension_l,Max_Na_Palecie,Karton_Wysokosc,Karton_Szerokosc,Karton_Dlugosc,description,category_en,rap_state,rap_state_www,kgo,LastUpdate,LastUser)
			VALUES(S.Id,S.product_code,S.product_description,S.ean,S.integral_code,S.series,S.category,S.brand,S.Pojemnosc_Opakowania,S.dimension_h,S.dimension_w,S.dimension_l,S.Max_Na_Palecie,S.Karton_Wysokosc,S.Karton_Szerokosc,S.Karton_Dlugosc,S.description,S.category_en,S.rap_state,S.rap_state_www,S.kgo,S.LastUpdate,S.LastUser);


		SET @EventRowcount = @@ROWCOUNT

		EXEC dbo.uspEventHandler
			 @ProcedureName = @PROCEDURE_NAME,@SchemaName = @SCHEMA_NAME
			,@EventRowcount = @EventRowcount
			,@EventMessage = 'Rowcount'
			,@EventParams = 'Products'

		/* log complete */
		EXEC dbo.uspEventHandler
			 @ProcedureName = @PROCEDURE_NAME,@SchemaName = @SCHEMA_NAME
			,@EventMessage = 'Completed'

	END TRY
	BEGIN CATCH
		IF @@TRANCOUNT > 0 ROLLBACK TRAN
		EXEC dbo.uspEventHandler /* this will reraise error and cause to bomb out in global try/catch */
			 @ProcedureName = @PROCEDURE_NAME,@SchemaName = @SCHEMA_NAME
			,@EventMessage = 'Unable to populate table dbo.tblProduct'
	END CATCH

END