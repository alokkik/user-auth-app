import psycopg2
from psycopg2.extensions import connection as pg_connection

DATABASE_URL = "postgresql://postgres@localhost:5432/postgres"

# Function to create the "users" table
def create_users_table(conn: pg_connection):
    # SQL statement to create the "users" table
    create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    """
    # Execute the SQL statement
    with conn.cursor() as cursor:
        cursor.execute(create_table_query)
    conn.commit()

def get_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn