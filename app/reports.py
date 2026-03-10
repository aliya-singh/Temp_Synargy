"""
Reports Module

This module generates various reports combining data from both SQL and NoSQL databases.
Provides formatted reports on employee-project assignments and performance summaries.
"""

from datetime import datetime
from .db_connections import get_sqlite_connection
from .employee_manager import get_employee_by_id, list_all_employees, EmployeeNotFoundError
from .project_manager import get_projects_for_employee, list_all_projects
from .performance_reviewer import (
    get_performance_reviews_for_employee,
    get_average_rating_for_employee,
    get_all_strengths_for_employee,
    get_all_areas_for_improvement_for_employee,
    MongoDBConnectionError
)


def generate_employee_project_report(db_path=None):
    """
    Generate a formatted report of all employee-project assignments.
    
    Combines data from Employees, Projects, and EmployeeProjects tables
    using JOIN queries.
    
    Args:
        db_path (str, optional): Path to the database file.
    
    Returns:
        str: A formatted report string.
    """
    conn = get_sqlite_connection(db_path)
    cursor = conn.cursor()
    
    try:
        # Join query to get all assignments with employee and project details
        cursor.execute('''
            SELECT 
                e.first_name || ' ' || e.last_name AS employee_name,
                e.department,
                p.project_name,
                p.status AS project_status,
                ep.role,
                ep.assignment_date
            FROM EmployeeProjects ep
            INNER JOIN Employees e ON ep.employee_id = e.employee_id
            INNER JOIN Projects p ON ep.project_id = p.project_id
            ORDER BY e.last_name, e.first_name, ep.assignment_date
        ''')
        
        rows = cursor.fetchall()
        
        # Generate formatted report
        report_lines = []
        report_lines.append("=" * 100)
        report_lines.append("EMPLOYEE-PROJECT ASSIGNMENTS REPORT")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("=" * 100)
        report_lines.append("")
        
        if not rows:
            report_lines.append("No employee-project assignments found.")
        else:
            # Header
            header = f"{'Employee Name':<25} | {'Department':<15} | {'Project Name':<20} | {'Role':<15} | {'Status':<12} | {'Assigned Date':<12}"
            report_lines.append(header)
            report_lines.append("-" * 100)
            
            # Data rows
            for row in rows:
                line = f"{row['employee_name']:<25} | {row['department']:<15} | {row['project_name']:<20} | {row['role']:<15} | {row['project_status']:<12} | {row['assignment_date']:<12}"
                report_lines.append(line)
        
        report_lines.append("")
        report_lines.append(f"Total Assignments: {len(rows)}")
        report_lines.append("=" * 100)
        
        report = "\n".join(report_lines)
        print(report)
        return report
        
    finally:
        conn.close()


def generate_employee_performance_summary(employee_id, db_path=None):
    """
    Generate a comprehensive performance summary for an employee.
    
    Combines:
    - Employee details from SQL database
    - Performance reviews from NoSQL database (MongoDB)
    
    Args:
        employee_id (int): The employee's unique identifier.
        db_path (str, optional): Path to the database file.
    
    Returns:
        str: A formatted performance summary string.
    
    Raises:
        EmployeeNotFoundError: If the employee doesn't exist.
    """
    # Get employee details from SQL
    employee = get_employee_by_id(employee_id, db_path)
    
    # Get projects for the employee
    try:
        projects = get_projects_for_employee(employee_id, db_path)
    except Exception:
        projects = []
    
    # Generate report header
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("EMPLOYEE PERFORMANCE SUMMARY")
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 80)
    report_lines.append("")
    
    # Employee Information
    report_lines.append("EMPLOYEE INFORMATION")
    report_lines.append("-" * 40)
    report_lines.append(f"Name: {employee['first_name']} {employee['last_name']}")
    report_lines.append(f"Email: {employee['email']}")
    report_lines.append(f"Department: {employee['department']}")
    report_lines.append(f"Hire Date: {employee['hire_date']}")
    report_lines.append("")
    
    # Project Assignments
    report_lines.append("PROJECT ASSIGNMENTS")
    report_lines.append("-" * 40)
    if projects:
        for project in projects:
            report_lines.append(f"  • {project['project_name']} - {project['role']} ({project['status']})")
    else:
        report_lines.append("  No project assignments.")
    report_lines.append("")
    
    # Try to get performance data from MongoDB
    try:
        reviews = get_performance_reviews_for_employee(employee_id)
        rating_summary = get_average_rating_for_employee(employee_id)
        strengths = get_all_strengths_for_employee(employee_id)
        areas_for_improvement = get_all_areas_for_improvement_for_employee(employee_id)
        
        # Performance Overview
        report_lines.append("PERFORMANCE OVERVIEW")
        report_lines.append("-" * 40)
        
        if rating_summary['review_count'] > 0:
            report_lines.append(f"Total Reviews: {rating_summary['review_count']}")
            report_lines.append(f"Average Rating: {rating_summary['average_rating']:.2f} / 5.00")
            report_lines.append(f"Rating Range: {rating_summary['min_rating']:.1f} - {rating_summary['max_rating']:.1f}")
        else:
            report_lines.append("No performance reviews on record.")
        report_lines.append("")
        
        # Key Strengths
        report_lines.append("KEY STRENGTHS")
        report_lines.append("-" * 40)
        if strengths:
            for s in strengths[:5]:  # Top 5 strengths
                report_lines.append(f"  • {s['strength']} (mentioned {s['count']} time(s))")
        else:
            report_lines.append("  No strengths recorded.")
        report_lines.append("")
        
        # Areas for Improvement
        report_lines.append("AREAS FOR IMPROVEMENT")
        report_lines.append("-" * 40)
        if areas_for_improvement:
            for a in areas_for_improvement[:5]:  # Top 5 areas
                report_lines.append(f"  • {a['area']} (mentioned {a['count']} time(s))")
        else:
            report_lines.append("  No areas for improvement recorded.")
        report_lines.append("")
        
        # Recent Reviews
        report_lines.append("RECENT REVIEWS")
        report_lines.append("-" * 40)
        if reviews:
            for review in reviews[:3]:  # Last 3 reviews
                report_lines.append(f"  Date: {review['review_date']} | Rating: {review['overall_rating']}/5 | Reviewer: {review['reviewer_name']}")
                if review.get('comments'):
                    report_lines.append(f"    Comments: {review['comments'][:100]}...")
        else:
            report_lines.append("  No reviews found.")
        
    except MongoDBConnectionError:
        report_lines.append("PERFORMANCE DATA")
        report_lines.append("-" * 40)
        report_lines.append("  [MongoDB unavailable - Performance data could not be retrieved]")
    
    report_lines.append("")
    report_lines.append("=" * 80)
    
    report = "\n".join(report_lines)
    print(report)
    return report


def generate_department_summary(department=None, db_path=None):
    """
    Generate a summary report for a department or all departments.
    
    Args:
        department (str, optional): Specific department name. If None, all departments.
        db_path (str, optional): Path to the database file.
    
    Returns:
        str: A formatted department summary.
    """
    conn = get_sqlite_connection(db_path)
    cursor = conn.cursor()
    
    try:
        if department:
            cursor.execute('''
                SELECT department, COUNT(*) as employee_count
                FROM Employees
                WHERE department = ?
                GROUP BY department
            ''', (department,))
        else:
            cursor.execute('''
                SELECT department, COUNT(*) as employee_count
                FROM Employees
                GROUP BY department
                ORDER BY employee_count DESC
            ''')
        
        rows = cursor.fetchall()
        
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("DEPARTMENT SUMMARY REPORT")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("=" * 60)
        report_lines.append("")
        
        if not rows:
            report_lines.append("No departments found.")
        else:
            header = f"{'Department':<30} | {'Employee Count':<15}"
            report_lines.append(header)
            report_lines.append("-" * 60)
            
            total_employees = 0
            for row in rows:
                line = f"{row['department']:<30} | {row['employee_count']:<15}"
                report_lines.append(line)
                total_employees += row['employee_count']
            
            report_lines.append("-" * 60)
            report_lines.append(f"{'Total':<30} | {total_employees:<15}")
        
        report_lines.append("")
        report_lines.append("=" * 60)
        
        report = "\n".join(report_lines)
        print(report)
        return report
        
    finally:
        conn.close()


def generate_project_status_report(db_path=None):
    """
    Generate a report showing project statuses and team sizes.
    
    Args:
        db_path (str, optional): Path to the database file.
    
    Returns:
        str: A formatted project status report.
    """
    conn = get_sqlite_connection(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT 
                p.project_id,
                p.project_name,
                p.start_date,
                p.end_date,
                p.status,
                COUNT(ep.employee_id) as team_size
            FROM Projects p
            LEFT JOIN EmployeeProjects ep ON p.project_id = ep.project_id
            GROUP BY p.project_id
            ORDER BY p.status, p.start_date
        ''')
        
        rows = cursor.fetchall()
        
        report_lines = []
        report_lines.append("=" * 100)
        report_lines.append("PROJECT STATUS REPORT")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("=" * 100)
        report_lines.append("")
        
        if not rows:
            report_lines.append("No projects found.")
        else:
            header = f"{'Project Name':<25} | {'Status':<12} | {'Start Date':<12} | {'End Date':<12} | {'Team Size':<10}"
            report_lines.append(header)
            report_lines.append("-" * 100)
            
            current_status = None
            for row in rows:
                if current_status != row['status']:
                    if current_status is not None:
                        report_lines.append("")
                    current_status = row['status']
                
                end_date = row['end_date'] if row['end_date'] else 'Ongoing'
                line = f"{row['project_name']:<25} | {row['status']:<12} | {row['start_date']:<12} | {end_date:<12} | {row['team_size']:<10}"
                report_lines.append(line)
        
        report_lines.append("")
        report_lines.append(f"Total Projects: {len(rows)}")
        report_lines.append("=" * 100)
        
        report = "\n".join(report_lines)
        print(report)
        return report
        
    finally:
        conn.close()


def export_employee_project_report_to_csv(filename='employee_project_report.csv', db_path=None):
    """
    Export employee-project assignments to a CSV file.
    
    Args:
        filename (str): Output CSV filename.
        db_path (str, optional): Path to the database file.
    
    Returns:
        str: Path to the created CSV file.
    """
    import csv
    
    conn = get_sqlite_connection(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT 
                e.employee_id,
                e.first_name,
                e.last_name,
                e.email,
                e.department,
                p.project_id,
                p.project_name,
                p.status AS project_status,
                ep.role,
                ep.assignment_date
            FROM EmployeeProjects ep
            INNER JOIN Employees e ON ep.employee_id = e.employee_id
            INNER JOIN Projects p ON ep.project_id = p.project_id
            ORDER BY e.last_name, e.first_name
        ''')
        
        rows = cursor.fetchall()
        
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['employee_id', 'first_name', 'last_name', 'email', 
                         'department', 'project_id', 'project_name', 
                         'project_status', 'role', 'assignment_date']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for row in rows:
                writer.writerow(dict(row))
        
        print(f"Report exported to {filename}")
        return filename
        
    finally:
        conn.close()
