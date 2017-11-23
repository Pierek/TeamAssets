CREATE TABLE [log].[EventLog]
(
	 [EventLogId]      int IDENTITY(1,1) NOT NULL
	,[EventTypeId]     int NOT NULL
	,[EventDate]       datetime NOT NULL
	,[DatabaseName]    nvarchar(255) NOT NULL
	,[SchemaName]      nvarchar(255) NOT NULL
	,[ProcedureName]   nvarchar(max) NOT NULL
	,[NestLevel]       tinyint NULL
	,[EventMessage]    nvarchar(max) NULL
	,[EventParameters] nvarchar(max) NULL
	,[EventRowcount]   int NULL
	,[ErrorMessage]    nvarchar(max) NULL
	,[ErrorNumber]     int NULL
	,[ErrorLine]       int NULL
	,[ErrorSeverity]   int NULL
	,[ErrorState]      tinyint NULL
	,[AddDate]         datetime CONSTRAINT [DF_EventLog_AddDate] DEFAULT GETDATE() NULL
	,[AddUser]         nvarchar(128) CONSTRAINT [DF_EventLog_AddUser] DEFAULT SUSER_SNAME() NULL
	,CONSTRAINT [PK_EventLog] PRIMARY KEY CLUSTERED([EventLogId] ASC)
);
