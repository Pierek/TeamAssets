--- <summary>Move stock data from enova to TeamExport</summary>
--- <event author="Piotr Purwin" date="2017-11-02" project="TEAM">Procedure created</event>
CREATE PROCEDURE [import].populate_stock

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

		MERGE [data].stock T
		USING [import].stock S
		ON (
			T.product_id = S.product_id
			AND ISNULL(T.client_id,'') = ISNULL(S.client_id,'')
			AND T.stock_dict = S.stock_dict
			)
		WHEN MATCHED AND ( 

			T.quantity <> S.quantity OR (T.quantity IS NULL AND S.quantity IS NOT NULL) OR (T.quantity IS NOT NULL AND S.quantity IS NULL)
		)


		THEN UPDATE
		SET  T.quantity = S.quantity
			,T.LastUpdate = S.LastUpdate 
			,T.LastUser = S.LastUser 
				
		WHEN NOT MATCHED
		THEN INSERT
		(
			 product_id
			,client_id
			,quantity
			,stock_dict
			,LastUpdate
			,LastUser
		)
		VALUES
		(
			 S.product_id
			,S.client_id
			,S.quantity
			,S.stock_dict
			,S.LastUpdate
			,S.LastUser
		)

		WHEN NOT MATCHED BY SOURCE AND T.DeletedOn IS NULL
		THEN UPDATE
		SET  T.DeletedOn = GETDATE();


		SET @EventRowcount = @@ROWCOUNT

		EXEC dbo.EventHandler
			 @ProcedureName = @PROCEDURE_NAME,@SchemaName = @SCHEMA_NAME
			,@EventRowcount = @EventRowcount
			,@EventMessage = 'Rowcount'
			,@EventParams = 'stock'

		/* log complete */
		EXEC dbo.EventHandler
			 @ProcedureName = @PROCEDURE_NAME,@SchemaName = @SCHEMA_NAME
			,@EventMessage = 'Completed'

	END TRY
	BEGIN CATCH
		IF @@TRANCOUNT > 0 ROLLBACK TRAN
		EXEC dbo.EventHandler /* this will reraise error and cause to bomb out in global try/catch */
			 @ProcedureName = @PROCEDURE_NAME,@SchemaName = @SCHEMA_NAME
			,@EventMessage = 'Unable to populate table data.stock'
	END CATCH

END