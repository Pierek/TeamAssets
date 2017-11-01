CREATE TABLE [dbo].[tblEventType]
(
     [EventTypeId]   int            NOT NULL
    ,[EventTypeCode] nvarchar(3)     NOT NULL
    ,[Description]   nvarchar(64)    NOT NULL
    ,[AddDate]       datetime       NOT NULL
    ,[AddUser]       nvarchar(32)   NOT NULL
    ,[ModDate]       datetime       NOT NULL
    ,[ModUser]       nvarchar(32)   NOT NULL
    ,CONSTRAINT [PK_tblEventType] PRIMARY KEY CLUSTERED([EventTypeId] ASC)
    ,CONSTRAINT [NX1_tblEventType] UNIQUE NONCLUSTERED([EventTypeCode] ASC)
);
GO
--- <summary>Updates ModUser/ModDate to trace changes</summary>
--- <event author="Piotr Purwin" date="2017-10-15" project="TEAM">Trigger Created.</event>
CREATE TRIGGER [dbo].[trgEventType] ON [dbo].[tblEventType]
AFTER UPDATE

AS

BEGIN
	SET	NOCOUNT ON

    UPDATE	X
    SET
         ModDate = GETDATE()
		,ModUser = SYSTEM_USER
	FROM [dbo].[tblEventType] X
	INNER JOIN inserted I
		ON	I.[EventTypeId] = X.[EventTypeId]
END
