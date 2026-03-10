# filepath: /Users/divyanshuraj/Downloads/Synergy/app/employee_manager.py
"""
Employee Manager Module

This module manages all employee-related data in the SQL database.
Provides functions to add, retrieve, update, and list employees.
"""

import sqlite3
from datetime import datetime
from .db_connections import get_sqlite_connection, DB_PATH


class DuplicateEmailError(Exception):
    """Custom exception raised when attempting to add an employee with a duplicate email."""
    pass


class EmployeeNotFoundError(Exception):
    """Custom exception raised when an employee is not found."""
    pass


def add_employee(first_name, last_name, email, hire_date, department, db_path=None):
    """
    Add a new employee to the database.
    
    Args:
        first_name (str): Employee's first name.
        last_name (str): Employee's last name.
        email (str): Employee's email address (must be unique).
        hire_date (str): Date of hiring (format: YYYY-MM-DD).
        department (str): Department name.
        db_path (str, optional): Path to the database file.
    
    Returns:
        int: The employee_id of the newly created employee.
    
    Raises:
        DuplicateEmailError: If an employee with the same email already exists.
        ValueError: If required fields are empty or invalid.
    """
    # Validate input
    if not all([first_name, last_name, email, hire_date, department]):
        raise ValueError("All fields (first_name, last_name, email, hire_date, department) are required.")
    
    # Validate email format (basic check)
    if '@' not in email or '.' not in email:
        raise ValueError("Invalid email format.")
    
    # Validate date format
    try:
        datetime.strptime(hire_date, '%Y-%m-%d')
    except ValueError:
        raise ValueError("hire_date must be in YYYY-MM-DD format.")
    
    conn = get_sqlite_connection(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO Employees (first_name, last_name, email, hire_date, department)
            VALUES (?, ?, ?, ?, ?)
        ''', (first_name.strip(), last_name.strip(), email.strip().lower(), hire_date, department.strip()))
        
        conn.commit()
        employee_id = cursor.lastrowid
        print(f"Employee '{first_name} {last_name}' added successfully with ID: {employee_id}")
        return employee_id
        
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e) or "email" in str(e).lower():
            raise DuplicateEmailError(f"An employee with email '{email}' already exists.")
        raise
    finally:
        conn.close()


def get_employee_by_id(employee_id, db_path=None):
    """
    Retrieve an employee's details by their ID.
    
    Args:
        employee_id (int): The unique identifier of the employee.
        db_path (str, optional): Path to the database file.
    
    Returns:
        dict: A dictionary containing the employee's details.
    
    Raises:
        EmployeeNotFoundError: If no employee with the given ID exists.
    """
    conn = get_sqlite_connection(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT employee_id, first_name, last_name, email, hire_date, department
            FROM Employees
            WHERE employee_id = ?
        ''', (employee_id,))
        
        row = cursor.fetchone()
        
        if row is None:
            raise EmployeeNotFoundError(f"Employee with ID {employee_id} not found.")
        
        return dict(row)
        
    finally:
        conn.close()


def list_all_employees(db_path=None):
    """
    Retrieve a list of all employees from the database.
    
    Args:
        db_path (str, optional): Path to the database file.
    
    Returns:
        list: A list of dictionaries, each containing an employee's details.
    """
    conn = get_sqlite_connection(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT employee_id, first_name, last_name, email, hire_date, department
            FROM Employees
            ORDER BY employee_id
        ''')
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
        
    finally:
        conn.close()


def update_employee(employee_id, first_name=None, last_name=None, email=None, 
                   hire_date=None, department=None, db_path=None):
    """
    Update an employee's details.
    
    Args:
        employee_id (int): The unique identifier of the employee.
        first_name (str, optional): New first name.
        last_name (str, optional): New last name.
        email (str, optional): New email address.
        hire_date (str, optional): New hire date.
        department (str, optional): New department.
        db_path (str, optional): Path to the database file.
    
    Returns:
        bool: True if update was successful.
    
    Raises:
        EmployeeNotFoundError: If no employee with the given ID exists.
        DuplicateEmailError: If the new email already exists.
    """
    # First check if employee exists
    get_employee_by_id(employee_id, db_path)
    
    # Build update query dynamically based on provided fields
    updates = []
    values = []
    
    if first_name is not None:
        updates.append("first_name = ?")
        values.append(first_name.strip())
    if last_name is not None:
        updates.append("last_name = ?")
        values.append(last_name.strip())
    if email is not None:
        if '@' not in email or '.' not in email:
            raise ValueError("Invalid email format.")
        updates.append("email = ?")
        values.append(email.strip().lower())
    if hire_date is not None:
        try:
            datetime.strptime(hire_date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("hire_date must be in YYYY-MM-DD format.")
        updates.append("hire_date = ?")
        values.append(hire_date)
    if department is not None:
        updates.append("department = ?")
        values.append(department.strip())
    
    if not updates:
        return True  # Nothing to update
    
    values.append(employee_id)
    
    conn = get_sqlite_connection(db_path)
    cursor = conn.cursor()
    
    try:
        query = f"UPDATE Employees SET {', '.join(updates)} WHERE employee_id = ?"
        cursor.execute(query, values)
        conn.commit()
        print(f"Employee ID {employee_id} updated successfully.")
        return True
        
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            raise DuplicateEmailError(f"An employee with email '{email}' already exists.")
        raise
    finally:
        conn.close()


def delete_employee(employee_id, db_path=None):
    """
    Delete an employee from the database.
    
    Args:
        employee_id (int): The unique identifier of the employee.
        db_path (str, optional): Path to the database file.
    
    Returns:
        bool: True if deletion was successful.
    
    Raises:
        EmployeeNotFoundError: If no employee with the given ID exists.
    """
    # First check if employee exists
    get_employee_by_id(employee_id, db_path)
    
    conn = get_sqlite_connection(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM Employees WHERE employee_id = ?', (employee_id,))
        conn.commit()
        print(f"Employee ID {employee_id} deleted successfully.")
        return True
        
    finally:
        conn.close()


def search_employees(search_term, db_path=None):
    """
    Search for employees by name, email, or department.
    
    Args:
        search_term (str): The search term to look for.
        db_path (str, optional): Path to the database file.
    
    Returns:
        list: A list of matching employee dictionaries.
    """
    conn = get_sqlite_connection(db_path)
    cursor = conn.cursor()
    
    try:
        search_pattern = f"%{search_term}%"
        cursor.execute('''
            SELECT employee_id, first_name, last_name, email, hire_date, department
            FROM Employees
            WHERE first_name LIKE ? 
               OR last_name LIKE ? 
               OR email LIKE ? 
               OR department LIKE ?
            ORDER BY employee_id
        ''', (search_pattern, search_pattern, search_pattern, search_pattern))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
        
    finally:
        conn.close()
