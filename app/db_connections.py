"""
Database Connection Module

This module handles all database connectivity for both SQLite (SQL) and MongoDB (NoSQL).
- SQLite: Used for structured employee and project data
- MongoDB: Used for semi-structured performance review data
"""

import sqlite3
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# Database paths and configurations
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'company.db')
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
MONGO_DB_NAME = 'performance_reviews_db'


# ==================== SQLite Connection ====================

def get_sqlite_connection(db_path=None):
    """
    Establish a connection to the SQLite database.
    
    Args:
        db_path: Optional path to the database file. Uses default if not provided.
    
    Returns:
        sqlite3.Connection: A connection object to the SQLite database.
    """
    if db_path is None:
        db_path = DB_PATH
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
    return conn


def initialize_sql_database(db_path=None):
    """
    Initialize the SQLite database with required tables.
    Creates tables only if they do not already exist.
    
    Tables created:
    - Employees: Stores employee information
    - Projects: Stores project information
    - EmployeeProjects: Junction table linking employees to projects
    """
    conn = get_sqlite_connection(db_path)
    cursor = conn.cursor()
    
    try:
        # Create Employees table
        # Rationale for constraints:
        # - employee_id: INTEGER PRIMARY KEY for auto-increment and fast lookups
        # - email: UNIQUE to prevent duplicate employee records
        # - NOT NULL on required fields to ensure data integrity
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Employees (
                employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                hire_date TEXT NOT NULL,
                department TEXT NOT NULL
            )
        ''')
        
        # Create Projects table
        # Rationale for constraints:
        # - project_id: INTEGER PRIMARY KEY for auto-increment
        # - end_date: Nullable since projects may not have defined end dates
        # - status: DEFAULT value for convenience
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Projects (
                project_id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT,
                status TEXT NOT NULL DEFAULT 'Planning'
            )
        ''')
        
        # Create EmployeeProjects junction table
        # Rationale for constraints:
        # - FOREIGN KEYs ensure referential integrity
        # - ON DELETE CASCADE: When employee/project is deleted, remove assignments
        # - assignment_date defaults to current date for convenience
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS EmployeeProjects (
                assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                project_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                assignment_date TEXT NOT NULL DEFAULT CURRENT_DATE,
                FOREIGN KEY (employee_id) REFERENCES Employees(employee_id) ON DELETE CASCADE,
                FOREIGN KEY (project_id) REFERENCES Projects(project_id) ON DELETE CASCADE,
                UNIQUE(employee_id, project_id)
            )
        ''')
        
        conn.commit()
        print("SQL database initialized successfully.")
        
    except sqlite3.Error as e:
        print(f"Error initializing SQL database: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


# ==================== MongoDB Connection ====================

def get_mongo_client():
    """
    Establish a connection to MongoDB.
    
    Returns:
        MongoClient: A MongoDB client object.
    
    Raises:
        ConnectionFailure: If unable to connect to MongoDB.
    """
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Verify connection
        client.admin.command('ping')
        return client
    except ConnectionFailure as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise


def get_reviews_collection(client=None):
    """
    Get the reviews collection from MongoDB.
    
    Args:
        client: Optional MongoClient. Creates new connection if not provided.
    
    Returns:
        Collection: The reviews collection from MongoDB.
    """
    if client is None:
        client = get_mongo_client()
    
    db = client[MONGO_DB_NAME]
    return db['reviews']


def initialize_mongo_database():
    """
    Initialize the MongoDB database.
    Creates the database and collection if they don't exist.
    Sets up indexes for efficient querying.
    """
    try:
        client = get_mongo_client()
        db = client[MONGO_DB_NAME]
        
        # Create the reviews collection if it doesn't exist
        if 'reviews' not in db.list_collection_names():
            db.create_collection('reviews')
        
        # Create index on employee_id for faster queries
        reviews = db['reviews']
        reviews.create_index('employee_id')
        reviews.create_index('review_date')
        
        print("MongoDB database initialized successfully.")
        client.close()
        
    except ConnectionFailure as e:
        print(f"Warning: Could not initialize MongoDB: {e}")
        print("Performance reviews will not be available until MongoDB is connected.")


def close_mongo_client(client):
    """
    Close the MongoDB client connection.
    
    Args:
        client: The MongoClient to close.
    """
    if client:
        client.close()


# ==================== Initialization ====================

def initialize_all_databases():
    """
    Initialize both SQL and NoSQL databases.
    Call this function at application startup.
    """
    print("Initializing databases...")
    initialize_sql_database()
    try:
        initialize_mongo_database()
    except ConnectionFailure:
        print("MongoDB initialization skipped. Please ensure MongoDB is running.")


if __name__ == "__main__":
    # Test database initialization
    initialize_all_databases()
