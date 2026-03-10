# Synergy - Employee Performance Tracker

A comprehensive Python-based system to manage employees, projects, and performance reviews using both SQL (SQLite) and NoSQL (MongoDB) databases.

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Technologies](#technologies)
- [Setup Instructions](#setup-instructions)
- [Running the Application](#running-the-application)
- [MongoDB Setup](#mongodb-setup)
- [Usage Guide](#usage-guide)
- [Testing](#testing)
- [API Reference](#api-reference)

---

## Features

### Employee Management
- Add new employees with basic details (name, email, department, hire date)
- View, update, and delete employee records
- Search employees by name, email, or department
- Duplicate email prevention

### Project Management
- Create projects with name, start/end dates, and status
- Track project statuses: Planning, In Progress, On Hold, Completed, Cancelled
- Assign employees to projects with specific roles
- View team compositions for each project

### Performance Reviews (NoSQL)
- Submit flexible performance reviews with ratings (1-5)
- Track strengths and areas for improvement
- Set goals for next review period
- Add custom fields without schema changes

### Reporting
- Employee-Project Assignment Reports
- Employee Performance Summaries
- Department Summaries
- Project Status Reports
- CSV Export functionality

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION LAYER                                 │
│                              (main.py - CLI)                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                           BUSINESS LOGIC LAYER                               │
│  ┌──────────────────┐ ┌──────────────────┐ ┌────────────────────────────┐   │
│  │ employee_manager │ │ project_manager  │ │ performance_reviewer       │   │
│  │ (CRUD Operations)│ │ (CRUD Operations)│ │ (CRUD Operations)          │   │
│  └──────────────────┘ └──────────────────┘ └────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         reports.py                                    │   │
│  │            (Report Generation, Data Aggregation)                      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────────┤
│                           DATA ACCESS LAYER                                  │
│                        (db_connections.py)                                   │
├───────────────────────────────┬─────────────────────────────────────────────┤
│      SQLite (Relational)      │           MongoDB (Document)                 │
│  ┌─────────────────────────┐  │  ┌────────────────────────────────────────┐ │
│  │ Employees Table         │  │  │ reviews Collection                     │ │
│  │ - employee_id (PK)      │  │  │ - employee_id                          │ │
│  │ - first_name            │  │  │ - reviewer_name                        │ │
│  │ - last_name             │  │  │ - overall_rating                       │ │
│  │ - email (UNIQUE)        │  │  │ - review_date                          │ │
│  │ - hire_date             │  │  │ - strengths[]                          │ │
│  │ - department            │  │  │ - areas_for_improvement[]              │ │
│  └─────────────────────────┘  │  │ - goals_for_next_period[]              │ │
│  ┌─────────────────────────┐  │  │ - comments                             │ │
│  │ Projects Table          │  │  │ - additional_fields{}                  │ │
│  │ - project_id (PK)       │  │  └────────────────────────────────────────┘ │
│  │ - project_name          │  │                                             │
│  │ - start_date            │  │  Why NoSQL for Reviews?                     │
│  │ - end_date              │  │  • Flexible schema for varying review types │
│  │ - status                │  │  • Easy to add new fields                   │
│  └─────────────────────────┘  │  • Good for document-centric data           │
│  ┌─────────────────────────┐  │  • No complex joins needed                  │
│  │ EmployeeProjects (M:N)  │  │                                             │
│  │ - assignment_id (PK)    │  │                                             │
│  │ - employee_id (FK)      │  │                                             │
│  │ - project_id (FK)       │  │                                             │
│  │ - role                  │  │                                             │
│  │ - assignment_date       │  │                                             │
│  └─────────────────────────┘  │                                             │
└───────────────────────────────┴─────────────────────────────────────────────┘
```

### Database Design Rationale

#### SQL (SQLite) for Structured Data:
- **Employees & Projects**: Fixed schema, well-defined relationships
- **ACID compliance**: Data integrity for HR records
- **Foreign Keys**: Maintain referential integrity
- **JOIN queries**: Efficient for relational queries

#### NoSQL (MongoDB) for Semi-Structured Data:
- **Performance Reviews**: Variable fields based on roles/departments
- **Schema flexibility**: Easy to add new review criteria
- **Document storage**: Natural fit for review documents
- **No migrations needed**: Adapt to changing requirements

---

## Project Structure

```
Synergy/
├── main.py                    # CLI entry point
├── company.db                 # SQLite database (auto-created)
├── requirement.txt            # Python dependencies
├── README.md                  # This file
├── LICENSE                    # Project license
├── app/
│   ├── __init__.py           # Package initialization
│   ├── db_connections.py     # Database connectivity
│   ├── employee_manager.py   # Employee CRUD operations
│   ├── project_manager.py    # Project CRUD operations
│   ├── performance_reviewer.py # Review CRUD operations
│   └── reports.py            # Report generation
└── test/
    ├── __init__.py           # Test package
    ├── conftest.py           # Pytest fixtures
    └── test1.py              # Comprehensive test suite
```

---

## Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.8+ | Application logic |
| SQLite | Built-in | Relational data storage |
| MongoDB | 4.4+ | Document data storage |
| pymongo | 4.6+ | MongoDB driver |
| pytest | 8.0+ | Testing framework |
| pytest-cov | 4.1+ | Code coverage |

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Synergy
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
.\venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirement.txt
```

Or install manually:
```bash
pip install pymongo pytest pytest-cov
```

### 4. Initialize Database

The SQLite database is automatically created on first run. To manually initialize:

```python
from app.db_connections import initialize_sql_database
initialize_sql_database()
```

---

## MongoDB Setup

### Option 1: MongoDB Atlas (Cloud - Recommended for Beginners)

1. Create a free account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new cluster (free tier available)
3. Create a database user with password
4. Get your connection string
5. Set environment variable:

```bash
export MONGO_URI="mongodb+srv://username:password@cluster.mongodb.net/"
```

### Option 2: Local MongoDB Installation

**macOS (using Homebrew):**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Ubuntu/Debian:**
```bash
sudo apt-get install -y mongodb
sudo systemctl start mongodb
```

**Windows:**
Download installer from [MongoDB Download Center](https://www.mongodb.com/try/download/community)

### Verify MongoDB Connection

```python
from app.db_connections import get_mongo_client
client = get_mongo_client()
print("MongoDB connected successfully!")
```

---

## Running the Application

```bash
python main.py
```

You'll see the main menu:

```
============================================================
  EMPLOYEE PERFORMANCE TRACKER
============================================================

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
```

---

## Usage Guide

### Adding an Employee

```
Enter your choice: 1

============================================================
  ADD EMPLOYEE
============================================================
First Name: John
Last Name: Doe
Email: john.doe@company.com
Hire Date (YYYY-MM-DD): 2024-01-15
Department: Engineering

✓ Employee added successfully! ID: 1
```

### Assigning Employee to Project

```
Enter your choice: 9

============================================================
  ASSIGN EMPLOYEE TO PROJECT
============================================================
Employee ID: 1
Project ID: 1
Role (e.g., Developer, Manager, QA): Senior Developer

✓ Employee assigned successfully! Assignment ID: 1
```

### Submitting Performance Review

```
Enter your choice: 13

============================================================
  SUBMIT PERFORMANCE REVIEW
============================================================
Employee ID: 1

Reviewing: John Doe
Your Name (Reviewer): Jane Smith
Overall Rating (1-5): 4.5

Enter strengths (one per line, empty line to finish):
  Strength: Technical expertise
  Strength: Team collaboration
  Strength: 

Enter areas for improvement (one per line, empty line to finish):
  Area: Time management
  Area: 

Additional Comments (optional): Excellent performance this quarter.

Enter goals for next period (one per line, empty line to finish):
  Goal: Lead the new microservices project
  Goal: 

✓ Review submitted successfully! ID: 507f1f77bcf86cd799439011
```

---

## Testing

### Run All Tests

```bash
pytest test/test1.py -v
```

### Run Tests with Coverage

```bash
pytest test/test1.py --cov=app --cov-report=term-missing
```

### Expected Coverage Output

```
Name                          Stmts   Miss  Cover
-------------------------------------------------
app/__init__.py                   6      0   100%
app/db_connections.py            67     38    43%
app/employee_manager.py         107      6    94%
app/performance_reviewer.py     167     16    90%
app/project_manager.py          169     10    94%
app/reports.py                  183      6    97%
-------------------------------------------------
TOTAL                           699     76    89%
```

**Note:** The lower coverage on `db_connections.py` is due to MongoDB connection functions that require an actual MongoDB instance to test fully.

---

## API Reference

### Employee Manager

```python
from app.employee_manager import (
    add_employee,
    get_employee_by_id,
    list_all_employees,
    update_employee,
    delete_employee,
    search_employees
)

# Add employee
emp_id = add_employee("John", "Doe", "john@example.com", "2024-01-15", "Engineering")

# Get employee
employee = get_employee_by_id(emp_id)

# List all
employees = list_all_employees()

# Update
update_employee(emp_id, department="Management")

# Delete
delete_employee(emp_id)

# Search
results = search_employees("Engineering")
```

### Project Manager

```python
from app.project_manager import (
    add_project,
    get_project_by_id,
    list_all_projects,
    assign_employee_to_project,
    remove_employee_from_project,
    get_projects_for_employee,
    get_employees_for_project,
    update_project,
    delete_project
)

# Add project
proj_id = add_project("Alpha", "2024-01-01", "2024-12-31", "In Progress")

# Assign employee
assign_employee_to_project(emp_id, proj_id, "Developer")

# Get projects for employee
projects = get_projects_for_employee(emp_id)

# Get employees for project
team = get_employees_for_project(proj_id)
```

### Performance Reviewer

```python
from app.performance_reviewer import (
    submit_performance_review,
    get_performance_reviews_for_employee,
    get_review_by_id,
    get_average_rating_for_employee,
    update_review,
    delete_review
)

# Submit review
review_id = submit_performance_review(
    employee_id=1,
    reviewer_name="Manager",
    overall_rating=4.5,
    strengths=["Communication", "Technical Skills"],
    areas_for_improvement=["Time Management"],
    comments="Great work!",
    goals_for_next_period=["Lead a project"]
)

# Get reviews
reviews = get_performance_reviews_for_employee(1)

# Get average rating
rating_info = get_average_rating_for_employee(1)
```

### Reports

```python
from app.reports import (
    generate_employee_project_report,
    generate_employee_performance_summary,
    generate_department_summary,
    generate_project_status_report,
    export_employee_project_report_to_csv
)

# Generate reports
generate_employee_project_report()
generate_employee_performance_summary(employee_id=1)
generate_department_summary()
generate_project_status_report()

# Export to CSV
export_employee_project_report_to_csv("report.csv")
```

---

## Error Handling

The application provides custom exceptions for better error handling:

```python
from app.employee_manager import DuplicateEmailError, EmployeeNotFoundError
from app.project_manager import ProjectNotFoundError, AssignmentError
from app.performance_reviewer import ReviewNotFoundError, MongoDBConnectionError
```

---

## License

See [LICENSE](LICENSE) file for details.

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest test/test1.py --cov=app`
5. Submit a pull request

---

## Author

Synergy Team


