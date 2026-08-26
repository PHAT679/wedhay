"""
Database connection pool and helper utilities
"""

# import pyodbc
from flask import current_app, g
from config import Config


def get_connection_string():
    """Build SQL Server connection string"""
    cfg = Config()
    if cfg.SQL_TRUSTED_CONNECTION == 'yes':
        return (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={cfg.SQL_SERVER};"
            f"DATABASE={cfg.SQL_DATABASE};"
            f"Trusted_Connection=yes;"
        )
    else:
        return (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={cfg.SQL_SERVER};"
            f"DATABASE={cfg.SQL_DATABASE};"
            f"UID={cfg.SQL_USERNAME};"
            f"PWD={cfg.SQL_PASSWORD};"
        )


def get_db():
    """Get database connection from Flask g object (per-request)"""
    if 'db' not in g:
        g.db = pyodbc.connect(get_connection_string())
    return g.db


def close_db(e=None):
    """Close database connection at end of request"""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def execute_query(sql, params=None, fetch=True):
    """Execute a SELECT query and return results as list of dicts"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        
        if fetch:
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        else:
            conn.commit()
            return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()


def execute_sp(sp_name, params=None, fetch=False):
    """Execute a stored procedure"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        if params:
            placeholders = ', '.join(['?' for _ in params])
            sql = f"EXEC {sp_name} {placeholders}"
            cursor.execute(sql, params)
        else:
            cursor.execute(f"EXEC {sp_name}")
        
        if fetch:
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                conn.commit()
                return [dict(zip(columns, row)) for row in rows]
            conn.commit()
            return []
        else:
            conn.commit()
            return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()


# Module-level pool placeholder (used in app.py import)
db_pool = None
