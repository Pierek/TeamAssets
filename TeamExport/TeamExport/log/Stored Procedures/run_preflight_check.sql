--- <summary>run_preflight_check and send an email msg if positive</summary>
--- <event author="Piotr Purwin" date="2018-03-15" project="TEAM">Procedure created</event>
CREATE PROCEDURE log.run_preflight_check

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
			,@NewLineChar char(2)
			,@duplicates varchar(MAX)
			,@currency varchar(MAX)
			

	BEGIN TRY
		/* initialise constants */
		SET	@PROCEDURE_NAME = ISNULL(OBJECT_NAME(@@PROCID),'Debug')
		SET @SCHEMA_NAME = ISNULL(OBJECT_SCHEMA_NAME(@@PROCID),'Debug')

		SET @NewLineChar = CHAR(13) + CHAR(10)

		/* log start */
		EXEC dbo.EventHandler
			 @ProcedureName = @PROCEDURE_NAME,@SchemaName = @SCHEMA_NAME
			,@EventMessage = 'Started'
		

		/* 1. Check if there are duplicated product_codes */

		;WITH products AS (
			SELECT
				 product_code
			FROM data.product
			WHERE REPLACE(product_code,' ','') IN (
													SELECT
														 [product] = REPLACE(product_code,' ','')
													FROM data.product
													GROUP BY REPLACE(product_code,' ','')
													HAVING COUNT(*) > 1
												)
		)
		SELECT @duplicates = (SELECT STUFF((SELECT
												 @NewLineChar + product_code
											FROM products
											ORDER BY REPLACE(product_code,' ','')
											FOR XML PATH(''), TYPE
											).value('.', 'varchar(MAX)') 
											,1,2,''))


		IF @duplicates IS NOT NULL
		BEGIN
			IF NOT EXISTS(
							SELECT 1
							FROM log.preflight_checks
							WHERE check_name = 'Duplicated product_codes'
								--AND data = @duplicates
						)
			BEGIN
				INSERT INTO log.preflight_checks
				(
					 [check_name]
					,[data]
				)
				SELECT
					 [check_name] = 'Duplicated product_codes'
					,[data] = @duplicates
			END
		END

		IF @duplicates IS NULL
		BEGIN
			DELETE FROM log.preflight_checks
			WHERE check_name = 'Duplicated product_codes'
		END


		/* 2. Check for proper currency codes */

		;WITH currency AS (
			SELECT
				 P.product_code
				,C.price_client_description
				,PR.currency_code
			FROM data.price PR
			INNER JOIN data.product P
				ON P.product_id = PR.product_id
			INNER JOIN data.price_client_dict C
				ON C.price_client_id = PR.price_client_id
			LEFT JOIN data.currency CU
				ON CU.currency_code = PR.currency_code
			WHERE CU.currency_code IS NULL
		)
		SELECT @currency = (SELECT STUFF((SELECT
												@NewLineChar + product_code + ', ' + price_client_description + ' - Currency: ' + currency_code
										  FROM currency
										  ORDER BY product_code, price_client_description, currency_code
										  FOR XML PATH(''), TYPE
										  ).value('.', 'varchar(MAX)') 
										  ,1,2,''))

		IF @currency IS NOT NULL
		BEGIN
			IF NOT EXISTS(
							SELECT 1
							FROM log.preflight_checks
							WHERE check_name = 'Invalid currency'
								--AND data = @currency
						)
			BEGIN
				INSERT INTO log.preflight_checks
				(
					 [check_name]
					,[data]
				)
				SELECT
					 [check_name] = 'Invalid currency'
					,[data] = @currency
			END
		END

		IF @currency IS NULL
		BEGIN
			DELETE FROM log.preflight_checks
			WHERE check_name = 'Invalid currency'
		END




		/* send email and raise error */
		IF EXISTS (SELECT 1 FROM log.preflight_checks WHERE email_datetime IS NULL OR email_datetime + '01:00:00' < GETDATE())
		BEGIN
			UPDATE log.preflight_checks
				 SET email_datetime = GETDATE()

		DECLARE @subject varchar(100) = 'TeamExport build notifier'
		DECLARE @body varchar(max)

		SET @body = 'Check data in source system:' + @NewLineChar + ISNULL((SELECT check_name + ' (' + CONVERT(varchar(23),email_datetime) + '):' + @NewLineChar + data
													  FROM log.preflight_checks WHERE [check_name] = 'Duplicated product_codes'),'')
												+ @NewLineChar +  ISNULL((SELECT check_name + ' (' + CONVERT(varchar(23),email_datetime) + '):' + @NewLineChar + data
													FROM log.preflight_checks WHERE [check_name] = 'Invalid currency'),'')


		EXEC msdb.dbo.sp_send_dbmail
			 @profile_name = 'TeamProfile'
			,@recipients='purwinp@gmail.com'
			,@subject=@subject
			,@body=@body


		RAISERROR('Disrepency in data - please correct the data',16,1)

		END




		/* log complete */
		EXEC dbo.EventHandler
			 @ProcedureName = @PROCEDURE_NAME,@SchemaName = @SCHEMA_NAME
			,@EventMessage = 'Completed'

	END TRY
	BEGIN CATCH
		IF @@TRANCOUNT > 0 ROLLBACK TRAN
		EXEC dbo.EventHandler /* this will reraise error and cause to bomb out in global try/catch */
			 @ProcedureName = @PROCEDURE_NAME,@SchemaName = @SCHEMA_NAME
			,@EventMessage = 'Unable to run preflight checks'
	END CATCH

END