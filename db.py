import os
from dotenv import load_dotenv
load_dotenv()

def get_db():
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL:
        import psycopg2
        return psycopg2.connect(os.environ["DATABASE_URL"])
    else:
        import sqlite3
        return sqlite3.connect("users.db", check_same_thread=False)

def is_postgres():
    return bool(os.getenv("DATABASE_URL"))

def query_format(query):
    if is_postgres():
        return query.replace("?", "%s")
    return query