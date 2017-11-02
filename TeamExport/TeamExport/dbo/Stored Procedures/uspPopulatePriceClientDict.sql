--- <summary>Move PriceClientDict data from enova to TeamExport</summary>
--- <event author="Piotr Purwin" date="2017-11-02" project="TEAM">Procedure created</event>
CREATE PROCEDURE [dbo].[uspPopulatePriceClientDict]

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

		MERGE dbo.tblPriceClientDict T
		USING dbo.vwPriceClientDict S
		ON (T.price_client_code = S.price_client_code) 
		WHEN MATCHED AND ( 

			 T.price_client_id <> S.price_client_id OR (T.price_client_id IS NULL AND S.price_client_id IS NOT NULL) OR (T.price_client_id IS NOT NULL AND S.price_client_id IS NULL)
		)


		THEN UPDATE
		SET  T.price_client_id = S.price_client_id
			,T.LastUpdate = S.LastUpdate 
			,T.LastUser = S.LastUser 
				
		WHEN NOT MATCHED
		THEN INSERT
		(
			 price_client_id
			,price_client_code
			,LastUpdate
			,LastUser
		)
		VALUES
		(
			 S.price_client_id
			,S.price_client_code
			,S.LastUpdate
			,S.LastUser
		);


		SET @EventRowcount = @@ROWCOUNT

		EXEC dbo.uspEventHandler
			 @ProcedureName = @PROCEDURE_NAME,@SchemaName = @SCHEMA_NAME
			,@EventRowcount = @EventRowcount
			,@EventMessage = 'Rowcount'
			,@EventParams = 'PriceClientDict'

		/* log complete */
		EXEC dbo.uspEventHandler
			 @ProcedureName = @PROCEDURE_NAME,@SchemaName = @SCHEMA_NAME
			,@EventMessage = 'Completed'

	END TRY
	BEGIN CATCH
		IF @@TRANCOUNT > 0 ROLLBACK TRAN
		EXEC dbo.uspEventHandler /* this will reraise error and cause to bomb out in global try/catch */
			 @ProcedureName = @PROCEDURE_NAME,@SchemaName = @SCHEMA_NAME
			,@EventMessage = 'Unable to populate table dbo.tblPriceClientDict'
	END CATCH

END