from sqlalchemy import create_engine
import urllib
import pandas as pd

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

def get_server_metrics():
    try:
        server_metrics = {}

        # Server Info
        query_server_info = """
        SELECT 
            @@SERVERNAME AS ServerName, 
            CAST(SERVERPROPERTY('Edition') AS VARCHAR(255)) AS Edition, 
            CAST(SERVERPROPERTY('ProductVersion') AS VARCHAR(255)) AS Version;
        """
        server_info = pd.read_sql(query_server_info, engine)
        server_metrics['ServerName'] = server_info.iloc[0]['ServerName']
        server_metrics['ServerEdition'] = server_info.iloc[0]['Edition']
        server_metrics['ServerVersion'] = server_info.iloc[0]['Version']

        # Disk Space
        query_disk_space = """
        SELECT DB_NAME(database_id) AS DatabaseName,
               SUM(size * 8 / 1024) AS TotalSpaceMB,
               SUM(size * 8 / 1024) - SUM(FILEPROPERTY(name, 'SpaceUsed') * 8 / 1024) AS EmptySpaceMB
        FROM sys.master_files
        GROUP BY database_id;
        """
        disk_space = pd.read_sql(query_disk_space, engine)
        server_metrics['DiskSpace'] = disk_space.to_dict('records')

        # Database Connections
        query_connections = """
        SELECT DB_NAME(dbid) as DatabaseName, COUNT(dbid) as NumberOfConnections FROM sys.sysprocesses WHERE dbid > 0 GROUP BY dbid;
        """
        connections = pd.read_sql(query_connections, engine)
        server_metrics['DatabaseConnections'] = connections.to_dict('records')

        # Network Traffic
        query_network_traffic = """
        SELECT 
          SUM(num_of_reads) AS TotalReads, 
          SUM(num_of_writes) AS TotalWrites
        FROM sys.dm_io_virtual_file_stats(null, null);
        """
        network_traffic = pd.read_sql(query_network_traffic, engine)
        server_metrics['NetworkTraffic'] = network_traffic.to_dict('index')[0]

        return server_metrics

    except Exception as e:
        print("Error:", str(e))
        return {"error": str(e)}

# # Fetch server metrics
# server_metrics = get_server_metrics()
# print(server_metrics)
