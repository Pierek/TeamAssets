TRUNCATE TABLE dbo.tblEventType;

INSERT INTO dbo.tblEventType
    (EventTypeId, EventTypeCode, Description, AddDate, AddUser, ModDate, ModUser)
VALUES 
     (1, 'SYS', 'SQL Error Messages'            ,GETDATE()  ,'MIG'  ,GETDATE()  ,'MIG')
    ,(2, 'BLD', 'Custom Build Error Message'    ,GETDATE()  ,'MIG'  ,GETDATE()  ,'MIG')
    ,(3, 'MSG', 'Message (Information Only)'    ,GETDATE()  ,'MIG'  ,GETDATE()  ,'MIG')

