import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import os
import json  

load_dotenv(".env")

USER = os.getenv("SUPABASE_USER")
PASSWORD = os.getenv("SUPABASE_PASSWORD")
HOST = os.getenv("SUPABASE_HOST")
PORT = os.getenv("SUPABASE_PORT")
DBNAME = os.getenv("SUPABASE_DBNAME")

connection = None
cursor = None


def connect():
    global connection 
    global cursor    
    try:
        connection = psycopg2.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            dbname=DBNAME
        )
        print("Connection to Supabase database successful!")
        cursor = connection.cursor()
    except Exception as e:
        print(f"Database connection error: {e}")
        print(type(e).__name__, e)

connect

def insert_period(period, incomes, expenses, comment):
    global connection 
    global cursor
    try:        
        incomes_jsonb = psycopg2.extras.Json(incomes)
        expenses_jsonb = psycopg2.extras.Json(expenses)
        
        cursor.execute(
            "INSERT INTO reports (period, incomes, expenses, comment) VALUES (%s, %s, %s, %s)",
            (period, incomes_jsonb, expenses_jsonb, comment)
        )
        connection.commit()
        print(f"Period {period} inserted successfully!")
    except Exception as e:
        print(f"Failed to insert period: {e}")
        connection.rollback()

def fetch_all_periods():
    global connection 
    global cursor    
    try:
        cursor.execute("SELECT period FROM reports")
        rows = cursor.fetchall()
        
        print("Raw periods fetched from DB:", rows)  
        
        periods = [row[0] for row in rows] if rows else []
        print("Extracted periods:", periods)  
        
        return periods
    except Exception as e:
        print(f"Failed to fetch all periods: {e}")
        connection.rollback()
        return []

def get_period(period):
    global connection 
    global cursor    
    try:
        print(f"Fetching data for period: {period}")  
        
        cursor.execute("SELECT period, incomes, expenses, comment FROM reports WHERE period = %s", (period,))
        result = cursor.fetchone()
        
        print("Raw query result:", result)  

        if result:
            incomes = result[1] if result[1] else {}
            expenses = result[2] if result[2] else {}
            comment = result[3] if result[3] else "No comment"

            if not isinstance(incomes, dict):
                print("Warning: `incomes` is not a dictionary:", incomes)
                incomes = {}

            if not isinstance(expenses, dict):
                print("Warning: `expenses` is not a dictionary:", expenses)
                expenses = {}

            return {
                "period": result[0],
                "incomes": incomes,
                "expenses": expenses,
                "comment": comment,
            }
        else:
            print("No data found for period:", period)
            return None
    except Exception as e:
        print(f"Failed to fetch period: {e}")
        connection.rollback()
        return None


