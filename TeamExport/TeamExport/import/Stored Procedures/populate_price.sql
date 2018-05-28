--- <summary>Move price data from enova to TeamExport</summary>
--- <event author="Piotr Purwin" date="2017-01-29" project="TEAM">Procedure created</event>
CREATE PROCEDURE [import].populate_price

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

		MERGE [data].price T
		USING [import].price S
		ON (
			T.product_id = S.product_id
			AND T.price_client_id = S.price_client_id
			)
		WHEN MATCHED AND ( 

			T.netto_price <> S.netto_price OR (T.netto_price IS NULL AND S.netto_price IS NOT NULL) OR (T.netto_price IS NOT NULL AND S.netto_price IS NULL)
		--OR	T.brutto_price <> S.brutto_price OR (T.brutto_price IS NULL AND S.brutto_price IS NOT NULL) OR (T.brutto_price IS NOT NULL AND S.brutto_price IS NULL)
		OR	T.currency_code <> S.currency_code OR (T.currency_code IS NULL AND S.currency_code IS NOT NULL) OR (T.currency_code IS NOT NULL AND S.currency_code IS NULL)
		)

		THEN UPDATE
		SET  T.netto_price = S.netto_price
			--,T.brutto_price = S.brutto_price
			,T.currency_code = S.currency_code
			,T.LastUpdate = S.LastUpdate
			,T.Action = CASE WHEN T.Action = 'POST' THEN 'POST' ELSE 'PUT' END -- when there is a change, next request should be PUT
				
		WHEN NOT MATCHED BY TARGET
		THEN INSERT
		(
			 product_id
			,price_client_id
			,netto_price
			--,brutto_price
			,currency_code
			,LastUpdate
			,Action
		)
		VALUES
		(
			 S.product_id
			,S.price_client_id
			,S.netto_price
			--,S.brutto_price
			,S.currency_code
			,S.LastUpdate
			,'POST' -- when there is a new object, next request should be POST
		)

		WHEN NOT MATCHED BY SOURCE AND T.netto_price <> 0 --AND T.brutto_price <> 0
		THEN UPDATE
		SET  T.netto_price = 0
			--,T.brutto_price = 0 
			,T.Action = 'PUT'; -- when object does not exist anymore, next request should be PUT


		SET @EventRowcount = @@ROWCOUNT

		EXEC dbo.EventHandler
			 @ProcedureName = @PROCEDURE_NAME,@SchemaName = @SCHEMA_NAME
			,@EventRowcount = @EventRowcount
			,@EventMessage = 'Rowcount'
			,@EventParams = 'price'

		/* log complete */
		EXEC dbo.EventHandler
			 @ProcedureName = @PROCEDURE_NAME,@SchemaName = @SCHEMA_NAME
			,@EventMessage = 'Completed'

	END TRY
	BEGIN CATCH
		IF @@TRANCOUNT > 0 ROLLBACK TRAN
		EXEC dbo.EventHandler /* this will reraise error and cause to bomb out in global try/catch */
			 @ProcedureName = @PROCEDURE_NAME,@SchemaName = @SCHEMA_NAME
			,@EventMessage = 'Unable to populate table data.price'
	END CATCH

END