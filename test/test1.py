# filepath: /Users/divyanshuraj/Downloads/Synergy/test/test1.py
"""
Comprehensive test suite for Employee Performance Tracker.

This module contains all tests for:
- Employee management (test_employee.py functionality)
- Project management (test_project.py functionality)
- Performance reviews (test_reviews.py functionality)

Tests are designed to achieve at least 80% code coverage.
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================
# EMPLOYEE MANAGER TESTS
# ============================================================

class TestEmployeeManager:
    """Tests for the employee_manager module."""
    
    def test_add_employee_success(self, initialized_db, sample_employee_data):
        """Test successful employee creation."""
        from app.employee_manager import add_employee, get_employee_by_id
        
        employee_id = add_employee(
            first_name=sample_employee_data['first_name'],
            last_name=sample_employee_data['last_name'],
            email=sample_employee_data['email'],
            hire_date=sample_employee_data['hire_date'],
            department=sample_employee_data['department'],
            db_path=initialized_db
        )
        
        assert employee_id is not None
        assert isinstance(employee_id, int)
        assert employee_id > 0
        
        # Verify employee was created
        employee = get_employee_by_id(employee_id, db_path=initialized_db)
        assert employee['first_name'] == sample_employee_data['first_name']
        assert employee['last_name'] == sample_employee_data['last_name']
        assert employee['email'] == sample_employee_data['email'].lower()
    
    def test_add_employee_duplicate_email(self, initialized_db, sample_employee_data):
        """Test that duplicate emails raise DuplicateEmailError."""
        from app.employee_manager import add_employee, DuplicateEmailError
        
        # Add first employee
        add_employee(
            first_name=sample_employee_data['first_name'],
            last_name=sample_employee_data['last_name'],
            email=sample_employee_data['email'],
            hire_date=sample_employee_data['hire_date'],
            department=sample_employee_data['department'],
            db_path=initialized_db
        )
        
        # Try to add another employee with the same email
        with pytest.raises(DuplicateEmailError):
            add_employee(
                first_name='Jane',
                last_name='Smith',
                email=sample_employee_data['email'],  # Same email
                hire_date='2024-02-01',
                department='Marketing',
                db_path=initialized_db
            )
    
    def test_add_employee_invalid_email(self, initialized_db):
        """Test that invalid email format raises ValueError."""
        from app.employee_manager import add_employee
        
        with pytest.raises(ValueError, match="Invalid email format"):
            add_employee(
                first_name='Test',
                last_name='User',
                email='invalid-email',
                hire_date='2024-01-01',
                department='Test',
                db_path=initialized_db
            )
    
    def test_add_employee_invalid_date(self, initialized_db):
        """Test that invalid date format raises ValueError."""
        from app.employee_manager import add_employee
        
        with pytest.raises(ValueError, match="YYYY-MM-DD"):
            add_employee(
                first_name='Test',
                last_name='User',
                email='test@example.com',
                hire_date='01-01-2024',  # Wrong format
                department='Test',
                db_path=initialized_db
            )
    
    def test_add_employee_missing_fields(self, initialized_db):
        """Test that missing required fields raise ValueError."""
        from app.employee_manager import add_employee
        
        with pytest.raises(ValueError, match="required"):
            add_employee(
                first_name='',
                last_name='User',
                email='test@example.com',
                hire_date='2024-01-01',
                department='Test',
                db_path=initialized_db
            )
    
    def test_get_employee_by_id_success(self, populated_db):
        """Test successful employee retrieval by ID."""
        from app.employee_manager import get_employee_by_id
        
        employee = get_employee_by_id(
            populated_db['employee_id'],
            db_path=populated_db['db_path']
        )
        
        assert employee is not None
        assert employee['employee_id'] == populated_db['employee_id']
        assert 'first_name' in employee
        assert 'last_name' in employee
        assert 'email' in employee
    
    def test_get_employee_by_id_not_found(self, initialized_db):
        """Test that non-existent employee raises EmployeeNotFoundError."""
        from app.employee_manager import get_employee_by_id, EmployeeNotFoundError
        
        with pytest.raises(EmployeeNotFoundError):
            get_employee_by_id(99999, db_path=initialized_db)
    
    def test_list_all_employees_empty(self, initialized_db):
        """Test listing employees when database is empty."""
        from app.employee_manager import list_all_employees
        
        employees = list_all_employees(db_path=initialized_db)
        
        assert employees == []
    
    def test_list_all_employees_with_data(self, populated_db):
        """Test listing all employees."""
        from app.employee_manager import list_all_employees, add_employee
        
        # Add another employee
        add_employee(
            first_name='Jane',
            last_name='Smith',
            email='jane.smith@example.com',
            hire_date='2024-02-01',
            department='Marketing',
            db_path=populated_db['db_path']
        )
        
        employees = list_all_employees(db_path=populated_db['db_path'])
        
        assert len(employees) == 2
        assert all('employee_id' in emp for emp in employees)
    
    def test_update_employee_success(self, populated_db):
        """Test successful employee update."""
        from app.employee_manager import update_employee, get_employee_by_id
        
        result = update_employee(
            populated_db['employee_id'],
            first_name='Johnny',
            department='Sales',
            db_path=populated_db['db_path']
        )
        
        assert result is True
        
        employee = get_employee_by_id(
            populated_db['employee_id'],
            db_path=populated_db['db_path']
        )
        assert employee['first_name'] == 'Johnny'
        assert employee['department'] == 'Sales'
    
    def test_update_employee_not_found(self, initialized_db):
        """Test updating non-existent employee."""
        from app.employee_manager import update_employee, EmployeeNotFoundError
        
        with pytest.raises(EmployeeNotFoundError):
            update_employee(99999, first_name='Test', db_path=initialized_db)
    
    def test_delete_employee_success(self, populated_db):
        """Test successful employee deletion."""
        from app.employee_manager import delete_employee, get_employee_by_id, EmployeeNotFoundError
        
        result = delete_employee(
            populated_db['employee_id'],
            db_path=populated_db['db_path']
        )
        
        assert result is True
        
        with pytest.raises(EmployeeNotFoundError):
            get_employee_by_id(
                populated_db['employee_id'],
                db_path=populated_db['db_path']
            )
    
    def test_search_employees(self, populated_db):
        """Test employee search functionality."""
        from app.employee_manager import search_employees, add_employee
        
        # Add more employees
        add_employee(
            first_name='Jane',
            last_name='Doe',
            email='jane.doe@example.com',
            hire_date='2024-02-01',
            department='Engineering',
            db_path=populated_db['db_path']
        )
        
        # Search by last name
        results = search_employees('Doe', db_path=populated_db['db_path'])
        assert len(results) == 2
        
        # Search by department
        results = search_employees('Engineering', db_path=populated_db['db_path'])
        assert len(results) >= 1


# ============================================================
# PROJECT MANAGER TESTS
# ============================================================

class TestProjectManager:
    """Tests for the project_manager module."""
    
    def test_add_project_success(self, initialized_db, sample_project_data):
        """Test successful project creation."""
        from app.project_manager import add_project, get_project_by_id
        
        project_id = add_project(
            project_name=sample_project_data['project_name'],
            start_date=sample_project_data['start_date'],
            end_date=sample_project_data['end_date'],
            status=sample_project_data['status'],
            db_path=initialized_db
        )
        
        assert project_id is not None
        assert isinstance(project_id, int)
        
        project = get_project_by_id(project_id, db_path=initialized_db)
        assert project['project_name'] == sample_project_data['project_name']
    
    def test_add_project_without_end_date(self, initialized_db):
        """Test adding a project without an end date."""
        from app.project_manager import add_project, get_project_by_id
        
        project_id = add_project(
            project_name='Ongoing Project',
            start_date='2024-01-01',
            db_path=initialized_db
        )
        
        project = get_project_by_id(project_id, db_path=initialized_db)
        assert project['end_date'] is None
        assert project['status'] == 'Planning'  # Default status
    
    def test_add_project_invalid_date(self, initialized_db):
        """Test that invalid date format raises ValueError."""
        from app.project_manager import add_project
        
        with pytest.raises(ValueError, match="YYYY-MM-DD"):
            add_project(
                project_name='Test Project',
                start_date='invalid-date',
                db_path=initialized_db
            )
    
    def test_add_project_end_before_start(self, initialized_db):
        """Test that end date before start date raises ValueError."""
        from app.project_manager import add_project
        
        with pytest.raises(ValueError, match="end_date cannot be before"):
            add_project(
                project_name='Test Project',
                start_date='2024-12-01',
                end_date='2024-01-01',
                db_path=initialized_db
            )
    
    def test_add_project_invalid_status(self, initialized_db):
        """Test that invalid status raises ValueError."""
        from app.project_manager import add_project
        
        with pytest.raises(ValueError, match="Invalid status"):
            add_project(
                project_name='Test Project',
                start_date='2024-01-01',
                status='InvalidStatus',
                db_path=initialized_db
            )
    
    def test_get_project_by_id_not_found(self, initialized_db):
        """Test that non-existent project raises ProjectNotFoundError."""
        from app.project_manager import get_project_by_id, ProjectNotFoundError
        
        with pytest.raises(ProjectNotFoundError):
            get_project_by_id(99999, db_path=initialized_db)
    
    def test_list_all_projects(self, initialized_db):
        """Test listing all projects."""
        from app.project_manager import add_project, list_all_projects
        
        # Add multiple projects
        add_project('Project A', '2024-01-01', db_path=initialized_db)
        add_project('Project B', '2024-02-01', db_path=initialized_db)
        
        projects = list_all_projects(db_path=initialized_db)
        
        assert len(projects) == 2
    
    def test_assign_employee_to_project_success(self, populated_db):
        """Test successful employee assignment to project."""
        from app.project_manager import assign_employee_to_project, get_projects_for_employee
        
        assignment_id = assign_employee_to_project(
            employee_id=populated_db['employee_id'],
            project_id=populated_db['project_id'],
            role='Developer',
            db_path=populated_db['db_path']
        )
        
        assert assignment_id is not None
        
        projects = get_projects_for_employee(
            populated_db['employee_id'],
            db_path=populated_db['db_path']
        )
        assert len(projects) == 1
        assert projects[0]['role'] == 'Developer'
    
    def test_assign_employee_duplicate_assignment(self, populated_db):
        """Test that duplicate assignment raises AssignmentError."""
        from app.project_manager import assign_employee_to_project, AssignmentError
        
        # First assignment
        assign_employee_to_project(
            employee_id=populated_db['employee_id'],
            project_id=populated_db['project_id'],
            role='Developer',
            db_path=populated_db['db_path']
        )
        
        # Try duplicate assignment
        with pytest.raises(AssignmentError, match="already assigned"):
            assign_employee_to_project(
                employee_id=populated_db['employee_id'],
                project_id=populated_db['project_id'],
                role='Manager',
                db_path=populated_db['db_path']
            )
    
    def test_assign_employee_invalid_employee(self, populated_db):
        """Test assignment with invalid employee ID."""
        from app.project_manager import assign_employee_to_project, AssignmentError
        
        with pytest.raises(AssignmentError, match="Employee with ID"):
            assign_employee_to_project(
                employee_id=99999,
                project_id=populated_db['project_id'],
                role='Developer',
                db_path=populated_db['db_path']
            )
    
    def test_assign_employee_invalid_project(self, populated_db):
        """Test assignment with invalid project ID."""
        from app.project_manager import assign_employee_to_project, AssignmentError
        
        with pytest.raises(AssignmentError, match="Project with ID"):
            assign_employee_to_project(
                employee_id=populated_db['employee_id'],
                project_id=99999,
                role='Developer',
                db_path=populated_db['db_path']
            )
    
    def test_remove_employee_from_project(self, populated_db):
        """Test removing employee from project."""
        from app.project_manager import (
            assign_employee_to_project, 
            remove_employee_from_project,
            get_projects_for_employee
        )
        
        # First assign
        assign_employee_to_project(
            employee_id=populated_db['employee_id'],
            project_id=populated_db['project_id'],
            role='Developer',
            db_path=populated_db['db_path']
        )
        
        # Then remove
        result = remove_employee_from_project(
            employee_id=populated_db['employee_id'],
            project_id=populated_db['project_id'],
            db_path=populated_db['db_path']
        )
        
        assert result is True
        
        projects = get_projects_for_employee(
            populated_db['employee_id'],
            db_path=populated_db['db_path']
        )
        assert len(projects) == 0
    
    def test_get_employees_for_project(self, populated_db):
        """Test getting employees assigned to a project."""
        from app.project_manager import (
            assign_employee_to_project,
            get_employees_for_project
        )
        from app.employee_manager import add_employee
        
        # Add another employee
        emp2_id = add_employee(
            first_name='Jane',
            last_name='Smith',
            email='jane.smith@example.com',
            hire_date='2024-02-01',
            department='QA',
            db_path=populated_db['db_path']
        )
        
        # Assign both to the project
        assign_employee_to_project(
            populated_db['employee_id'],
            populated_db['project_id'],
            'Developer',
            db_path=populated_db['db_path']
        )
        assign_employee_to_project(
            emp2_id,
            populated_db['project_id'],
            'QA Engineer',
            db_path=populated_db['db_path']
        )
        
        employees = get_employees_for_project(
            populated_db['project_id'],
            db_path=populated_db['db_path']
        )
        
        assert len(employees) == 2
    
    def test_update_project(self, populated_db):
        """Test updating a project."""
        from app.project_manager import update_project, get_project_by_id
        
        result = update_project(
            populated_db['project_id'],
            project_name='Updated Project Name',
            status='Completed',
            db_path=populated_db['db_path']
        )
        
        assert result is True
        
        project = get_project_by_id(
            populated_db['project_id'],
            db_path=populated_db['db_path']
        )
        assert project['project_name'] == 'Updated Project Name'
        assert project['status'] == 'Completed'
    
    def test_delete_project(self, populated_db):
        """Test deleting a project."""
        from app.project_manager import delete_project, get_project_by_id, ProjectNotFoundError
        
        result = delete_project(
            populated_db['project_id'],
            db_path=populated_db['db_path']
        )
        
        assert result is True
        
        with pytest.raises(ProjectNotFoundError):
            get_project_by_id(
                populated_db['project_id'],
                db_path=populated_db['db_path']
            )


# ============================================================
# PERFORMANCE REVIEWER TESTS
# ============================================================

class TestPerformanceReviewer:
    """Tests for the performance_reviewer module."""
    
    def test_submit_review_success(self, mock_mongo_collection):
        """Test successful performance review submission."""
        from app.performance_reviewer import submit_performance_review
        
        review_id = submit_performance_review(
            employee_id=1,
            reviewer_name='Manager Smith',
            overall_rating=4.5,
            strengths=['Communication', 'Technical Skills'],
            areas_for_improvement=['Time Management'],
            comments='Great employee',
            goals_for_next_period=['Complete certification']
        )
        
        assert review_id is not None
    
    def test_submit_review_missing_fields(self, mock_mongo_collection):
        """Test that missing required fields raise ValueError."""
        from app.performance_reviewer import submit_performance_review
        
        with pytest.raises(ValueError, match="employee_id is required"):
            submit_performance_review(
                employee_id=None,
                reviewer_name='Manager',
                overall_rating=4.0
            )
        
        with pytest.raises(ValueError, match="reviewer_name is required"):
            submit_performance_review(
                employee_id=1,
                reviewer_name='',
                overall_rating=4.0
            )
    
    def test_submit_review_invalid_rating(self, mock_mongo_collection):
        """Test that invalid rating raises ValueError."""
        from app.performance_reviewer import submit_performance_review
        
        with pytest.raises(ValueError, match="between 1 and 5"):
            submit_performance_review(
                employee_id=1,
                reviewer_name='Manager',
                overall_rating=6.0  # Invalid: > 5
            )
        
        with pytest.raises(ValueError, match="between 1 and 5"):
            submit_performance_review(
                employee_id=1,
                reviewer_name='Manager',
                overall_rating=0  # Invalid: < 1
            )
    
    def test_get_reviews_for_employee(self, mock_mongo_collection):
        """Test retrieving reviews for an employee."""
        from app.performance_reviewer import (
            submit_performance_review,
            get_performance_reviews_for_employee
        )
        
        # Submit a review
        submit_performance_review(
            employee_id=1,
            reviewer_name='Manager',
            overall_rating=4.0
        )
        
        reviews = get_performance_reviews_for_employee(1)
        
        assert len(reviews) >= 1
        assert reviews[0]['employee_id'] == 1
    
    def test_get_average_rating(self, mock_mongo_collection):
        """Test calculating average rating for an employee."""
        from app.performance_reviewer import (
            submit_performance_review,
            get_average_rating_for_employee
        )
        
        # Submit multiple reviews
        submit_performance_review(
            employee_id=1,
            reviewer_name='Manager A',
            overall_rating=4.0
        )
        submit_performance_review(
            employee_id=1,
            reviewer_name='Manager B',
            overall_rating=5.0
        )
        
        rating_info = get_average_rating_for_employee(1)
        
        assert rating_info['review_count'] == 2
        assert rating_info['average_rating'] == 4.5


# ============================================================
# DATABASE CONNECTION TESTS
# ============================================================

class TestDatabaseConnections:
    """Tests for the db_connections module."""
    
    def test_sqlite_connection(self, temp_db_path):
        """Test SQLite connection establishment."""
        from app.db_connections import get_sqlite_connection
        
        conn = get_sqlite_connection(temp_db_path)
        
        assert conn is not None
        
        # Test that we can execute a query
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        assert result[0] == 1
        
        conn.close()
    
    def test_initialize_sql_database(self, temp_db_path):
        """Test SQL database initialization."""
        from app.db_connections import initialize_sql_database, get_sqlite_connection
        
        initialize_sql_database(temp_db_path)
        
        conn = get_sqlite_connection(temp_db_path)
        cursor = conn.cursor()
        
        # Check that tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert 'Employees' in tables
        assert 'Projects' in tables
        assert 'EmployeeProjects' in tables
        
        conn.close()


# ============================================================
# REPORTS TESTS
# ============================================================

class TestReports:
    """Tests for the reports module."""
    
    def test_generate_employee_project_report_empty(self, initialized_db):
        """Test generating report with no data."""
        from app.reports import generate_employee_project_report
        
        report = generate_employee_project_report(db_path=initialized_db)
        
        assert 'EMPLOYEE-PROJECT ASSIGNMENTS REPORT' in report
        assert 'No employee-project assignments found' in report
    
    def test_generate_employee_project_report_with_data(self, populated_db):
        """Test generating report with data."""
        from app.reports import generate_employee_project_report
        from app.project_manager import assign_employee_to_project
        
        # Create an assignment
        assign_employee_to_project(
            populated_db['employee_id'],
            populated_db['project_id'],
            'Developer',
            db_path=populated_db['db_path']
        )
        
        report = generate_employee_project_report(db_path=populated_db['db_path'])
        
        assert 'EMPLOYEE-PROJECT ASSIGNMENTS REPORT' in report
        assert 'Developer' in report
        assert 'Total Assignments: 1' in report
    
    def test_generate_department_summary(self, populated_db):
        """Test generating department summary."""
        from app.reports import generate_department_summary
        
        report = generate_department_summary(db_path=populated_db['db_path'])
        
        assert 'DEPARTMENT SUMMARY REPORT' in report
        assert 'Engineering' in report
    
    def test_generate_project_status_report(self, populated_db):
        """Test generating project status report."""
        from app.reports import generate_project_status_report
        
        report = generate_project_status_report(db_path=populated_db['db_path'])
        
        assert 'PROJECT STATUS REPORT' in report
        assert 'Alpha Project' in report


# ============================================================
# INTEGRATION TESTS
# ============================================================

class TestIntegration:
    """Integration tests combining multiple modules."""
    
    def test_full_employee_lifecycle(self, initialized_db):
        """Test complete employee lifecycle: create, read, update, delete."""
        from app.employee_manager import (
            add_employee, get_employee_by_id, update_employee, 
            delete_employee, EmployeeNotFoundError
        )
        
        # Create
        emp_id = add_employee(
            'Test', 'User', 'test.user@example.com',
            '2024-01-01', 'Engineering',
            db_path=initialized_db
        )
        
        # Read
        employee = get_employee_by_id(emp_id, db_path=initialized_db)
        assert employee['first_name'] == 'Test'
        
        # Update
        update_employee(emp_id, first_name='Updated', db_path=initialized_db)
        employee = get_employee_by_id(emp_id, db_path=initialized_db)
        assert employee['first_name'] == 'Updated'
        
        # Delete
        delete_employee(emp_id, db_path=initialized_db)
        with pytest.raises(EmployeeNotFoundError):
            get_employee_by_id(emp_id, db_path=initialized_db)
    
    def test_full_project_lifecycle(self, initialized_db):
        """Test complete project lifecycle: create, read, update, delete."""
        from app.project_manager import (
            add_project, get_project_by_id, update_project,
            delete_project, ProjectNotFoundError
        )
        
        # Create
        proj_id = add_project(
            'Test Project', '2024-01-01',
            db_path=initialized_db
        )
        
        # Read
        project = get_project_by_id(proj_id, db_path=initialized_db)
        assert project['project_name'] == 'Test Project'
        
        # Update
        update_project(proj_id, status='In Progress', db_path=initialized_db)
        project = get_project_by_id(proj_id, db_path=initialized_db)
        assert project['status'] == 'In Progress'
        
        # Delete
        delete_project(proj_id, db_path=initialized_db)
        with pytest.raises(ProjectNotFoundError):
            get_project_by_id(proj_id, db_path=initialized_db)
    
    def test_employee_project_assignment_workflow(self, initialized_db):
        """Test complete workflow of assigning employees to projects."""
        from app.employee_manager import add_employee
        from app.project_manager import (
            add_project, assign_employee_to_project,
            get_projects_for_employee, get_employees_for_project
        )
        
        # Create employees
        emp1_id = add_employee(
            'Alice', 'Developer', 'alice@example.com',
            '2024-01-01', 'Engineering',
            db_path=initialized_db
        )
        emp2_id = add_employee(
            'Bob', 'Designer', 'bob@example.com',
            '2024-01-02', 'Design',
            db_path=initialized_db
        )
        
        # Create projects
        proj1_id = add_project(
            'Website Redesign', '2024-02-01',
            db_path=initialized_db
        )
        proj2_id = add_project(
            'Mobile App', '2024-03-01',
            db_path=initialized_db
        )
        
        # Assign employees to projects
        assign_employee_to_project(
            emp1_id, proj1_id, 'Lead Developer',
            db_path=initialized_db
        )
        assign_employee_to_project(
            emp1_id, proj2_id, 'Developer',
            db_path=initialized_db
        )
        assign_employee_to_project(
            emp2_id, proj1_id, 'UI Designer',
            db_path=initialized_db
        )
        
        # Verify assignments
        alice_projects = get_projects_for_employee(emp1_id, db_path=initialized_db)
        assert len(alice_projects) == 2
        
        website_team = get_employees_for_project(proj1_id, db_path=initialized_db)
        assert len(website_team) == 2


# ============================================================
# ADDITIONAL TESTS FOR IMPROVED COVERAGE
# ============================================================

class TestEmployeeManagerAdditional:
    """Additional tests for employee_manager module to increase coverage."""
    
    def test_add_employee_email_normalized(self, initialized_db):
        """Test that email is normalized to lowercase."""
        from app.employee_manager import add_employee, get_employee_by_id
        
        employee_id = add_employee(
            first_name='Test',
            last_name='User',
            email='TEST.USER@EXAMPLE.COM',
            hire_date='2024-01-01',
            department='Test',
            db_path=initialized_db
        )
        
        employee = get_employee_by_id(employee_id, db_path=initialized_db)
        assert employee['email'] == 'test.user@example.com'
    
    def test_update_employee_email_validation(self, populated_db):
        """Test that email validation works on update."""
        from app.employee_manager import update_employee
        
        with pytest.raises(ValueError, match="Invalid email format"):
            update_employee(
                populated_db['employee_id'],
                email='invalid-email',
                db_path=populated_db['db_path']
            )
    
    def test_update_employee_date_validation(self, populated_db):
        """Test that date validation works on update."""
        from app.employee_manager import update_employee
        
        with pytest.raises(ValueError, match="YYYY-MM-DD"):
            update_employee(
                populated_db['employee_id'],
                hire_date='invalid-date',
                db_path=populated_db['db_path']
            )
    
    def test_update_employee_no_changes(self, populated_db):
        """Test updating with no changes returns True."""
        from app.employee_manager import update_employee
        
        result = update_employee(
            populated_db['employee_id'],
            db_path=populated_db['db_path']
        )
        assert result is True
    
    def test_update_employee_duplicate_email(self, populated_db):
        """Test that updating to an existing email raises error."""
        from app.employee_manager import add_employee, update_employee, DuplicateEmailError
        
        # Add another employee
        add_employee(
            first_name='Another',
            last_name='User',
            email='another@example.com',
            hire_date='2024-01-01',
            department='Test',
            db_path=populated_db['db_path']
        )
        
        # Try to update first employee with second employee's email
        with pytest.raises(DuplicateEmailError):
            update_employee(
                populated_db['employee_id'],
                email='another@example.com',
                db_path=populated_db['db_path']
            )


class TestProjectManagerAdditional:
    """Additional tests for project_manager module to increase coverage."""
    
    def test_add_project_missing_name(self, initialized_db):
        """Test that missing project name raises ValueError."""
        from app.project_manager import add_project
        
        with pytest.raises(ValueError, match="Project name is required"):
            add_project(
                project_name='',
                start_date='2024-01-01',
                db_path=initialized_db
            )
    
    def test_add_project_missing_start_date(self, initialized_db):
        """Test that missing start date raises ValueError."""
        from app.project_manager import add_project
        
        with pytest.raises(ValueError, match="Start date is required"):
            add_project(
                project_name='Test Project',
                start_date='',
                db_path=initialized_db
            )
    
    def test_add_project_invalid_end_date_format(self, initialized_db):
        """Test that invalid end date format raises ValueError."""
        from app.project_manager import add_project
        
        with pytest.raises(ValueError, match="end_date must be in YYYY-MM-DD"):
            add_project(
                project_name='Test Project',
                start_date='2024-01-01',
                end_date='invalid-date',
                db_path=initialized_db
            )
    
    def test_assign_employee_missing_role(self, populated_db):
        """Test that missing role raises ValueError."""
        from app.project_manager import assign_employee_to_project
        
        with pytest.raises(ValueError, match="Role is required"):
            assign_employee_to_project(
                employee_id=populated_db['employee_id'],
                project_id=populated_db['project_id'],
                role='',
                db_path=populated_db['db_path']
            )
    
    def test_assign_employee_invalid_date(self, populated_db):
        """Test that invalid assignment date raises ValueError."""
        from app.project_manager import assign_employee_to_project
        
        with pytest.raises(ValueError, match="assignment_date must be in YYYY-MM-DD"):
            assign_employee_to_project(
                employee_id=populated_db['employee_id'],
                project_id=populated_db['project_id'],
                role='Developer',
                assignment_date='invalid-date',
                db_path=populated_db['db_path']
            )
    
    def test_remove_nonexistent_assignment(self, populated_db):
        """Test removing non-existent assignment raises AssignmentError."""
        from app.project_manager import remove_employee_from_project, AssignmentError
        
        with pytest.raises(AssignmentError, match="No assignment found"):
            remove_employee_from_project(
                employee_id=populated_db['employee_id'],
                project_id=populated_db['project_id'],
                db_path=populated_db['db_path']
            )
    
    def test_update_project_no_changes(self, populated_db):
        """Test updating project with no changes returns True."""
        from app.project_manager import update_project
        
        result = update_project(
            populated_db['project_id'],
            db_path=populated_db['db_path']
        )
        assert result is True
    
    def test_update_project_invalid_start_date(self, populated_db):
        """Test updating project with invalid start date."""
        from app.project_manager import update_project
        
        with pytest.raises(ValueError, match="start_date must be in YYYY-MM-DD"):
            update_project(
                populated_db['project_id'],
                start_date='invalid-date',
                db_path=populated_db['db_path']
            )
    
    def test_update_project_invalid_end_date(self, populated_db):
        """Test updating project with invalid end date."""
        from app.project_manager import update_project
        
        with pytest.raises(ValueError, match="end_date must be in YYYY-MM-DD"):
            update_project(
                populated_db['project_id'],
                end_date='invalid-date',
                db_path=populated_db['db_path']
            )
    
    def test_update_project_invalid_status(self, populated_db):
        """Test updating project with invalid status."""
        from app.project_manager import update_project
        
        with pytest.raises(ValueError, match="Invalid status"):
            update_project(
                populated_db['project_id'],
                status='InvalidStatus',
                db_path=populated_db['db_path']
            )
    
    def test_get_projects_for_nonexistent_employee(self, initialized_db):
        """Test getting projects for non-existent employee."""
        from app.project_manager import get_projects_for_employee
        from app.employee_manager import EmployeeNotFoundError
        
        with pytest.raises(EmployeeNotFoundError):
            get_projects_for_employee(99999, db_path=initialized_db)


class TestPerformanceReviewerAdditional:
    """Additional tests for performance_reviewer module to increase coverage."""
    
    def test_submit_review_invalid_rating_type(self, mock_mongo_collection):
        """Test that non-numeric rating raises ValueError."""
        from app.performance_reviewer import submit_performance_review
        
        with pytest.raises(ValueError, match="must be a number"):
            submit_performance_review(
                employee_id=1,
                reviewer_name='Manager',
                overall_rating='not-a-number'
            )
    
    def test_submit_review_invalid_date(self, mock_mongo_collection):
        """Test that invalid date format raises ValueError."""
        from app.performance_reviewer import submit_performance_review
        
        with pytest.raises(ValueError, match="YYYY-MM-DD"):
            submit_performance_review(
                employee_id=1,
                reviewer_name='Manager',
                overall_rating=4.0,
                review_date='invalid-date'
            )
    
    def test_submit_review_with_additional_fields(self, mock_mongo_collection):
        """Test submitting review with additional custom fields."""
        from app.performance_reviewer import submit_performance_review
        
        review_id = submit_performance_review(
            employee_id=1,
            reviewer_name='Manager',
            overall_rating=4.0,
            additional_fields={'custom_field': 'custom_value'}
        )
        
        assert review_id is not None
    
    def test_submit_review_with_all_optional_fields(self, mock_mongo_collection):
        """Test submitting review with all optional fields."""
        from app.performance_reviewer import submit_performance_review
        
        review_id = submit_performance_review(
            employee_id=1,
            reviewer_name='Manager',
            overall_rating=4.5,
            strengths=['Leadership', 'Communication'],
            areas_for_improvement=['Time Management'],
            comments='Good performance overall.',
            goals_for_next_period=['Get certified', 'Lead a project'],
            review_date='2024-06-15'
        )
        
        assert review_id is not None
    
    def test_get_average_rating_no_reviews(self, mock_mongo_collection):
        """Test getting average rating when no reviews exist."""
        from app.performance_reviewer import get_average_rating_for_employee
        
        # Clear the mock storage
        mock_mongo_collection._storage.clear()
        
        rating_info = get_average_rating_for_employee(99999)
        
        assert rating_info['review_count'] == 0
        assert rating_info['average_rating'] is None


class TestReportsAdditional:
    """Additional tests for reports module to increase coverage."""
    
    def test_generate_department_summary_specific(self, populated_db):
        """Test generating department summary for a specific department."""
        from app.reports import generate_department_summary
        
        report = generate_department_summary(
            department='Engineering',
            db_path=populated_db['db_path']
        )
        
        assert 'DEPARTMENT SUMMARY REPORT' in report
        assert 'Engineering' in report
    
    def test_generate_department_summary_empty(self, initialized_db):
        """Test generating department summary when no employees exist."""
        from app.reports import generate_department_summary
        
        report = generate_department_summary(db_path=initialized_db)
        
        assert 'No departments found' in report
    
    def test_generate_project_status_report_empty(self, initialized_db):
        """Test generating project status report when no projects exist."""
        from app.reports import generate_project_status_report
        
        report = generate_project_status_report(db_path=initialized_db)
        
        assert 'No projects found' in report
    
    def test_generate_project_status_report_multiple_projects(self, initialized_db):
        """Test project status report with multiple projects."""
        from app.reports import generate_project_status_report
        from app.project_manager import add_project
        
        # Add projects with different statuses
        add_project('Project A', '2024-01-01', status='Planning', db_path=initialized_db)
        add_project('Project B', '2024-02-01', status='In Progress', db_path=initialized_db)
        add_project('Project C', '2024-03-01', '2024-12-31', status='Completed', db_path=initialized_db)
        
        report = generate_project_status_report(db_path=initialized_db)
        
        assert 'Project A' in report
        assert 'Project B' in report
        assert 'Project C' in report
        assert 'Total Projects: 3' in report


class TestDatabaseConnectionsAdditional:
    """Additional tests for db_connections module."""
    
    def test_sqlite_row_factory(self, temp_db_path):
        """Test that SQLite connection has row factory enabled."""
        from app.db_connections import get_sqlite_connection, initialize_sql_database
        
        initialize_sql_database(temp_db_path)
        conn = get_sqlite_connection(temp_db_path)
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO Employees (first_name, last_name, email, hire_date, department) VALUES (?, ?, ?, ?, ?)",
                      ('Test', 'User', 'test@test.com', '2024-01-01', 'Test'))
        conn.commit()
        
        cursor.execute("SELECT * FROM Employees WHERE email = ?", ('test@test.com',))
        row = cursor.fetchone()
        
        # Test that we can access by column name (row factory)
        assert row['first_name'] == 'Test'
        assert row['email'] == 'test@test.com'
        
        conn.close()
    
    def test_foreign_keys_enabled(self, temp_db_path):
        """Test that foreign keys are enabled."""
        from app.db_connections import get_sqlite_connection, initialize_sql_database
        
        initialize_sql_database(temp_db_path)
        conn = get_sqlite_connection(temp_db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA foreign_keys")
        result = cursor.fetchone()
        
        assert result[0] == 1  # Foreign keys enabled
        
        conn.close()


class TestPerformanceReviewerExtended:
    """Extended tests for performance_reviewer module."""
    
    def test_get_review_by_id(self, mock_mongo_collection):
        """Test retrieving a specific review by ID."""
        from app.performance_reviewer import submit_performance_review, get_review_by_id
        
        review_id = submit_performance_review(
            employee_id=1,
            reviewer_name='Manager',
            overall_rating=4.0
        )
        
        review = get_review_by_id(review_id)
        
        assert review is not None
        assert review['employee_id'] == 1
    
    def test_get_review_by_id_not_found(self, mock_mongo_collection):
        """Test that non-existent review raises ReviewNotFoundError."""
        from app.performance_reviewer import get_review_by_id, ReviewNotFoundError
        from bson import ObjectId
        
        # Clear storage first
        mock_mongo_collection._storage.clear()
        
        with pytest.raises(ReviewNotFoundError):
            get_review_by_id(str(ObjectId()))
    
    def test_update_review_success(self, mock_mongo_collection):
        """Test successful review update."""
        from app.performance_reviewer import submit_performance_review, update_review, get_review_by_id
        
        review_id = submit_performance_review(
            employee_id=1,
            reviewer_name='Manager',
            overall_rating=3.0
        )
        
        result = update_review(review_id, overall_rating=4.5, comments='Updated comment')
        
        assert result is True
    
    def test_update_review_no_changes(self, mock_mongo_collection):
        """Test update with no changes returns True."""
        from app.performance_reviewer import submit_performance_review, update_review
        
        review_id = submit_performance_review(
            employee_id=1,
            reviewer_name='Manager',
            overall_rating=4.0
        )
        
        result = update_review(review_id)
        
        assert result is True
    
    def test_update_review_invalid_rating(self, mock_mongo_collection):
        """Test that invalid rating on update raises ValueError."""
        from app.performance_reviewer import submit_performance_review, update_review
        
        review_id = submit_performance_review(
            employee_id=1,
            reviewer_name='Manager',
            overall_rating=4.0
        )
        
        with pytest.raises(ValueError, match="between 1 and 5"):
            update_review(review_id, overall_rating=6.0)
    
    def test_update_review_invalid_rating_type(self, mock_mongo_collection):
        """Test that non-numeric rating on update raises ValueError."""
        from app.performance_reviewer import submit_performance_review, update_review
        
        review_id = submit_performance_review(
            employee_id=1,
            reviewer_name='Manager',
            overall_rating=4.0
        )
        
        with pytest.raises(ValueError, match="must be a number"):
            update_review(review_id, overall_rating='invalid')
    
    def test_update_review_not_found(self, mock_mongo_collection):
        """Test updating non-existent review raises ReviewNotFoundError."""
        from app.performance_reviewer import update_review, ReviewNotFoundError
        from bson import ObjectId
        
        mock_mongo_collection._storage.clear()
        
        with pytest.raises(ReviewNotFoundError):
            update_review(str(ObjectId()), overall_rating=4.0)
    
    def test_delete_review_success(self, mock_mongo_collection):
        """Test successful review deletion."""
        from app.performance_reviewer import submit_performance_review, delete_review
        
        review_id = submit_performance_review(
            employee_id=1,
            reviewer_name='Manager',
            overall_rating=4.0
        )
        
        result = delete_review(review_id)
        
        assert result is True
    
    def test_delete_review_not_found(self, mock_mongo_collection):
        """Test deleting non-existent review raises ReviewNotFoundError."""
        from app.performance_reviewer import delete_review, ReviewNotFoundError
        from bson import ObjectId
        
        mock_mongo_collection._storage.clear()
        
        with pytest.raises(ReviewNotFoundError):
            delete_review(str(ObjectId()))
    
    def test_get_all_strengths_for_employee(self, mock_mongo_collection):
        """Test aggregating strengths for an employee."""
        from app.performance_reviewer import submit_performance_review, get_all_strengths_for_employee
        
        mock_mongo_collection._storage.clear()
        
        submit_performance_review(
            employee_id=1,
            reviewer_name='Manager A',
            overall_rating=4.0,
            strengths=['Communication', 'Leadership']
        )
        submit_performance_review(
            employee_id=1,
            reviewer_name='Manager B',
            overall_rating=4.5,
            strengths=['Communication', 'Technical Skills']
        )
        
        strengths = get_all_strengths_for_employee(1)
        
        assert isinstance(strengths, list)
    
    def test_get_all_areas_for_improvement(self, mock_mongo_collection):
        """Test aggregating areas for improvement for an employee."""
        from app.performance_reviewer import submit_performance_review, get_all_areas_for_improvement_for_employee
        
        mock_mongo_collection._storage.clear()
        
        submit_performance_review(
            employee_id=1,
            reviewer_name='Manager',
            overall_rating=4.0,
            areas_for_improvement=['Time Management', 'Documentation']
        )
        
        areas = get_all_areas_for_improvement_for_employee(1)
        
        assert isinstance(areas, list)
    
    def test_get_reviews_by_date_range(self, mock_mongo_collection):
        """Test retrieving reviews by date range."""
        from app.performance_reviewer import submit_performance_review, get_reviews_by_date_range
        
        mock_mongo_collection._storage.clear()
        
        submit_performance_review(
            employee_id=1,
            reviewer_name='Manager',
            overall_rating=4.0,
            review_date='2024-01-15'
        )
        submit_performance_review(
            employee_id=1,
            reviewer_name='Manager',
            overall_rating=4.5,
            review_date='2024-06-15'
        )
        
        reviews = get_reviews_by_date_range(
            employee_id=1,
            start_date='2024-01-01',
            end_date='2024-12-31'
        )
        
        assert isinstance(reviews, list)
    
    def test_get_reviews_by_date_range_no_filter(self, mock_mongo_collection):
        """Test retrieving all reviews without filters."""
        from app.performance_reviewer import submit_performance_review, get_reviews_by_date_range
        
        mock_mongo_collection._storage.clear()
        
        submit_performance_review(
            employee_id=1,
            reviewer_name='Manager',
            overall_rating=4.0
        )
        
        reviews = get_reviews_by_date_range()
        
        assert isinstance(reviews, list)


class TestReportsExtended:
    """Extended tests for reports module."""
    
    def test_generate_employee_performance_summary(self, populated_db, mock_mongo_collection):
        """Test generating employee performance summary."""
        from app.reports import generate_employee_performance_summary
        from app.performance_reviewer import submit_performance_review
        from app.project_manager import assign_employee_to_project
        
        # Assign employee to a project
        assign_employee_to_project(
            populated_db['employee_id'],
            populated_db['project_id'],
            'Developer',
            db_path=populated_db['db_path']
        )
        
        # Submit a review
        submit_performance_review(
            employee_id=populated_db['employee_id'],
            reviewer_name='Manager',
            overall_rating=4.5,
            strengths=['Communication'],
            areas_for_improvement=['Documentation'],
            comments='Great work!'
        )
        
        report = generate_employee_performance_summary(
            populated_db['employee_id'],
            db_path=populated_db['db_path']
        )
        
        assert 'EMPLOYEE PERFORMANCE SUMMARY' in report
        assert 'John' in report or 'Doe' in report  # Sample employee name
    
    def test_generate_employee_performance_summary_no_projects(self, populated_db, mock_mongo_collection):
        """Test performance summary for employee with no projects."""
        from app.reports import generate_employee_performance_summary
        
        mock_mongo_collection._storage.clear()
        
        report = generate_employee_performance_summary(
            populated_db['employee_id'],
            db_path=populated_db['db_path']
        )
        
        assert 'EMPLOYEE PERFORMANCE SUMMARY' in report
        assert 'No project assignments' in report
    
    def test_generate_employee_performance_summary_not_found(self, initialized_db):
        """Test performance summary for non-existent employee."""
        from app.reports import generate_employee_performance_summary
        from app.employee_manager import EmployeeNotFoundError
        
        with pytest.raises(EmployeeNotFoundError):
            generate_employee_performance_summary(99999, db_path=initialized_db)
    
    def test_export_employee_project_report_to_csv(self, populated_db, tmp_path):
        """Test exporting employee-project report to CSV."""
        from app.reports import export_employee_project_report_to_csv
        from app.project_manager import assign_employee_to_project
        import os
        
        # Create assignment
        assign_employee_to_project(
            populated_db['employee_id'],
            populated_db['project_id'],
            'Developer',
            db_path=populated_db['db_path']
        )
        
        csv_path = str(tmp_path / 'test_report.csv')
        result = export_employee_project_report_to_csv(
            filename=csv_path,
            db_path=populated_db['db_path']
        )
        
        assert os.path.exists(csv_path)
        assert result == csv_path


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=app', '--cov-report=term-missing'])
