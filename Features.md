
# SQL Server Monitoring and Health Check Platform Features

## 1. Server Health Check
**Objective:** Monitor the overall health of the SQL Server, including version, edition, and service pack level.

**T-SQL Query:**
```bash
SELECT 
  SERVERPROPERTY('ProductVersion') AS 'Version',
  SERVERPROPERTY('Edition') AS 'Edition',
  SERVERPROPERTY('ProductLevel') AS 'Service Pack'
```
## 2. Error Log Monitoring
**Objective:** Analyze error logs to identify recent server issues and monitor error occurrences over time.

**T-SQL Query:**
```bash
EXEC sp_readerrorlog;
```

## 3. Disk Space Monitoring
**Objective:** Ensure there is adequate disk space on the server to prevent performance issues or crashes.

**T-SQL Query:**
```bash
EXEC xp_fixeddrives;
```

## 4. Backup Status Check
**Objective:** Verify that backups are occurring as scheduled and identify databases without recent backups.

**T-SQL Query:**
```bash
SELECT 
  sdb.Name AS DatabaseName,
  MAX(bus.backup_finish_date) AS LastBackupDate
FROM 
  master.sys.databases sdb
LEFT JOIN 
  msdb.dbo.backupset bus ON sdb.name = bus.database_name
WHERE 
  sdb.database_id NOT IN (2, 3)  -- Exclude system databases TempDB and Model
GROUP BY 
  sdb.Name
HAVING 
  MAX(bus.backup_finish_date) IS NULL OR 
  MAX(bus.backup_finish_date) < DATEADD(day, -1, GETDATE());
```

## 5. Performance Metrics Monitoring
**Objective:** Track and analyze key performance indicators like CPU usage, wait statistics, and I/O usage.

**T-SQL Query:**
```bash
SELECT 
  sqltext.TEXT,
  req.session_id,
  req.status,
  req.command,
  req.cpu_time,
  req.total_elapsed_time
FROM 
  sys.dm_exec_requests req
CROSS APPLY 
  sys.dm_exec_sql_text(req.sql_handle) AS sqltext
WHERE 
  req.status = 'running' 
  AND req.cpu_time > 0
ORDER BY 
  req.cpu_time DESC;
```

## 6. Job Status Monitoring
**Objective:** Monitor SQL Server Agent jobs to ensure they complete successfully and on schedule.

**T-SQL Query:**
```bash
SELECT 
  sj.name AS JobName,
  sj.enabled AS IsEnabled,
  sjs.last_run_date AS LastRunDate,
  sjs.last_run_time AS LastRunTime,
  sjs.last_run_outcome AS LastOutcome,
  CASE sjs.last_run_outcome 
    WHEN 0 THEN 'Failed'
    WHEN 1 THEN 'Succeeded'
    ELSE 'Unknown'
  END AS OutcomeDescription
FROM 
  msdb.dbo.sysjobs sj
JOIN 
  msdb.dbo.sysjobhistory sjs ON sj.job_id = sjs.job_id AND sjs.instance_id = (
    SELECT MAX(instance_id) 
    FROM msdb.dbo.sysjobhistory 
    WHERE job_id = sj.job_id
  );
```

## 7. Index Fragmentation Analysis
**Objective:** Identify and remedy index fragmentation to maintain optimal database performance.

**T-SQL Query:**
```bash
SELECT 
  dbschemas.[name] as 'Schema',  
  dbtables.[name] as 'Table',  
  dbindexes.[name] as 'Index',  
  indexstats.avg_fragmentation_in_percent,  
  indexstats.page_count  
FROM 
  sys.dm_db_index_physical_stats (DB_ID(), NULL, NULL, NULL, NULL) AS indexstats  
INNER JOIN 
  sys.tables dbtables on dbtables.[object_id] = indexstats.[object_id]  
INNER JOIN 
  sys.schemas dbschemas on dbtables.[schema_id] = dbschemas.[schema_id]  
INNER JOIN 
  sys.indexes AS dbindexes ON dbindexes.[object_id] = indexstats.[object_id]  
  AND indexstats.index_id = dbindexes.index_id  
WHERE 
  indexstats.avg_fragmentation_in_percent > 30
  AND indexstats.page_count > 100  
ORDER BY 
  indexstats.avg_fragmentation_in_percent DESC;
```

## 8. Security Audit
**Objective:** Regularly audit security settings and logs to prevent unauthorized access and ensure compliance.

**T-SQL Query:**
```bash
SELECT 
  session_id,
  login_name,
  client_interface_name,
  login_time,
  host_name,
  program_name,
  client_net_address,
  authentication_method,
  server_principal_name,
  error_number,
  is_success
FROM 
  sys.dm_exec_sessions
JOIN 
  sys.dm_audit_login_trail ON sys.dm_exec_sessions.session_id = sys.dm_audit_login_trail.session_id
WHERE 
  login_time > DATEADD(day, -1, GETDATE());  -- Adjust timeframe as needed
```

## 9. Database Growth Tracking
**Objective:** Monitor database size growth to predict future storage needs and prevent storage shortages.

**T-SQL Query:**
```bash
SELECT 
  DB_NAME(database_id) AS DatabaseName,
  CAST(SUM(size) * 8./1024 AS DECIMAL(10,2)) AS DatabaseSizeMB
FROM 
  sys.master_files
GROUP BY 
  database_id
ORDER BY 
  DatabaseSizeMB DESC;
```

## 10. Real-time Query Performance Monitoring
**Objective:** Capture and analyze real-time query performance to identify slow queries and optimize them.

**T-SQL Query:**
```bash
SELECT 
  req.session_id,
  req.start_time,
  req.status,
  req.command,
  req.cpu_time,
  req.total_elapsed_time,
  SUBSTRING(qt.text, (req.statement_start_offset/2) + 1, 
    ((CASE WHEN req.statement_end_offset = -1 
      THEN DATALENGTH(qt.text) 
      ELSE req.statement_end_offset 
    END - req.statement_start_offset)/2) + 1) AS statement_text
FROM 
  sys.dm_exec_requests AS req
CROSS APPLY 
  sys.dm_exec_sql_text(req.sql_handle) AS qt
WHERE 
  req.status = 'running' AND 
  req.total_elapsed_time > 5000  -- Filter to capture queries running longer than 5 seconds
ORDER BY 
  req.cpu_time DESC;
```

## 11. Database Mirroring Monitoring
**Objective:** Monitor database mirroring sessions to ensure they are synchronized and functioning correctly.

**T-SQL Query:**
```bash
SELECT 
  DB_NAME(database_id) AS DatabaseName,
  mirroring_state_desc,
  mirroring_role_desc,
  mirroring_safety_level_desc
FROM 
  sys.database_mirroring
WHERE 
  mirroring_guid IS NOT NULL;
```

## 12. Always On Availability Groups Monitoring
**Objective:** Ensure high availability and disaster recovery by monitoring the health and performance of Always On groups.

**T-SQL Query:**
```bash
SELECT 
  ag.name AS AvailabilityGroupName,
  replica_server_name,
  ars.role_desc,
  ars.operational_state_desc,
  ars.connected_state_desc,
  ars.recovery_health_desc,
  ars.synchronization_health_desc
FROM 
  sys.dm_hadr_availability_replica_states ars
INNER JOIN 
  sys.availability_groups ag 
  ON ars.group_id = ag.group_id
INNER JOIN 
  sys.availability_replicas ar 
  ON ars.replica_id = ar.replica_id;
```

## 13. Transaction Log Monitoring
**Objective:** Monitor the transaction log to ensure it doesn't fill up and affect database operations.

**T-SQL Query:**
```bash
SELECT 
  DB_NAME(database_id) AS DatabaseName,
  name AS LogFileName,
  size/128.0 AS LogSizeMB,
  CAST(FILEPROPERTY(name, 'SpaceUsed') AS INT)/128.0 AS SpaceUsedMB,
  (size - CAST(FILEPROPERTY(name, 'SpaceUsed') AS INT))/128.0 AS AvailableSpaceMB
FROM 
  sys.database_files
WHERE 
  type_desc = 'LOG';
```

## 14. Deadlock Detection
**Objective:** Detect and resolve deadlocks to maintain smooth operation and prevent application errors.

**T-SQL Query:**
```bash
WITH DeadlockEvents AS (
    SELECT 
        XEvent.query('(event/data/value/deadlock)[1]') AS DeadlockGraph,
        XEvent.value('(@timestamp)[1]', 'datetime2') AS TimeOccurred
    FROM 
        (SELECT 
            CAST(event_data AS XML) AS XEvent
         FROM 
            sys.fn_xe_file_target_read_file('system_health*.xel', NULL, NULL, NULL)
        ) AS Data
    WHERE 
        XEvent.value('(@name)[1]', 'varchar(50)') = 'xml_deadlock_report'
)
SELECT 
    TimeOccurred,
    DeadlockGraph
FROM 
    DeadlockEvents
ORDER BY 
    TimeOccurred DESC;
```

## 15. Memory Usage Monitoring
**Objective:** Track SQL Server memory usage to ensure it has sufficient memory for operations and to optimize performance.

**T-SQL Query:**
```bash
SELECT 
  total_physical_memory_kb/1024 AS TotalPhysicalMemoryMB,
  available_physical_memory_kb/1024 AS AvailableMemoryMB,
  total_page_file_kb/1024 AS TotalPageFileMB,
  available_page_file_kb/1024 AS AvailablePageFileMB,
  system_memory_state_desc
FROM 
  sys.dm_os_sys_memory;
```

## 16. Custom Alerts and Notifications
**Objective:** Implement custom alerts for critical issues and performance thresholds to notify administrators immediately.

**T-SQL Query:**

**A** Configure Database Mail:
```bash
EXEC msdb.dbo.sysmail_add_account_sp 
    @account_name='SQLAlerts', 
    @email_address='your-email@example.com',
    @mailserver_name='smtp.example.com'; -- Specify your SMTP server details here

EXEC msdb.dbo.sysmail_add_profile_sp 
    @profile_name='SQLAlertProfile', 
    @description='Profile used for SQL Server alerts';

EXEC msdb.dbo.sysmail_add_profileaccount_sp 
    @profile_name='SQLAlertProfile', 
    @account_name='SQLAlerts', 
    @sequence_number=1;
```
**B** Create SQL Server Agent Jobs:
```bash
-- Assume 'CheckCondition' is a procedure that returns 1 if the condition is met
DECLARE @ConditionMet BIT;
EXEC @ConditionMet = dbo.CheckCondition;

IF @ConditionMet = 1
BEGIN
    EXEC msdb.dbo.sp_send_dbmail
        @profile_name='SQLAlertProfile',
        @recipients='admin@example.com',
        @body='Alert: The condition has been met.',
        @subject='SQL Server Alert';
END;
```
**C** Schedule and Monitor Jobs:
- Use SQL Server Agent to schedule these jobs to run at specific intervals (e.g., every 15 minutes) and to monitor their success or failure.