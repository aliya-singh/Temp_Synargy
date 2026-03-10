"""
Employee Performance Tracker - Main Application

This is the entry point for the Employee Performance Tracker application.
Provides a command-line interface (CLI) for all system operations.

Features:
- Employee management (add, view, list)
- Project management (add, assign employees)
- Performance review management (submit, view)
- Report generation (employee-project, performance summaries)
"""

import sys
from datetime import datetime

# Initialize the app module path
from app.db_connections import initialize_all_databases, initialize_sql_database
from app.employee_manager import (
    add_employee, get_employee_by_id, list_all_employees,
    update_employee, delete_employee, search_employees,
    DuplicateEmailError, EmployeeNotFoundError
)
from app.project_manager import (
    add_project, get_project_by_id, list_all_projects,
    assign_employee_to_project, remove_employee_from_project,
    get_projects_for_employee, get_employees_for_project,
    update_project, delete_project,
    ProjectNotFoundError, AssignmentError
)
from app.performance_reviewer import (
    submit_performance_review, get_performance_reviews_for_employee,
    get_review_by_id, get_average_rating_for_employee,
    MongoDBConnectionError
)
from app.reports import (
    generate_employee_project_report, generate_employee_performance_summary,
    generate_department_summary, generate_project_status_report
)


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_menu():
    """Display the main menu."""
    print_header("EMPLOYEE PERFORMANCE TRACKER")
    print("""
    EMPLOYEE MANAGEMENT
    1.  Add Employee
    2.  View Employee by ID
    3.  List All Employees
    4.  Update Employee
    5.  Delete Employee
    
    PROJECT MANAGEMENT
    6.  Add Project
    7.  View Project by ID
    8.  List All Projects
    9.  Assign Employee to Project
    10. Remove Employee from Project
    11. View Projects for Employee
    12. View Employees for Project
    
    PERFORMANCE REVIEWS
    13. Submit Performance Review
    14. View Reviews for Employee
    15. View Average Rating for Employee
    
    REPORTS
    16. Generate Employee-Project Report
    17. Generate Employee Performance Summary
    18. Generate Department Summary
    19. Generate Project Status Report
    
    0.  Exit
    """)


def get_input(prompt, required=True, input_type=str):
    """Get user input with validation."""
    while True:
        value = input(prompt).strip()
        if not value and required:
            print("This field is required. Please enter a value.")
            continue
        if not value and not required:
            return None
        try:
            return input_type(value)
        except ValueError:
            print(f"Invalid input. Expected {input_type.__name__}.")


def handle_add_employee():
    """Handle adding a new employee."""
    print_header("ADD EMPLOYEE")
    
    first_name = get_input("First Name: ")
    last_name = get_input("Last Name: ")
    email = get_input("Email: ")
    hire_date = get_input("Hire Date (YYYY-MM-DD): ")
    department = get_input("Department: ")
    
    try:
        employee_id = add_employee(first_name, last_name, email, hire_date, department)
        print(f"\n✓ Employee added successfully! ID: {employee_id}")
    except DuplicateEmailError as e:
        print(f"\n✗ Error: {e}")
    except ValueError as e:
        print(f"\n✗ Validation Error: {e}")


def handle_view_employee():
    """Handle viewing an employee by ID."""
    print_header("VIEW EMPLOYEE")
    
    employee_id = get_input("Employee ID: ", input_type=int)
    
    try:
        employee = get_employee_by_id(employee_id)
        print("\n--- Employee Details ---")
        print(f"ID: {employee['employee_id']}")
        print(f"Name: {employee['first_name']} {employee['last_name']}")
        print(f"Email: {employee['email']}")
        print(f"Department: {employee['department']}")
        print(f"Hire Date: {employee['hire_date']}")
    except EmployeeNotFoundError as e:
        print(f"\n✗ Error: {e}")


def handle_list_employees():
    """Handle listing all employees."""
    print_header("ALL EMPLOYEES")
    
    employees = list_all_employees()
    
    if not employees:
        print("\nNo employees found.")
        return
    
    print(f"\n{'ID':<6} | {'Name':<25} | {'Email':<30} | {'Department':<15}")
    print("-" * 80)
    
    for emp in employees:
        name = f"{emp['first_name']} {emp['last_name']}"
        print(f"{emp['employee_id']:<6} | {name:<25} | {emp['email']:<30} | {emp['department']:<15}")
    
    print(f"\nTotal: {len(employees)} employee(s)")


def handle_update_employee():
    """Handle updating an employee."""
    print_header("UPDATE EMPLOYEE")
    
    employee_id = get_input("Employee ID: ", input_type=int)
    
    try:
        employee = get_employee_by_id(employee_id)
        print(f"\nCurrent: {employee['first_name']} {employee['last_name']} ({employee['email']})")
        print("Leave blank to keep current value.\n")
        
        first_name = get_input(f"First Name [{employee['first_name']}]: ", required=False) or None
        last_name = get_input(f"Last Name [{employee['last_name']}]: ", required=False) or None
        email = get_input(f"Email [{employee['email']}]: ", required=False) or None
        department = get_input(f"Department [{employee['department']}]: ", required=False) or None
        
        update_employee(employee_id, first_name=first_name, last_name=last_name,
                       email=email, department=department)
        print("\n✓ Employee updated successfully!")
        
    except EmployeeNotFoundError as e:
        print(f"\n✗ Error: {e}")
    except (DuplicateEmailError, ValueError) as e:
        print(f"\n✗ Error: {e}")


def handle_delete_employee():
    """Handle deleting an employee."""
    print_header("DELETE EMPLOYEE")
    
    employee_id = get_input("Employee ID: ", input_type=int)
    
    try:
        employee = get_employee_by_id(employee_id)
        print(f"\nEmployee: {employee['first_name']} {employee['last_name']}")
        
        confirm = input("Are you sure you want to delete this employee? (yes/no): ").strip().lower()
        if confirm == 'yes':
            delete_employee(employee_id)
            print("\n✓ Employee deleted successfully!")
        else:
            print("\n✗ Deletion cancelled.")
            
    except EmployeeNotFoundError as e:
        print(f"\n✗ Error: {e}")


def handle_add_project():
    """Handle adding a new project."""
    print_header("ADD PROJECT")
    
    project_name = get_input("Project Name: ")
    start_date = get_input("Start Date (YYYY-MM-DD): ")
    end_date = get_input("End Date (YYYY-MM-DD, or leave blank): ", required=False)
    
    print("\nStatus options: Planning, In Progress, On Hold, Completed, Cancelled")
    status = get_input("Status [Planning]: ", required=False) or 'Planning'
    
    try:
        project_id = add_project(project_name, start_date, end_date, status)
        print(f"\n✓ Project added successfully! ID: {project_id}")
    except ValueError as e:
        print(f"\n✗ Validation Error: {e}")


def handle_view_project():
    """Handle viewing a project by ID."""
    print_header("VIEW PROJECT")
    
    project_id = get_input("Project ID: ", input_type=int)
    
    try:
        project = get_project_by_id(project_id)
        print("\n--- Project Details ---")
        print(f"ID: {project['project_id']}")
        print(f"Name: {project['project_name']}")
        print(f"Start Date: {project['start_date']}")
        print(f"End Date: {project['end_date'] or 'Not set'}")
        print(f"Status: {project['status']}")
        
        # Show assigned employees
        employees = get_employees_for_project(project_id)
        print(f"\nAssigned Employees ({len(employees)}):")
        if employees:
            for emp in employees:
                print(f"  - {emp['first_name']} {emp['last_name']} ({emp['role']})")
        else:
            print("  No employees assigned.")
            
    except ProjectNotFoundError as e:
        print(f"\n✗ Error: {e}")


def handle_list_projects():
    """Handle listing all projects."""
    print_header("ALL PROJECTS")
    
    projects = list_all_projects()
    
    if not projects:
        print("\nNo projects found.")
        return
    
    print(f"\n{'ID':<6} | {'Project Name':<25} | {'Status':<12} | {'Start Date':<12} | {'End Date':<12}")
    print("-" * 75)
    
    for proj in projects:
        end_date = proj['end_date'] or 'Ongoing'
        print(f"{proj['project_id']:<6} | {proj['project_name']:<25} | {proj['status']:<12} | {proj['start_date']:<12} | {end_date:<12}")
    
    print(f"\nTotal: {len(projects)} project(s)")


def handle_assign_employee():
    """Handle assigning an employee to a project."""
    print_header("ASSIGN EMPLOYEE TO PROJECT")
    
    employee_id = get_input("Employee ID: ", input_type=int)
    project_id = get_input("Project ID: ", input_type=int)
    role = get_input("Role (e.g., Developer, Manager, QA): ")
    
    try:
        assignment_id = assign_employee_to_project(employee_id, project_id, role)
        print(f"\n✓ Employee assigned successfully! Assignment ID: {assignment_id}")
    except AssignmentError as e:
        print(f"\n✗ Error: {e}")
    except ValueError as e:
        print(f"\n✗ Validation Error: {e}")


def handle_remove_employee_from_project():
    """Handle removing an employee from a project."""
    print_header("REMOVE EMPLOYEE FROM PROJECT")
    
    employee_id = get_input("Employee ID: ", input_type=int)
    project_id = get_input("Project ID: ", input_type=int)
    
    try:
        remove_employee_from_project(employee_id, project_id)
        print("\n✓ Employee removed from project successfully!")
    except AssignmentError as e:
        print(f"\n✗ Error: {e}")


def handle_view_projects_for_employee():
    """Handle viewing projects for an employee."""
    print_header("PROJECTS FOR EMPLOYEE")
    
    employee_id = get_input("Employee ID: ", input_type=int)
    
    try:
        employee = get_employee_by_id(employee_id)
        projects = get_projects_for_employee(employee_id)
        
        print(f"\nProjects for {employee['first_name']} {employee['last_name']}:")
        print("-" * 60)
        
        if not projects:
            print("No project assignments found.")
        else:
            for proj in projects:
                print(f"  • {proj['project_name']} - {proj['role']} ({proj['status']})")
                print(f"    Assigned: {proj['assignment_date']}")
                
    except EmployeeNotFoundError as e:
        print(f"\n✗ Error: {e}")


def handle_view_employees_for_project():
    """Handle viewing employees for a project."""
    print_header("EMPLOYEES FOR PROJECT")
    
    project_id = get_input("Project ID: ", input_type=int)
    
    try:
        project = get_project_by_id(project_id)
        employees = get_employees_for_project(project_id)
        
        print(f"\nEmployees for {project['project_name']}:")
        print("-" * 60)
        
        if not employees:
            print("No employees assigned to this project.")
        else:
            for emp in employees:
                print(f"  • {emp['first_name']} {emp['last_name']} - {emp['role']}")
                print(f"    Email: {emp['email']} | Assigned: {emp['assignment_date']}")
                
    except ProjectNotFoundError as e:
        print(f"\n✗ Error: {e}")


def handle_submit_review():
    """Handle submitting a performance review."""
    print_header("SUBMIT PERFORMANCE REVIEW")
    
    employee_id = get_input("Employee ID: ", input_type=int)
    
    try:
        employee = get_employee_by_id(employee_id)
        print(f"\nReviewing: {employee['first_name']} {employee['last_name']}")
    except EmployeeNotFoundError as e:
        print(f"\n✗ Error: {e}")
        return
    
    reviewer_name = get_input("Your Name (Reviewer): ")
    overall_rating = get_input("Overall Rating (1-5): ", input_type=float)
    
    print("\nEnter strengths (one per line, empty line to finish):")
    strengths = []
    while True:
        s = input("  Strength: ").strip()
        if not s:
            break
        strengths.append(s)
    
    print("\nEnter areas for improvement (one per line, empty line to finish):")
    areas = []
    while True:
        a = input("  Area: ").strip()
        if not a:
            break
        areas.append(a)
    
    comments = get_input("Additional Comments (optional): ", required=False) or ""
    
    print("\nEnter goals for next period (one per line, empty line to finish):")
    goals = []
    while True:
        g = input("  Goal: ").strip()
        if not g:
            break
        goals.append(g)
    
    try:
        review_id = submit_performance_review(
            employee_id=employee_id,
            reviewer_name=reviewer_name,
            overall_rating=overall_rating,
            strengths=strengths,
            areas_for_improvement=areas,
            comments=comments,
            goals_for_next_period=goals
        )
        print(f"\n✓ Review submitted successfully! ID: {review_id}")
    except MongoDBConnectionError as e:
        print(f"\n✗ MongoDB Error: {e}")
        print("  Please ensure MongoDB is running and accessible.")
    except ValueError as e:
        print(f"\n✗ Validation Error: {e}")


def handle_view_reviews():
    """Handle viewing reviews for an employee."""
    print_header("PERFORMANCE REVIEWS FOR EMPLOYEE")
    
    employee_id = get_input("Employee ID: ", input_type=int)
    
    try:
        employee = get_employee_by_id(employee_id)
        print(f"\nReviews for {employee['first_name']} {employee['last_name']}:")
        print("-" * 60)
        
        reviews = get_performance_reviews_for_employee(employee_id)
        
        if not reviews:
            print("No performance reviews found.")
        else:
            for review in reviews:
                print(f"\nDate: {review['review_date']} | Rating: {review['overall_rating']}/5")
                print(f"Reviewer: {review['reviewer_name']}")
                
                if review.get('strengths'):
                    print(f"Strengths: {', '.join(review['strengths'])}")
                if review.get('areas_for_improvement'):
                    print(f"Areas for Improvement: {', '.join(review['areas_for_improvement'])}")
                if review.get('comments'):
                    print(f"Comments: {review['comments']}")
                print("-" * 40)
                
    except EmployeeNotFoundError as e:
        print(f"\n✗ Error: {e}")
    except MongoDBConnectionError as e:
        print(f"\n✗ MongoDB Error: {e}")


def handle_view_average_rating():
    """Handle viewing average rating for an employee."""
    print_header("AVERAGE RATING FOR EMPLOYEE")
    
    employee_id = get_input("Employee ID: ", input_type=int)
    
    try:
        employee = get_employee_by_id(employee_id)
        rating_info = get_average_rating_for_employee(employee_id)
        
        print(f"\nRating Summary for {employee['first_name']} {employee['last_name']}:")
        print("-" * 40)
        
        if rating_info['review_count'] == 0:
            print("No reviews found.")
        else:
            print(f"Total Reviews: {rating_info['review_count']}")
            print(f"Average Rating: {rating_info['average_rating']:.2f} / 5.00")
            print(f"Min Rating: {rating_info['min_rating']:.1f}")
            print(f"Max Rating: {rating_info['max_rating']:.1f}")
            
    except EmployeeNotFoundError as e:
        print(f"\n✗ Error: {e}")
    except MongoDBConnectionError as e:
        print(f"\n✗ MongoDB Error: {e}")


def handle_generate_employee_project_report():
    """Handle generating employee-project report."""
    print_header("EMPLOYEE-PROJECT REPORT")
    generate_employee_project_report()


def handle_generate_performance_summary():
    """Handle generating performance summary."""
    print_header("EMPLOYEE PERFORMANCE SUMMARY")
    
    employee_id = get_input("Employee ID: ", input_type=int)
    
    try:
        generate_employee_performance_summary(employee_id)
    except EmployeeNotFoundError as e:
        print(f"\n✗ Error: {e}")


def handle_generate_department_summary():
    """Handle generating department summary."""
    print_header("DEPARTMENT SUMMARY")
    
    department = get_input("Department (or leave blank for all): ", required=False)
    generate_department_summary(department if department else None)


def handle_generate_project_status_report():
    """Handle generating project status report."""
    print_header("PROJECT STATUS REPORT")
    generate_project_status_report()


def main():
    """Main application entry point."""
    print("\nInitializing Employee Performance Tracker...")
    
    # Initialize SQL database (always)
    try:
        initialize_sql_database()
    except Exception as e:
        print(f"Error initializing SQL database: {e}")
        sys.exit(1)
    
    # Try to initialize MongoDB (optional)
    try:
        from app.db_connections import initialize_mongo_database
        initialize_mongo_database()
    except Exception as e:
        print(f"Warning: MongoDB not available. Performance reviews will be disabled.")
        print(f"  Details: {e}")
    
    print("\n✓ System ready!")
    
    # Menu handlers mapping
    handlers = {
        '1': handle_add_employee,
        '2': handle_view_employee,
        '3': handle_list_employees,
        '4': handle_update_employee,
        '5': handle_delete_employee,
        '6': handle_add_project,
        '7': handle_view_project,
        '8': handle_list_projects,
        '9': handle_assign_employee,
        '10': handle_remove_employee_from_project,
        '11': handle_view_projects_for_employee,
        '12': handle_view_employees_for_project,
        '13': handle_submit_review,
        '14': handle_view_reviews,
        '15': handle_view_average_rating,
        '16': handle_generate_employee_project_report,
        '17': handle_generate_performance_summary,
        '18': handle_generate_department_summary,
        '19': handle_generate_project_status_report,
    }
    
    while True:
        print_menu()
        choice = input("Enter your choice (0-19): ").strip()
        
        if choice == '0':
            print("\nThank you for using Employee Performance Tracker. Goodbye!")
            break
        elif choice in handlers:
            try:
                handlers[choice]()
            except KeyboardInterrupt:
                print("\n\nOperation cancelled.")
            except Exception as e:
                print(f"\n✗ Unexpected error: {e}")
        else:
            print("\n✗ Invalid choice. Please enter a number between 0 and 19.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
