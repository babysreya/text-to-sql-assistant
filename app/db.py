import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def get_schema():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]
    schema = ""
    for table in tables:
        cursor.execute(f"DESCRIBE {table}")
        columns = cursor.fetchall()
        cursor.execute(f"""
            SELECT k.COLUMN_NAME, k.REFERENCED_TABLE_NAME, k.REFERENCED_COLUMN_NAME
            FROM information_schema.KEY_COLUMN_USAGE k
            WHERE k.TABLE_SCHEMA = DATABASE()
            AND k.TABLE_NAME = '{table}'
            AND k.REFERENCED_TABLE_NAME IS NOT NULL
        """)
        foreign_keys = cursor.fetchall()
        schema += f"Table: {table}\n"
        schema += "Columns:\n"
        for col in columns:
            schema += f"  - {col[0]} ({col[1]})"
            # flag date columns explicitly
            if 'date' in col[1].lower():
                schema += f"  ← DATE COLUMN, use {table}.{col[0]}"
            schema += "\n"
        if foreign_keys:
            schema += "Foreign Keys:\n"
            for fk in foreign_keys:
                schema += f"  - {table}.{fk[0]} → {fk[1]}.{fk[2]}\n"
        schema += "\n"
    conn.close()
    return schema

def execute_query(sql):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        if sql.strip().upper().startswith("SELECT"):
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            conn.close()
            return columns, rows, None
        else:
            conn.commit()
            conn.close()
            return None, None, f"✅ Done. Rows affected: {cursor.rowcount}"
    except Exception as e:
        conn.close()
        return None, None, f"❌ Error: {str(e)}"