--- <summary>Default Event Handler for ECAT DM Process</summary>
--- <concept>Error Handling</concept>
--- <link>http://www.sommarskog.se/error_handling_2005.html</link>
--- <link>http://sqlfool.com/2008/12/error-handling-in-t-sql</link>
--- <link>http://www.sommarskog.se/error_handling/Part3.html</link>
--- <event author="Piotr Purwin" date="2017-10-15" project="TEAM">Procedure Created.</event>
CREATE PROCEDURE [dbo].[uspEventHandler]
(
	@EventTypeId	tinyint			= 1,	--- <param name="@EventType">Dummy parameter</param>
	@ProcedureName	sysname			= NULL,	--- <param name="@ProcedureName">Name of the calling Procedure.</param>
	@SchemaName		sysname			= NULL,	--- <param name="@SchemaName">Name of schema of the calling Procedure.</param>
	@EventMessage	nvarchar(MAX)	= NULL,	--- <param name="@EventMessage">Description of the Event.</param>
	@EventParams	nvarchar(MAX)	= NULL,	--- <param name="@EventParams">Parameters used for the Event.</param>
	@EventRowcount	int				= NULL,	--- <param name="@EventRowcount">Rowcount returned from the Event.</param>
	@RaiseError		bit				= NULL	--- <param name="@RaiseError">Do we want to raise an Error with the details provided?</param>
)

AS

BEGIN

	SET	XACT_ABORT, NOCOUNT ON

	BEGIN TRY 
		
		/* declare variables */
		DECLARE	@ErrorMessage nvarchar(MAX) = ERROR_MESSAGE()	--- <var name="@ErrorMessage" type="nvarchar(MAX)">Stores the Error Message Text.</var>
				,@ErrorSeverity tinyint = ERROR_SEVERITY()		--- <var name="@ErrorSeverity" type="tinyint">Stores the Severity of the Error.</var>
				,@ErrorState tinyint = ERROR_STATE()			--- <var name="@ErrorState" type="tinyint">Stores the State Number of the Error.</var>
				,@ErrorNumber int = ERROR_NUMBER()				--- <var name="@ErrorNumber" type="int">Stores the Error Number.</var>
				,@ErrorLine int = ERROR_LINE()					--- <var name="@ErrorLine" type="int">Stores the line number at which the Error occured.</var>
				,@CustomErrorMessage nvarchar(2048)				--- <var name="@CustomErrorMessage" type="nvarchar(2048)">Stores the Custom Message we will raise back to calling procedure.</var>
				,@ErrorProcedure sysname = ERROR_PROCEDURE()

	
		IF @@ERROR <> 0 and @@TRANCOUNT > 0 ROLLBACK TRANSACTION	/* Always roll back the transaction in case of an error */

		/* initialise variables */
		SET @ProcedureName = COALESCE(@ProcedureName, @ErrorProcedure)
		SET @SchemaName = COALESCE(@SchemaName, '')
		SET @EventMessage = COALESCE(@EventMessage, 'No EventMessage provided')
	
		SET	@RaiseError =	
				CASE WHEN @RaiseError IS NULL and @ErrorSeverity >= 11 /* Should always raise for severity >= 11 */
					THEN 1
					WHEN @RaiseError IS NULL and @ErrorSeverity < 11
					THEN 0
					ELSE @RaiseError 
				END

		SET	@CustomErrorMessage =
				COALESCE(QUOTENAME(@ProcedureName), '<dynamic SQL>') +
				': Msg ' + LTRIM(STR(@ErrorNumber)) +
				', Line ' + LTRIM(STR(@ErrorLine)) +
				': ' + ISNULL(@EventMessage + ': ', '') + @ErrorMessage

		SET	@ProcedureName = COALESCE(@ProcedureName, '<dynamic SQL>')

		INSERT INTO [dbo].[tblEventLog]
		(
			 [EventTypeId]
			,[EventDate]
			,[DatabaseName]
			,[SchemaName]
			,[ProcedureName]
			,[NestLevel]
			,[EventMessage]
			,[EventParameters]
			,[EventRowcount]
			,[ErrorMessage]
			,[ErrorNumber]
			,[ErrorLine]
			,[ErrorSeverity]
			,[ErrorState]
		)
		VALUES
		(
			@EventTypeId
			,GETDATE()
			,DB_NAME()
			,@SchemaName
			,@ProcedureName
			,@@NESTLEVEL - 1
			,@EventMessage
			,@EventParams
			,@EventRowcount
			,@ErrorMessage
			,@ErrorNumber
			,@ErrorLine
			,@ErrorSeverity
			,@ErrorState
		)
	END	TRY
	BEGIN CATCH		
		DECLARE @NewErrorMessage nvarchar(MAX)

		SET @RaiseError = 1
		SET @NewErrorMessage = ERROR_MESSAGE()
		SET @CustomErrorMessage = 
				'[dbo].[uspEventHandler] failed with: ' +
				@NewErrorMessage +  ', Original message: ' + @ErrorMessage


		IF XACT_STATE() = -1 ROLLBACK TRANSACTION	/* Avoid new error if transaction is doomed. If -1, the transaction is uncommittable and should be rolled back. */
	END CATCH
	IF @RaiseError = 1	/* Reraise if requested (or if an unexepected error occurred).*/
		BEGIN
			IF @ErrorSeverity > 18 
			BEGIN
				SET @ErrorSeverity = 18	/* Adjust severity if needed; plain users cannot raise level 19.*/
			END
			RAISERROR(@CustomErrorMessage,  @ErrorSeverity, @ErrorState) 
		END
END