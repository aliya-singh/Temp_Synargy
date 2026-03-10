"""
Web Application for Employee Management System
Flask-based web interface with role-based access control
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
import os
from datetime import datetime

# Import existing modules
from app.employee_manager import (
    add_employee, get_employee_by_id, list_all_employees, 
    update_employee, delete_employee, search_employees,
    DuplicateEmailError, EmployeeNotFoundError
)
from app.project_manager import (
    add_project, get_project_by_id, list_all_projects,
    assign_employee_to_project, remove_employee_from_project,
    get_projects_for_employee, get_employees_for_project,
    ProjectNotFoundError
)
from app.performance_reviewer import (
    submit_performance_review, get_performance_reviews_for_employee, 
    get_average_rating_for_employee
)
from app.db_connections import initialize_all_databases

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize databases on startup
initialize_all_databases()

# Allowed roles for portal access
ALLOWED_ROLES = ['HR', 'Project Manager']

# Demo users (in production, this should be in a database with hashed passwords)
DEMO_USERS = {
    'hr@company.com': {'password': 'hr123', 'role': 'HR', 'name': 'HR Admin'},
    'pm@company.com': {'password': 'pm123', 'role': 'Project Manager', 'name': 'Project Manager'}
}


def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(allowed_roles):
    """Decorator to require specific roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login'))
            if session['user']['role'] not in allowed_roles:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@app.route('/')
def index():
    """Redirect to login or dashboard"""
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        user = DEMO_USERS.get(email)
        
        if user and user['password'] == password:
            if user['role'] in ALLOWED_ROLES:
                session['user'] = {
                    'email': email,
                    'name': user['name'],
                    'role': user['role']
                }
                flash(f'Welcome, {user["name"]}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Access denied. Only HR and Project Managers can access this portal.', 'danger')
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout user"""
    session.pop('user', None)
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    try:
        employees = list_all_employees()
        projects = list_all_projects()
        
        stats = {
            'total_employees': len(employees),
            'total_projects': len(projects),
            'active_projects': len([p for p in projects if p['status'] == 'Active']),
            'departments': len(set(e['department'] for e in employees))
        }
        
        return render_template('dashboard.html', stats=stats)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'danger')
        return render_template('dashboard.html', stats={})


@app.route('/employees')
@login_required
def employees():
    """List all employees"""
    try:
        search = request.args.get('search', '').strip()
        if search:
            employee_list = search_employees(search)
        else:
            employee_list = list_all_employees()
        return render_template('employees.html', employees=employee_list, search=search)
    except Exception as e:
        flash(f'Error loading employees: {str(e)}', 'danger')
        return render_template('employees.html', employees=[], search='')


@app.route('/employees/add', methods=['GET', 'POST'])
@login_required
def add_employee_route():
    """Add new employee"""
    if request.method == 'POST':
        try:
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            email = request.form.get('email', '').strip()
            hire_date = request.form.get('hire_date', '').strip()
            department = request.form.get('department', '').strip()
            
            employee_id = add_employee(first_name, last_name, email, hire_date, department)
            flash(f'Employee {first_name} {last_name} added successfully!', 'success')
            return redirect(url_for('employees'))
        except DuplicateEmailError as e:
            flash(str(e), 'danger')
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(f'Error adding employee: {str(e)}', 'danger')
    
    return render_template('employee_form.html', action='Add', employee=None)


@app.route('/employees/<int:employee_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_employee_route(employee_id):
    """Edit employee"""
    if request.method == 'POST':
        try:
            first_name = request.form.get('first_name', '').strip() or None
            last_name = request.form.get('last_name', '').strip() or None
            email = request.form.get('email', '').strip() or None
            hire_date = request.form.get('hire_date', '').strip() or None
            department = request.form.get('department', '').strip() or None
            
            update_employee(employee_id, first_name, last_name, email, hire_date, department)
            flash('Employee updated successfully!', 'success')
            return redirect(url_for('employees'))
        except DuplicateEmailError as e:
            flash(str(e), 'danger')
        except EmployeeNotFoundError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(f'Error updating employee: {str(e)}', 'danger')
    
    try:
        employee = get_employee_by_id(employee_id)
        return render_template('employee_form.html', action='Edit', employee=employee)
    except EmployeeNotFoundError as e:
        flash(str(e), 'danger')
        return redirect(url_for('employees'))


@app.route('/employees/<int:employee_id>/delete', methods=['POST'])
@login_required
def delete_employee_route(employee_id):
    """Delete employee"""
    try:
        delete_employee(employee_id)
        flash('Employee deleted successfully!', 'success')
    except EmployeeNotFoundError as e:
        flash(str(e), 'danger')
    except Exception as e:
        flash(f'Error deleting employee: {str(e)}', 'danger')
    
    return redirect(url_for('employees'))


@app.route('/employees/<int:employee_id>')
@login_required
def view_employee(employee_id):
    """View employee details"""
    try:
        employee = get_employee_by_id(employee_id)
        projects = get_projects_for_employee(employee_id)
        reviews = get_performance_reviews_for_employee(employee_id)
        avg_rating_data = get_average_rating_for_employee(employee_id)
        
        # Extract just the average rating number
        avg_rating = avg_rating_data.get('average_rating') if avg_rating_data else None
        
        return render_template('employee_detail.html', 
                             employee=employee, 
                             projects=projects,
                             reviews=reviews,
                             avg_rating=avg_rating)
    except EmployeeNotFoundError as e:
        flash(str(e), 'danger')
        return redirect(url_for('employees'))
    except Exception as e:
        flash(f'Error loading employee: {str(e)}', 'danger')
        return redirect(url_for('employees'))


@app.route('/projects')
@login_required
def projects():
    """List all projects"""
    try:
        project_list = list_all_projects()
        return render_template('projects.html', projects=project_list)
    except Exception as e:
        flash(f'Error loading projects: {str(e)}', 'danger')
        return render_template('projects.html', projects=[])


@app.route('/projects/add', methods=['GET', 'POST'])
@login_required
def add_project_route():
    """Add new project"""
    if request.method == 'POST':
        try:
            project_name = request.form.get('project_name', '').strip()
            start_date = request.form.get('start_date', '').strip()
            end_date = request.form.get('end_date', '').strip() or None
            status = request.form.get('status', 'Planning').strip()
            
            project_id = add_project(project_name, start_date, end_date, status)
            flash(f'Project {project_name} added successfully!', 'success')
            return redirect(url_for('projects'))
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(f'Error adding project: {str(e)}', 'danger')
    
    return render_template('project_form.html', action='Add', project=None)


@app.route('/projects/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project_route(project_id):
    """Edit project"""
    if request.method == 'POST':
        try:
            project_name = request.form.get('project_name', '').strip() or None
            start_date = request.form.get('start_date', '').strip() or None
            end_date = request.form.get('end_date', '').strip() or None
            status = request.form.get('status', '').strip() or None
            
            from app.project_manager import update_project
            update_project(project_id, project_name, start_date, end_date, status)
            flash('Project updated successfully!', 'success')
            return redirect(url_for('projects'))
        except ProjectNotFoundError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(f'Error updating project: {str(e)}', 'danger')
    
    try:
        project = get_project_by_id(project_id)
        return render_template('project_form.html', action='Edit', project=project)
    except ProjectNotFoundError as e:
        flash(str(e), 'danger')
        return redirect(url_for('projects'))


@app.route('/projects/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project_route(project_id):
    """Delete project"""
    try:
        from app.project_manager import delete_project
        delete_project(project_id)
        flash('Project deleted successfully!', 'success')
    except ProjectNotFoundError as e:
        flash(str(e), 'danger')
    except Exception as e:
        flash(f'Error deleting project: {str(e)}', 'danger')
    
    return redirect(url_for('projects'))


@app.route('/projects/<int:project_id>')
@login_required
def view_project(project_id):
    """View project details"""
    try:
        project = get_project_by_id(project_id)
        employees = get_employees_for_project(project_id)
        all_employees = list_all_employees()
        
        return render_template('project_detail.html', 
                             project=project, 
                             employees=employees,
                             all_employees=all_employees)
    except ProjectNotFoundError as e:
        flash(str(e), 'danger')
        return redirect(url_for('projects'))
    except Exception as e:
        flash(f'Error loading project: {str(e)}', 'danger')
        return redirect(url_for('projects'))


@app.route('/projects/<int:project_id>/assign', methods=['POST'])
@login_required
def assign_employee_route(project_id):
    """Assign employee to project"""
    try:
        employee_id = int(request.form.get('employee_id'))
        role = request.form.get('role', '').strip()
        
        assign_employee_to_project(employee_id, project_id, role)
        flash('Employee assigned to project successfully!', 'success')
    except Exception as e:
        flash(f'Error assigning employee: {str(e)}', 'danger')
    
    return redirect(url_for('view_project', project_id=project_id))


@app.route('/projects/<int:project_id>/remove/<int:employee_id>', methods=['POST'])
@login_required
def remove_employee_route(project_id, employee_id):
    """Remove employee from project"""
    try:
        remove_employee_from_project(employee_id, project_id)
        flash('Employee removed from project successfully!', 'success')
    except Exception as e:
        flash(f'Error removing employee: {str(e)}', 'danger')
    
    return redirect(url_for('view_project', project_id=project_id))


@app.route('/reviews/add', methods=['GET', 'POST'])
@login_required
def add_review_route():
    """Add performance review"""
    if request.method == 'POST':
        try:
            employee_id = int(request.form.get('employee_id'))
            reviewer_name = request.form.get('reviewer_name', '').strip()
            overall_rating = float(request.form.get('overall_rating'))
            review_period = request.form.get('review_period', '').strip()
            strengths = request.form.get('strengths', '').strip()
            areas_for_improvement = request.form.get('areas_for_improvement', '').strip()
            goals = request.form.get('goals', '').strip()
            comments = request.form.get('comments', '').strip()
            
            # Convert text inputs to lists
            strengths_list = [s.strip() for s in strengths.split('\n') if s.strip()] if strengths else []
            improvements_list = [a.strip() for a in areas_for_improvement.split('\n') if a.strip()] if areas_for_improvement else []
            goals_list = [g.strip() for g in goals.split('\n') if g.strip()] if goals else []
            
            # Create additional fields for review_period
            additional_fields = {'review_period': review_period} if review_period else {}
            
            review_id = submit_performance_review(
                employee_id=employee_id,
                reviewer_name=reviewer_name,
                overall_rating=overall_rating,
                strengths=strengths_list,
                areas_for_improvement=improvements_list,
                goals_for_next_period=goals_list,
                comments=comments,
                additional_fields=additional_fields
            )
            flash('Performance review submitted successfully!', 'success')
            return redirect(url_for('view_employee', employee_id=employee_id))
        except Exception as e:
            flash(f'Error submitting review: {str(e)}', 'danger')
    
    try:
        employees = list_all_employees()
        return render_template('review_form.html', employees=employees)
    except Exception as e:
        flash(f'Error loading form: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))


@app.route('/reports')
@login_required
def reports_page():
    """Reports dashboard"""
    return render_template('reports.html')


@app.route('/reports/employee-projects')
@login_required
def employee_projects_report():
    """Employee-Project assignment report"""
    try:
        from app.reports import generate_employee_project_report
        import io
        import sys
        
        # Capture report output
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        
        generate_employee_project_report()
        
        report_output = buffer.getvalue()
        sys.stdout = old_stdout
        
        return render_template('report_view.html', 
                             title='Employee-Project Report',
                             report_content=report_output)
    except Exception as e:
        flash(f'Error generating report: {str(e)}', 'danger')
        return redirect(url_for('reports_page'))


@app.route('/reports/department-summary')
@login_required
def department_summary_report():
    """Department summary report"""
    try:
        from app.reports import generate_department_summary
        import io
        import sys
        
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        
        generate_department_summary()
        
        report_output = buffer.getvalue()
        sys.stdout = old_stdout
        
        return render_template('report_view.html',
                             title='Department Summary Report',
                             report_content=report_output)
    except Exception as e:
        flash(f'Error generating report: {str(e)}', 'danger')
        return redirect(url_for('reports_page'))


@app.route('/reports/project-status')
@login_required
def project_status_report():
    """Project status report"""
    try:
        from app.reports import generate_project_status_report
        import io
        import sys
        
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        
        generate_project_status_report()
        
        report_output = buffer.getvalue()
        sys.stdout = old_stdout
        
        return render_template('report_view.html',
                             title='Project Status Report',
                             report_content=report_output)
    except Exception as e:
        flash(f'Error generating report: {str(e)}', 'danger')
        return redirect(url_for('reports_page'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
