--- <summary>Move currenct data from enova to TeamExport</summary>
--- <event author="Piotr Purwin" date="2017-11-02" project="TEAM">Procedure created</event>
CREATE PROCEDURE [import].populate_currency

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

		MERGE [data].currency T
		USING [import].currency S
		ON (T.currency_id = S.currency_id) 
		WHEN MATCHED AND ( 

			T.currency_code <> S.currency_code OR (T.currency_code IS NULL AND S.currency_code IS NOT NULL) OR (T.currency_code IS NOT NULL AND S.currency_code IS NULL)
		OR	T.currency_description <> S.currency_description OR (T.currency_description IS NULL AND S.currency_description IS NOT NULL) OR (T.currency_description IS NOT NULL AND S.currency_description IS NULL)
		)


		THEN UPDATE
		SET  T.currency_code = S.currency_code
			,T.currency_description = S.currency_description
			,T.LastUpdate = S.LastUpdate 
				
		WHEN NOT MATCHED BY TARGET
		THEN INSERT
		(
			 currency_id
			,currency_code
			,currency_description
			,LastUpdate
		)
		VALUES
		(
			 S.currency_id
			,S.currency_code
			,S.currency_description
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
			,@EventParams = 'currency'

		/* log complete */
		EXEC dbo.EventHandler
			 @ProcedureName = @PROCEDURE_NAME,@SchemaName = @SCHEMA_NAME
			,@EventMessage = 'Completed'

	END TRY
	BEGIN CATCH
		IF @@TRANCOUNT > 0 ROLLBACK TRAN
		EXEC dbo.EventHandler /* this will reraise error and cause to bomb out in global try/catch */
			 @ProcedureName = @PROCEDURE_NAME,@SchemaName = @SCHEMA_NAME
			,@EventMessage = 'Unable to populate table data.currency'
	END CATCH

END