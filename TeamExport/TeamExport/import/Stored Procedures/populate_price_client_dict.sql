--- <summary>Move PriceClientDict data from enova to TeamExport</summary>
--- <event author="Piotr Purwin" date="2017-11-02" project="TEAM">Procedure created</event>
CREATE PROCEDURE [import].populate_price_client_dict

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

		MERGE [data].price_client_dict T
		USING [import].price_client_dict S
		ON (T.price_client_code = S.price_client_code) 
		WHEN MATCHED AND ( 

			 T.price_client_id <> S.price_client_id OR (T.price_client_id IS NULL AND S.price_client_id IS NOT NULL) OR (T.price_client_id IS NOT NULL AND S.price_client_id IS NULL)
		)


		THEN UPDATE
		SET  T.price_client_id = S.price_client_id
			,T.LastUpdate = S.LastUpdate 
				
		WHEN NOT MATCHED
		THEN INSERT
		(
			 price_client_id
			,price_client_code
			,LastUpdate
		)
		VALUES
		(
			 S.price_client_id
			,S.price_client_code
			,S.LastUpdate
		)

		WHEN NOT MATCHED BY SOURCE AND T.DeletedOn IS NULL
		THEN UPDATE
		SET  T.DeletedOn = GETDATE();


		SET @EventRowcount = @@ROWCOUNT

		EXEC dbo.EventHandler
			 @ProcedureName = @PROCEDURE_NAME,@SchemaName = @SCHEMA_NAME
			,@EventRowcount = @EventRowcount
			,@EventMessage = 'Rowcount'
			,@EventParams = 'price_client_dict'

		/* log complete */
		EXEC dbo.EventHandler
			 @ProcedureName = @PROCEDURE_NAME,@SchemaName = @SCHEMA_NAME
			,@EventMessage = 'Completed'

	END TRY
	BEGIN CATCH
		IF @@TRANCOUNT > 0 ROLLBACK TRAN
		EXEC dbo.EventHandler /* this will reraise error and cause to bomb out in global try/catch */
			 @ProcedureName = @PROCEDURE_NAME,@SchemaName = @SCHEMA_NAME
			,@EventMessage = 'Unable to populate table data.price_client_dict'
	END CATCH

END