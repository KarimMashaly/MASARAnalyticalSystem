from supabase import create_client
import pandas as pd
import psycopg2
# import socket
# import sys
# import traceback


url = "https://oeezpsqvyelbjupmalra.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9lZXpzcXZlWVsYmp1cG1hbHJhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjgwMzQ4NSwiZXhwIjoyMDkyMzc5NDg1fQ.w7tk5zWnhEqoMmpxxv5lMWCcHmrLiXpAvJrSfslt8S4"
host = "aws-0-eu-west-1.pooler.supabase.com"
password="WEFTRZkac#rEF56"

import psycopg2
import pandas as pd
import os

os.makedirs("Data", exist_ok=True)

conn = psycopg2.connect(
    host="aws-0-eu-west-1.pooler.supabase.com",
    database="postgres",
    user="postgres.oeezpsqvyelbjupmalra",
    password= password,
    port="6543",
    sslmode="require"
)

# 🔴 CHANGE THIS LINE ONLY
query = "SELECT * FROM  user_assessments"   # <-- replace with your actual table name

df = pd.read_sql(query, conn)

df.to_csv("Data/UserResponse.csv", index=False, encoding="utf-8")

conn.close()

print("Done")