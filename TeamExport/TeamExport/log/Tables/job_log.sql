CREATE TABLE [log].[job_log]
(
	 [job_id]          int NOT NULL IDENTITY(1,1) PRIMARY KEY
	,[start_datetime]  datetime NULL
	,[finish_datetime] datetime NULL
	,[status]          varchar(10) NULL
)
