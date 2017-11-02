--- <summary>Move ClientDict data from enova to TeamExport</summary>
--- <event author="Piotr Purwin" date="2017-11-02" project="TEAM">Procedure created</event>
CREATE PROCEDURE [dbo].[uspPopulateClientDict]

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

		MERGE dbo.tblClientDict T
		USING dbo.vwClientDict S
		ON (T.client_code = S.client_code) 
		WHEN MATCHED AND ( 

			T.client_id <> S.client_id OR (T.client_id IS NULL AND S.client_id IS NOT NULL) OR (T.client_id IS NOT NULL AND S.client_id IS NULL)
		OR	T.client_description <> S.client_description OR (T.client_description IS NULL AND S.client_description IS NOT NULL) OR (T.client_description IS NOT NULL AND S.client_description IS NULL)
		)


		THEN UPDATE
		SET  T.client_id = S.client_id
			,T.client_description = S.client_description
			,T.LastUpdate = S.LastUpdate 
			,T.LastUser = S.LastUser 
				
		WHEN NOT MATCHED
		THEN INSERT
		(
			 client_id
			,client_code
			,client_description
			,LastUpdate
			,LastUser
		)
		VALUES
		(
			 S.client_id
			,S.client_code
			,S.client_description
			,S.LastUpdate
			,S.LastUser
		);


		SET @EventRowcount = @@ROWCOUNT

		EXEC dbo.uspEventHandler
			 @ProcedureName = @PROCEDURE_NAME,@SchemaName = @SCHEMA_NAME
			,@EventRowcount = @EventRowcount
			,@EventMessage = 'Rowcount'
			,@EventParams = 'ClientDict'

		/* log complete */
		EXEC dbo.uspEventHandler
			 @ProcedureName = @PROCEDURE_NAME,@SchemaName = @SCHEMA_NAME
			,@EventMessage = 'Completed'

	END TRY
	BEGIN CATCH
		IF @@TRANCOUNT > 0 ROLLBACK TRAN
		EXEC dbo.uspEventHandler /* this will reraise error and cause to bomb out in global try/catch */
			 @ProcedureName = @PROCEDURE_NAME,@SchemaName = @SCHEMA_NAME
			,@EventMessage = 'Unable to populate table dbo.tblClientDict'
	END CATCH

END