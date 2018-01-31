--- <summary>Wrapper procedure</summary>
--- <event author="Piotr Purwin" date="2017-11-02" project="TEAM">Procedure created</event>
CREATE PROCEDURE dbo.FullRefresh

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
			,@start_time datetime

	BEGIN TRY
		/* initialise constants */
		SET	@PROCEDURE_NAME = ISNULL(OBJECT_NAME(@@PROCID),'Debug')
		SET @SCHEMA_NAME = ISNULL(OBJECT_SCHEMA_NAME(@@PROCID),'Debug')

		SET @start_time = GETDATE()

		/* log start */
		EXEC dbo.EventHandler
			 @ProcedureName = @PROCEDURE_NAME,@SchemaName = @SCHEMA_NAME
			,@EventMessage = 'Started'
		

		/* procedures */
		EXEC import.populate_product

		EXEC import.populate_client_dict

		EXEC import.populate_price_client_dict

		EXEC import.populate_currency

		EXEC import.populate_stock

		EXEC import.populate_price

		EXEC sp_MSforeachtable 'IF NOT EXISTS (SELECT 1 FROM ?) AND LEFT(''?'',6) = ''[data]'' RAISERROR (''Some tables are empty'',16,1)'

		/* if everything went ok, insert start and end time with OK status to the log table */
		INSERT INTO log.job_log (start_time, end_time, status) SELECT @start_time, GETDATE(), 'OK'

		/* log complete */
		EXEC dbo.EventHandler
			 @ProcedureName = @PROCEDURE_NAME,@SchemaName = @SCHEMA_NAME
			,@EventMessage = 'Completed'

	END TRY
	BEGIN CATCH
		IF @@TRANCOUNT > 0 ROLLBACK TRAN
		BEGIN
			EXEC dbo.EventHandler /* this will reraise error and cause to bomb out in global try/catch */
				 @ProcedureName = @PROCEDURE_NAME,@SchemaName = @SCHEMA_NAME
				,@EventMessage = 'Unable to run procedure dbo.FullRefresh'

			/* if job fails, insert start and end time with ERROR status to the log table */
			INSERT INTO log.job_log (start_time, end_time, status) SELECT @start_time, GETDATE(), 'ERROR'
		END
	END CATCH

END