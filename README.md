# Synergy — Employee Performance Tracker

> A comprehensive Python-based system to manage employees, projects, and performance reviews using both SQL (SQLite) and NoSQL (MongoDB) databases.

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Built--in-003B57?style=flat&logo=sqlite&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-4.4+-47A248?style=flat&logo=mongodb&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-8.0+-0A9EDC?style=flat&logo=pytest&logoColor=white)
![Coverage](https://img.shields.io/badge/Coverage-89%25-brightgreen?style=flat)

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Technologies](#technologies)
- [Setup Instructions](#setup-instructions)
- [MongoDB Setup](#mongodb-setup)
- [Running the Application](#running-the-application)
- [Usage Guide](#usage-guide)
- [Testing](#testing)
- [API Reference](#api-reference)
- [Error Handling](#error-handling)
- [Contributing](#contributing)
- [License](#license)

---

## Features

### 👤 Employee Management
- Add employees with name, email, department, and hire date
- View, update, and delete employee records
- Search by name, email, or department
- Duplicate email prevention enforced at the database level

### 📁 Project Management
- Create projects with name, start/end dates, and status
- Supported statuses: `Planning`, `In Progress`, `On Hold`, `Completed`, `Cancelled`
- Assign employees to projects with defined roles
- View full team compositions per project

### ⭐ Performance Reviews *(NoSQL)*
- Submit flexible reviews with ratings (1–5)
- Track strengths and areas for improvement
- Set goals for the next review period
- Add custom fields without schema changes

### 📊 Reporting
- Employee–Project assignment reports
- Employee performance summaries
- Department summaries
- Project status reports
- CSV export functionality

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          PRESENTATION LAYER                               │
│                            (main.py — CLI)                                │
├──────────────────────────────────────────────────────────────────────────┤
│                         BUSINESS LOGIC LAYER                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────────────┐  │
│  │ employee_manager│  │ project_manager │  │  performance_reviewer    │  │
│  │ (CRUD)          │  │ (CRUD)          │  │  (CRUD)                  │  │
│  └─────────────────┘  └─────────────────┘  └──────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │                          reports.py                                │   │
│  │               (Report Generation, Data Aggregation)                │   │
│  └───────────────────────────────────────────────────────────────────┘   │
├──────────────────────────────────────────────────────────────────────────┤
│                           DATA ACCESS LAYER                               │
│                          (db_connections.py)                              │
├────────────────────────────────┬─────────────────────────────────────────┤
│       SQLite (Relational)      │          MongoDB (Document)              │
│                                │                                          │
│  Employees                     │  reviews collection                      │
│  ├── employee_id  (PK)         │  ├── employee_id                         │
│  ├── first_name                │  ├── reviewer_name                       │
│  ├── last_name                 │  ├── overall_rating                      │
│  ├── email  (UNIQUE)           │  ├── review_date                         │
│  ├── hire_date                 │  ├── strengths[]                         │
│  └── department                │  ├── areas_for_improvement[]             │
│                                │  ├── goals_for_next_period[]             │
│  Projects                      │  ├── comments                            │
│  ├── project_id  (PK)          │  └── additional_fields{}                 │
│  ├── project_name              │                                          │
│  ├── start_date                │                                          │
│  ├── end_date                  │                                          │
│  └── status                    │                                          │
│                                │                                          │
│  EmployeeProjects (M:N)        │                                          │
│  ├── assignment_id  (PK)       │                                          │
│  ├── employee_id  (FK)         │                                          │
│  ├── project_id  (FK)          │                                          │
│  ├── role                      │                                          │
│  └── assignment_date           │                                          │
└────────────────────────────────┴─────────────────────────────────────────┘
```

### Design Rationale

| Concern | Choice | Why |
|---|---|---|
| Employees & Projects | **SQLite** | Fixed schema, ACID compliance, FK integrity, efficient JOINs |
| Performance Reviews | **MongoDB** | Variable fields per role/dept, no migrations, document-centric |

---

## Project Structure

```
Synergy/
├── main.py                      # CLI entry point
├── web_app.py                   # Web application entry point
├── company.db                   # SQLite database (auto-created)
├── requirement.txt              # Python dependencies
├── README.md
├── LICENSE
├── app/
│   ├── __init__.py
│   ├── db_connections.py        # Database connectivity
│   ├── employee_manager.py      # Employee CRUD operations
│   ├── project_manager.py       # Project CRUD operations
│   ├── performance_reviewer.py  # Review CRUD operations
│   └── reports.py               # Report generation
└── test/
    ├── __init__.py
    ├── conftest.py              # Pytest fixtures
    └── test1.py                 # Comprehensive test suite
```

---

## Technologies

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.8+ | Application logic |
| SQLite | Built-in | Relational data storage |
| MongoDB | 4.4+ | Document data storage |
| pymongo | 4.6+ | MongoDB Python driver |
| pytest | 8.0+ | Testing framework |
| pytest-cov | 4.1+ | Code coverage reporting |

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Synergy
```

### 2. Create a Virtual Environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
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

### 4. Initialize the Database

The SQLite database is created automatically on first run. To initialize it manually:

```python
from app.db_connections import initialize_sql_database
initialize_sql_database()
```

---

## MongoDB Setup

### Option 1: MongoDB Atlas *(Cloud — Recommended)*

1. Create a free account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new cluster (free tier available)
3. Add a database user with a password
4. Copy your connection string
5. Set the environment variable:

```bash
export MONGO_URI="mongodb+srv://username:password@cluster.mongodb.net/"
```

### Option 2: Local MongoDB

**macOS (Homebrew):**
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
Download the installer from the [MongoDB Download Center](https://www.mongodb.com/try/download/community). MongoDB Compass can also be used to manage a localhost connection visually.

### Verify the Connection

```python
from app.db_connections import get_mongo_client
client = get_mongo_client()
print("MongoDB connected successfully!")
```

---

## Running the Application

**CLI:**
```bash
python main.py
```

**Web:**
```bash
python web_app.py
```

The CLI presents the following menu on launch:

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

### Assigning an Employee to a Project

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

### Submitting a Performance Review

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

### Run with Coverage Report

```bash
pytest test/test1.py --cov=app --cov-report=term-missing
```

### Coverage Summary

```
Name                           Stmts   Miss  Cover
--------------------------------------------------
app/__init__.py                    6      0   100%
app/db_connections.py             67     38    43%
app/employee_manager.py          107      6    94%
app/performance_reviewer.py      167     16    90%
app/project_manager.py           169     10    94%
app/reports.py                   183      6    97%
--------------------------------------------------
TOTAL                            699     76    89%
```

> **Note:** The lower coverage on `db_connections.py` reflects MongoDB connection functions that require a live instance to test fully.

---

## API Reference

### Employee Manager

```python
from app.employee_manager import (
    add_employee, get_employee_by_id, list_all_employees,
    update_employee, delete_employee, search_employees
)

emp_id   = add_employee("John", "Doe", "john@example.com", "2024-01-15", "Engineering")
employee = get_employee_by_id(emp_id)
all_emps = list_all_employees()
           update_employee(emp_id, department="Management")
           delete_employee(emp_id)
results  = search_employees("Engineering")
```

### Project Manager

```python
from app.project_manager import (
    add_project, get_project_by_id, list_all_projects,
    assign_employee_to_project, remove_employee_from_project,
    get_projects_for_employee, get_employees_for_project,
    update_project, delete_project
)

proj_id  = add_project("Alpha", "2024-01-01", "2024-12-31", "In Progress")
           assign_employee_to_project(emp_id, proj_id, "Developer")
projects = get_projects_for_employee(emp_id)
team     = get_employees_for_project(proj_id)
```

### Performance Reviewer

```python
from app.performance_reviewer import (
    submit_performance_review, get_performance_reviews_for_employee,
    get_review_by_id, get_average_rating_for_employee,
    update_review, delete_review
)

review_id   = submit_performance_review(
    employee_id=1,
    reviewer_name="Manager",
    overall_rating=4.5,
    strengths=["Communication", "Technical Skills"],
    areas_for_improvement=["Time Management"],
    comments="Great work!",
    goals_for_next_period=["Lead a project"]
)
reviews     = get_performance_reviews_for_employee(1)
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

generate_employee_project_report()
generate_employee_performance_summary(employee_id=1)
generate_department_summary()
generate_project_status_report()
export_employee_project_report_to_csv("report.csv")
```

---

## Error Handling

Synergy exposes custom exceptions for precise error handling:

```python
from app.employee_manager     import DuplicateEmailError, EmployeeNotFoundError
from app.project_manager      import ProjectNotFoundError, AssignmentError
from app.performance_reviewer import ReviewNotFoundError, MongoDBConnectionError
```

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Run the test suite: `pytest test/test1.py --cov=app`
5. Submit a pull request

---

## License

See the [LICENSE](LICENSE) file for details.

---

## Author

Built with ❤️ by the **Synergy Team**