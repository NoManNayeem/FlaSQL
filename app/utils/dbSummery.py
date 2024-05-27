import socket
from sqlalchemy import create_engine, text
import urllib
import datetime
import sqlalchemy

# Connection parameters
server = 'NAYEEMISLAM'
database = 'master'
driver = 'ODBC Driver 17 for SQL Server'

# Properly encode the parameters for the URL
params = urllib.parse.quote_plus(
    f"DRIVER={{{driver}}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"Trusted_Connection=yes;"
)

# Create the connection string for SQLAlchemy
connection_str = f"mssql+pyodbc:///?odbc_connect={params}"

# Create an SQLAlchemy engine
engine = create_engine(connection_str)

def get_ip_address():
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except Exception as e:
        print(f"Error fetching IP address: {e}")
        return "Unknown IP"

def get_Server_Details():
    with engine.connect() as connection:
        try:
            # Fetch databases and their statuses
            result = connection.execute(text("SELECT name, state_desc FROM sys.databases"))
            databases = [{'name': row[0], 'status': row[1]} for row in result]
        except sqlalchemy.exc.SQLAlchemyError as e:
            print(f"Error fetching databases: {e}")
            databases = []

        try:
            # Fetch server load (CPU usage example query)
            load_result = connection.execute(text("""
                SELECT TOP 10
                    record.value('(./Record/@id)[1]', 'int') as id,
                    record.value('(./Record/SchedulerMonitorEvent/SystemHealth/SystemIdle)[1]', 'int') as SystemIdle,
                    record.value('(./Record/SchedulerMonitorEvent/SystemHealth/ProcessUtilization)[1]', 'int') as SQLServerCPUUtilization,
                    100 - record.value('(./Record/SchedulerMonitorEvent/SystemHealth/SystemIdle)[1]', 'int') - record.value('(./Record/SchedulerMonitorEvent/SystemHealth/ProcessUtilization)[1]', 'int') as NonSQLCPUUtilization,
                    timestamp
                FROM (
                    SELECT timestamp, convert(xml, record) as record
                    FROM sys.dm_os_ring_buffers
                    WHERE ring_buffer_type = N'RING_BUFFER_SCHEDULER_MONITOR'
                    AND record LIKE '%<SystemHealth>%'
                ) as RingBufferInfo
                ORDER BY timestamp DESC
            """))
            server_load = [{'time': row[4], 'cpu_usage': row[2], 'idle': row[1], 'other_usage': row[3]} for row in load_result]
        except sqlalchemy.exc.SQLAlchemyError as e:
            print(f"Error fetching server load: {e}")
            server_load = []

        try:
            # Fetch recent queries (example query)
            queries_result = connection.execute(text("""
                SELECT TOP 5 
                    SUBSTRING(st.text, (qs.statement_start_offset / 2) + 1, 
                    ((CASE statement_end_offset 
                        WHEN -1 THEN DATALENGTH(st.text) 
                        ELSE qs.statement_end_offset END 
                        - qs.statement_start_offset) / 2) + 1) AS query_text,
                    qs.execution_count,
                    qs.total_logical_reads, 
                    qs.total_worker_time,
                    qs.total_elapsed_time
                FROM sys.dm_exec_query_stats AS qs
                CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) AS st
                ORDER BY qs.total_elapsed_time DESC
            """))
            recent_queries = [{'query_text': row[0], 'execution_count': row[1], 'total_logical_reads': row[2], 'total_worker_time': row[3], 'total_elapsed_time': row[4]} for row in queries_result]
        except sqlalchemy.exc.SQLAlchemyError as e:
            print(f"Error fetching recent queries: {e}")
            recent_queries = []

        try:
            # Fetch server uptime
            uptime_result = connection.execute(text("SELECT sqlserver_start_time FROM sys.dm_os_sys_info"))
            uptime = next(uptime_result)[0]
            uptime_duration = datetime.datetime.now() - uptime
        except sqlalchemy.exc.SQLAlchemyError as e:
            print(f"Error fetching server uptime: {e}")
            uptime_duration = "N/A"

        try:
            # Fetch SQL Server version
            version_result = connection.execute(text("SELECT @@VERSION"))
            version = next(version_result)[0]
        except sqlalchemy.exc.SQLAlchemyError as e:
            print(f"Error fetching SQL Server version: {e}")
            version = "N/A"

        try:
            # Fetch last backup time
            last_backup_result = connection.execute(text("""
                SELECT TOP 1 
                    backup_finish_date 
                FROM msdb.dbo.backupset 
                WHERE type = 'D' 
                ORDER BY backup_finish_date DESC
            """))
            last_backup = next(last_backup_result, None)
            if last_backup:
                last_backup = last_backup[0]
            else:
                last_backup = "No backups found"
        except sqlalchemy.exc.SQLAlchemyError as e:
            print(f"Error fetching last backup time: {e}")
            last_backup = "N/A"

        try:
            # Fetch recent alerts (example query, replace with actual logic)
            recent_alerts_result = connection.execute(text("""
                SELECT COUNT(*) 
                FROM msdb.dbo.sysalerts 
                WHERE last_occurrence_date >= CONVERT(datetime, GETDATE())
            """))
            recent_alerts = next(recent_alerts_result)[0]
        except sqlalchemy.exc.SQLAlchemyError as e:
            print(f"Error fetching recent alerts: {e}")
            recent_alerts = 0

        try:
            # Fetch next maintenance time (placeholder, replace with actual query if available)
            next_maintenance = "No scheduled maintenance found"
            # Uncomment and replace with actual query if you have a maintenance schedule table
            # next_maintenance_result = connection.execute(text("""
            #     SELECT TOP 1 
            #         maintenance_start_time 
            #     FROM your_maintenance_schedule_table 
            #     WHERE maintenance_start_time > GETDATE()
            #     ORDER BY maintenance_start_time ASC
            # """))
            # next_maintenance = next(next_maintenance_result, None)
            # if next_maintenance:
            #     next_maintenance = next_maintenance[0]
            # else:
            #     next_maintenance = "No scheduled maintenance found"
        except sqlalchemy.exc.SQLAlchemyError as e:
            print(f"Error fetching next maintenance time: {e}")
            next_maintenance = "N/A"

        try:
            # Determine performance (example logic)
            cpu_usage = sum([item['cpu_usage'] for item in server_load]) / len(server_load) if server_load else 0
            performance = 'Good' if cpu_usage < 70 else 'Moderate' if cpu_usage < 90 else 'High'
        except Exception as e:
            print(f"Error determining performance: {e}")
            performance = "N/A"

        # Example server metrics
        metrics = {
            'server_name': server,
            'ip_address': get_ip_address(),
            'uptime': str(uptime_duration),
            'version': version,
            'last_backup': last_backup,
            'next_maintenance': next_maintenance,
            'active_databases': len(databases),
            'databases': databases,
            'recent_alerts': recent_alerts,
            'performance': performance,
            'server_load': server_load,
            'recent_queries': recent_queries
        }
        return metrics
