import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import os
import json  # Import json for proper handling of JSON

# Load environment variables from .env
load_dotenv(".env")

# Fetch Supabase credentials from environment
USER = os.getenv("SUPABASE_USER")
PASSWORD = os.getenv("SUPABASE_PASSWORD")
HOST = os.getenv("SUPABASE_HOST")
PORT = os.getenv("SUPABASE_PORT")
DBNAME = os.getenv("SUPABASE_DBNAME")


# Connect to the Supabase PostgreSQL database
# Connect to the Supabase PostgreSQL database

try:
    global connection 
    global cursor
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



def insert_period(period, incomes, expenses, comment):
    try:
        # Use psycopg2.extras.Json to handle jsonb data
        incomes_jsonb = psycopg2.extras.Json(incomes)
        expenses_jsonb = psycopg2.extras.Json(expenses)
        
        cursor.execute(
            "INSERT INTO reports (period, incomes, expenses, comment) VALUES (%s, %s, %s, %s)",
            (period, incomes_jsonb, expenses_jsonb, comment)
        )
        connection.commit()
        print(f"✅ Period {period} inserted successfully!")
    except Exception as e:
        print(f"❌ Failed to insert period: {e}")
        connection.rollback()


def fetch_all_periods():
    try:
        cursor.execute("SELECT period FROM reports")
        rows = cursor.fetchall()
        
        print("📌 Raw periods fetched from DB:", rows)  # Debugging
        
        periods = [row[0] for row in rows] if rows else []
        print("✅ Extracted periods:", periods)  # Debugging
        
        return periods
    except Exception as e:
        print(f"❌ Failed to fetch all periods: {e}")
        connection.rollback()
        return []


# Fetch all periods
def get_period(period):
    try:
        print(f"📌 Fetching data for period: {period}")  # Debugging
        
        cursor.execute("SELECT period, incomes, expenses, comment FROM reports WHERE period = %s", (period,))
        result = cursor.fetchone()
        
        print("📌 Raw query result:", result)  # Debugging

        if result:
            incomes = result[1] if result[1] else {}
            expenses = result[2] if result[2] else {}
            comment = result[3] if result[3] else "No comment"

            # Ensure `incomes` and `expenses` are dictionaries
            if not isinstance(incomes, dict):
                print("⚠️ Warning: `incomes` is not a dictionary:", incomes)
                incomes = {}

            if not isinstance(expenses, dict):
                print("⚠️ Warning: `expenses` is not a dictionary:", expenses)
                expenses = {}

            return {
                "period": result[0],
                "incomes": incomes,
                "expenses": expenses,
                "comment": comment,
            }
        else:
            print("❌ No data found for period:", period)
            return None
    except Exception as e:
        print(f"❌ Failed to fetch period: {e}")
        connection.rollback()
        return None

# Data for insertion
#period = "2023_September"
#incomes = {"salary": 5000, "bonus": 1000}
#expenses = {"rent": 1500, "utilities": 300}
#comment = "Monthly report for September 2023"

# Insert, fetch all, and get specific period
#insert_period(period, incomes, expenses, comment)
#   fetch_all_periods()
#get_period(period)

# Close the cursor and connection
#  cursor.close()
#   connection.close()
# print("Connection closed.")
