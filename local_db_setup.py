#!/usr/bin/env python3


import os
import sys
import psycopg2
from getpass import getpass
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database(db_name, db_user, db_password, db_host='localhost', db_port=5443):
    """Create a PostgreSQL database if it doesn't exist."""
    try:
        
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Creating database {db_name}...")
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"Database {db_name} created successfully!")
        else:
            print(f"Database {db_name} already exists.")
        
        cursor.close()
        conn.close()
        
        return True
    except Exception as e:
        print(f"Error creating database: {e}")
        return False

def setup_database_schema(db_name, db_user, db_password, db_host='localhost', db_port=5443):
    """Set up the database schema using the SQL script."""
    try:
        # Connect to the newly created database
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        cursor = conn.cursor()
        
        # Read and execute the SQL script
        with open('database_init.sql', 'r') as f:
            sql_script = f.read()
            cursor.execute(sql_script)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("Database schema created successfully!")
        return True
    except Exception as e:
        print(f"Error setting up database schema: {e}")
        return False

def create_env_file(db_name, db_user, db_password, db_host='localhost', db_port=5443):
    """Create a .env file with database connection information."""
    try:
        db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        
        with open('.env', 'w') as f:
            f.write(f"DATABASE_URL={db_url}\n")
            f.write(f"PGDATABASE={db_name}\n")
            f.write(f"PGUSER={db_user}\n")
            f.write(f"PGPASSWORD={db_password}\n")
            f.write(f"PGHOST={db_host}\n")
            f.write(f"PGPORT={db_port}\n")
            f.write("SESSION_SECRET=your_secret_key_here\n")
        
        print(".env file created with database connection information.")
        return True
    except Exception as e:
        print(f"Error creating .env file: {e}")
        return False

def main():
    print("===== MindfulConnect Local Database Setup =====")
    print("This script will help you set up a local PostgreSQL database for development.")
    print("Make sure PostgreSQL is installed and running on your system.")
    
    # Get database connection information
    db_name = "mindfulconnect"
    db_user ="postgres"
    if not db_user:
        print("Error: Username is required.")
        sys.exit(1)
    
    db_password ="1234"
    db_host = "localhost"
    db_port = "5443"
    
    # Create database
    if not create_database(db_name, db_user, db_password, db_host, db_port):
        sys.exit(1)
    
    # Set up database schema
    if not setup_database_schema(db_name, db_user, db_password, db_host, db_port):
        sys.exit(1)
    
    # Create .env file
    if not create_env_file(db_name, db_user, db_password, db_host, db_port):
        sys.exit(1)
    
    print("\n===== Setup Complete =====")
    print("Your local database has been set up successfully!")
    print("To connect to your database in the application:")
    print("1. Make sure to load environment variables from the .env file")
    print("2. The application will use the DATABASE_URL environment variable")
    print("\nHappy coding!")

if __name__ == "__main__":
    main()