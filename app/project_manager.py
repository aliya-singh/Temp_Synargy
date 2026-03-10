# project manager file
# handles project stuff

import sqlite3
from datetime import datetime, date
from .db_connections import get_sqlite_connection, DB_PATH


# custom exceptions
class ProjectNotFoundError(Exception):
    pass


class AssignmentError(Exception):
    pass


# function to add new project
def add_project(project_name, start_date, end_date=None, status='Planning', db_path=None):
    # check if project name is empty
    if project_name == "" or project_name == None:
        raise ValueError("Project name is required.")
    if start_date == "" or start_date == None:
        raise ValueError("Start date is required.")
    
    # check date format
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    except:
        raise ValueError("start_date must be in YYYY-MM-DD format.")
    
    # validate end date if provided
    if end_date != None and end_date != "":
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            if end_dt < start_dt:
                raise ValueError("end_date cannot be before start_date.")
        except ValueError as e:
            if "end_date cannot be before" in str(e):
                raise
            raise ValueError("end_date must be in YYYY-MM-DD format.")
    
    # check status is valid
    valid_statuses = ['Planning', 'In Progress', 'On Hold', 'Completed', 'Cancelled']
    if status not in valid_statuses:
        raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
    
    conn = get_sqlite_connection(db_path)
    cursor = conn.cursor()
    
    try:
        # insert into database
        cursor.execute('''
            INSERT INTO Projects (project_name, start_date, end_date, status)
            VALUES (?, ?, ?, ?)
        ''', (project_name.strip(), start_date, end_date, status))
        
        conn.commit()
        project_id = cursor.lastrowid
        print(f"Project '{project_name}' added successfully with ID: {project_id}")
        return project_id
        
    except sqlite3.Error as e:
        print(f"Error adding project: {e}")
        raise
    finally:
        conn.close()


def get_project_by_id(project_id, db_path=None):
    # get project details from database
    conn = get_sqlite_connection(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT project_id, project_name, start_date, end_date, status
            FROM Projects
            WHERE project_id = ?
        ''', (project_id,))
        
        row = cursor.fetchone()
        
        if row == None:
            raise ProjectNotFoundError(f"Project with ID {project_id} not found.")
        
        return dict(row)
        
    finally:
        conn.close()


def list_all_projects(db_path=None):
    # returns all projects
    conn = get_sqlite_connection(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT project_id, project_name, start_date, end_date, status
            FROM Projects
            ORDER BY project_id
        ''')
        
        rows = cursor.fetchall()
        projects = []
        for row in rows:
            projects.append(dict(row))
        return projects
        
    finally:
        conn.close()


def assign_employee_to_project(employee_id, project_id, role, assignment_date=None, db_path=None):
    # assign employee to project
    if role == "" or role == None:
        raise ValueError("Role is required.")
    
    # if no date provided use today
    if assignment_date == None:
        assignment_date = date.today().strftime('%Y-%m-%d')
    else:
        try:
            datetime.strptime(assignment_date, '%Y-%m-%d')
        except:
            raise ValueError("assignment_date must be in YYYY-MM-DD format.")
    
    conn = get_sqlite_connection(db_path)
    cursor = conn.cursor()
    
    try:
        # check if employee exists
        cursor.execute('SELECT employee_id FROM Employees WHERE employee_id = ?', (employee_id,))
        emp = cursor.fetchone()
        if emp == None:
            raise AssignmentError(f"Employee with ID {employee_id} not found.")
        
        # check if project exists
        cursor.execute('SELECT project_id FROM Projects WHERE project_id = ?', (project_id,))
        proj = cursor.fetchone()
        if proj == None:
            raise AssignmentError(f"Project with ID {project_id} not found.")
        
        # insert assignment
        cursor.execute('''
            INSERT INTO EmployeeProjects (employee_id, project_id, role, assignment_date)
            VALUES (?, ?, ?, ?)
        ''', (employee_id, project_id, role.strip(), assignment_date))
        
        conn.commit()
        assignment_id = cursor.lastrowid
        print(f"Employee {employee_id} assigned to project {project_id} as '{role}'.")
        return assignment_id
        
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            raise AssignmentError(f"Employee {employee_id} is already assigned to project {project_id}.")
        if "FOREIGN KEY constraint failed" in str(e):
            raise AssignmentError("Invalid employee or project ID.")
        raise
    finally:
        conn.close()


def remove_employee_from_project(employee_id, project_id, db_path=None):
    # remove employee from project
    conn = get_sqlite_connection(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            DELETE FROM EmployeeProjects
            WHERE employee_id = ? AND project_id = ?
        ''', (employee_id, project_id))
        
        if cursor.rowcount == 0:
            raise AssignmentError(f"No assignment found for employee {employee_id} on project {project_id}.")
        
        conn.commit()
        print(f"Employee {employee_id} removed from project {project_id}.")
        return True
        
    finally:
        conn.close()


def get_projects_for_employee(employee_id, db_path=None):
    # get all projects for an employee
    conn = get_sqlite_connection(db_path)
    cursor = conn.cursor()
    
    try:
        # check employee exists
        cursor.execute('SELECT employee_id FROM Employees WHERE employee_id = ?', (employee_id,))
        if cursor.fetchone() == None:
            from .employee_manager import EmployeeNotFoundError
            raise EmployeeNotFoundError(f"Employee with ID {employee_id} not found.")
        
        # get projects
        cursor.execute('''
            SELECT 
                p.project_id,
                p.project_name,
                p.start_date,
                p.end_date,
                p.status,
                ep.role,
                ep.assignment_date
            FROM Projects p
            INNER JOIN EmployeeProjects ep ON p.project_id = ep.project_id
            WHERE ep.employee_id = ?
            ORDER BY ep.assignment_date DESC
        ''', (employee_id,))
        
        rows = cursor.fetchall()
        result = []
        for row in rows:
            result.append(dict(row))
        return result
        
    finally:
        conn.close()


def get_employees_for_project(project_id, db_path=None):
    # get all employees on a project
    conn = get_sqlite_connection(db_path)
    cursor = conn.cursor()
    
    try:
        # check project exists
        get_project_by_id(project_id, db_path)
        
        # get employees
        cursor.execute('''
            SELECT 
                e.employee_id,
                e.first_name,
                e.last_name,
                e.email,
                e.department,
                ep.role,
                ep.assignment_date
            FROM Employees e
            INNER JOIN EmployeeProjects ep ON e.employee_id = ep.employee_id
            WHERE ep.project_id = ?
            ORDER BY ep.assignment_date
        ''', (project_id,))
        
        rows = cursor.fetchall()
        employees = []
        for row in rows:
            employees.append(dict(row))
        return employees
        
    finally:
        conn.close()


def update_project(project_id, project_name=None, start_date=None, 
                  end_date=None, status=None, db_path=None):
    # update project details
    
    # check if project exists first
    get_project_by_id(project_id, db_path)
    
    # build update query
    updates = []
    values = []
    
    if project_name != None:
        updates.append("project_name = ?")
        values.append(project_name.strip())
    if start_date != None:
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
        except:
            raise ValueError("start_date must be in YYYY-MM-DD format.")
        updates.append("start_date = ?")
        values.append(start_date)
    if end_date != None:
        try:
            datetime.strptime(end_date, '%Y-%m-%d')
        except:
            raise ValueError("end_date must be in YYYY-MM-DD format.")
        updates.append("end_date = ?")
        values.append(end_date)
    if status != None:
        valid_statuses = ['Planning', 'In Progress', 'On Hold', 'Completed', 'Cancelled']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        updates.append("status = ?")
        values.append(status)
    
    if len(updates) == 0:
        return True  # nothing to update
    
    values.append(project_id)
    
    conn = get_sqlite_connection(db_path)
    cursor = conn.cursor()
    
    try:
        query = f"UPDATE Projects SET {', '.join(updates)} WHERE project_id = ?"
        cursor.execute(query, values)
        conn.commit()
        print(f"Project ID {project_id} updated successfully.")
        return True
        
    finally:
        conn.close()


def delete_project(project_id, db_path=None):
    """
    Delete a project from the database.
    
    Note: Due to CASCADE delete, all employee assignments to this project
    will also be removed.
    
    Args:
        project_id (int): The unique identifier of the project.
        db_path (str, optional): Path to the database file.
    
    Returns:
        bool: True if deletion was successful.
    
    Raises:
        ProjectNotFoundError: If no project with the given ID exists.
    """
    # First check if project exists
    get_project_by_id(project_id, db_path)
    
    conn = get_sqlite_connection(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM Projects WHERE project_id = ?', (project_id,))
        conn.commit()
        print(f"Project ID {project_id} deleted successfully.")
        return True
        
    finally:
        conn.close()