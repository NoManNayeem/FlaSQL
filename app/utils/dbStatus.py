import socket
from sqlalchemy import create_engine, text
import urllib
import datetime
import sqlalchemy
from ..models import MSSQLConnection  # Adjust the import to your actual model file
from .. import db  # Adjust the import to your actual Flask app

def get_active_connection():
    return MSSQLConnection.query.filter_by(active=True).first()

def connect_to_db():
    # Get the active connection
    active_connection = get_active_connection()

    if active_connection:
        # Get the connection string from the active connection
        connection_str = active_connection.get_connection_string()

        # Create an SQLAlchemy engine
        engine = create_engine(connection_str)

        try:
            # Test the connection and retrieve details
            with engine.connect() as conn:
                # Get server name and version
                server_name = conn.execute(text("SELECT @@servername")).fetchone()[0]
                version = conn.execute(text("SELECT @@version")).fetchone()[0]

                # # Get server IP address
                # server_ip = socket.gethostbyname(server_name)
                server_ip = "127.0.0.0"

                # Get number of users
                users_count = conn.execute(text("SELECT COUNT(*) FROM sys.syslogins")).fetchone()[0]

                # Get number of databases
                databases_count = conn.execute(text("SELECT COUNT(*) FROM sys.databases")).fetchone()[0]

                # Get number of connections
                connections_count = conn.execute(text("SELECT COUNT(*) FROM sys.dm_exec_connections")).fetchone()[0]

                # Fetch recent login events
                recent_login_events = conn.execute(text("""
                    SELECT TOP 10 
                        login_time AS event_time, 
                        'Login' AS event_type, 
                        login_name AS details
                    FROM sys.dm_exec_sessions 
                    ORDER BY login_time DESC
                """)).fetchall()

                # Fetch recent database requests
                recent_db_requests = conn.execute(text("""
                    SELECT TOP 10 
                        start_time AS event_time, 
                        'Database Request' AS event_type, 
                        command AS details
                    FROM sys.dm_exec_requests 
                    ORDER BY start_time DESC
                """)).fetchall()

                # Combine the results
                recent_activities = recent_login_events + recent_db_requests
                recent_activities = sorted(recent_activities, key=lambda x: x.event_time, reverse=True)

                activities = []
                for activity in recent_activities:
                    activities.append({
                        "event_time": activity.event_time,
                        "event_type": activity.event_type,
                        "details": activity.details
                    })

                # Return the details as a dictionary
                return {
                    "server_name": server_name,
                    "server_ip": server_ip,
                    "version": version,
                    "users_count": users_count,
                    "databases_count": databases_count,
                    "connections_count": connections_count,
                    "recent_activities": activities,
                }
        except sqlalchemy.exc.OperationalError as e:
            print(f"Error connecting to the database: {e}")
            return None
    else:
        print("No active MSSQL connection found")
        return None
