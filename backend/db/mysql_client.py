import os
import mysql.connector
from mysql.connector import Error


def get_connection():
    """Return a new MySQL connection using XAMPP defaults.

    Adjust host/user/password/database if you changed your XAMPP setup.
    """
    return mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST", "localhost"),
        user=os.environ.get("MYSQL_USER", "root"),
        password=os.environ.get("MYSQL_PASSWORD", ""),
        database=os.environ.get("MYSQL_DATABASE", "opcua_monitor"),
    )
