import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def run_query(sql_query):
    conn = get_connection()  #connects to sql db
    cursor = conn.cursor()   #creates a cursor for executing sql
    cursor.execute(sql_query) 
    result = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    
    return columns, result
