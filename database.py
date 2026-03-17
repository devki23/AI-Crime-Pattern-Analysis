import mysql.connector
import os
from mysql.connector.conversion import MySQLConverter
from dotenv import load_dotenv

load_dotenv()

class StringConverter(MySQLConverter):
    def _DATETIME_to_python(self, value, dsc=None):
        return value.decode('utf-8') if isinstance(value, bytes) else str(value)
        
    def _TIMESTAMP_to_python(self, value, dsc=None):
        return value.decode('utf-8') if isinstance(value, bytes) else str(value)
        
    def _DECIMAL_to_python(self, value, dsc=None):
        return float(value)
        
    def _NEWDECIMAL_to_python(self, value, dsc=None):
        return float(value)

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DB', 'crime_db'),
            auth_plugin='mysql_native_password',
            converter_class=StringConverter
        )
        print(f"DEBUG: Connected to MySQL database '{os.getenv('MYSQL_DB', 'crime_db')}'")
        return connection
    except Exception as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def init_db():
    # Connect without database first to ensure the database exists
    try:
        conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            auth_plugin='mysql_native_password'
        )
        cursor = conn.cursor()
        
        # Open and execute schema.sql
        with open('schema.sql', 'r') as f:
            schema_sql = f.read()
            
            # Since schema.sql already contains CREATE DATABASE and USE statements
            # we just need to split and execute
            commands = schema_sql.split(';')
            for command in commands:
                command = command.strip()
                if command:
                    cursor.execute(command)
                    
        conn.commit()
        print("MySQL Database and tables initialized successfully.")
    except Exception as e:
        print(f"Error initializing MySQL database: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
