"""Create a sample SQLite database for testing the Database Query Tool."""
import sqlite3
from pathlib import Path

# Create the database in the project directory
db_dir = Path(__file__).parent / "sample_data"
db_dir.mkdir(exist_ok=True)
db_path = db_dir / "company.sqlite"

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Drop existing tables
cursor.executescript("""
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS salaries;
""")

# Create departments table
cursor.execute("""
CREATE TABLE departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    budget REAL NOT NULL
)
""")

# Create employees table
cursor.execute("""
CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    department_id INTEGER NOT NULL,
    salary REAL NOT NULL,
    hire_date DATE NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (department_id) REFERENCES departments(id)
)
""")

# Create projects table
cursor.execute("""
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    department_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    status TEXT NOT NULL DEFAULT 'active',
    budget REAL NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(id)
)
""")

# Create salaries table
cursor.execute("""
CREATE TABLE salaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    effective_date DATE NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
)
""")

# Insert departments
departments = [
    (1, "Engineering", "New York", 5000000.00),
    (2, "Marketing", "San Francisco", 2500000.00),
    (3, "Sales", "Chicago", 3000000.00),
    (4, "Human Resources", "Boston", 1500000.00),
    (5, "Finance", "New York", 2000000.00),
]
cursor.executemany("INSERT INTO departments VALUES (?, ?, ?, ?)", departments)

# Insert employees
employees = [
    (1, "Alice Zhang", "alice.zhang@company.com", 1, 95000.00, "2020-03-15", 1),
    (2, "Bob Chen", "bob.chen@company.com", 1, 82000.00, "2021-07-01", 1),
    (3, "Carol Wang", "carol.wang@company.com", 2, 75000.00, "2019-11-20", 1),
    (4, "David Liu", "david.liu@company.com", 3, 88000.00, "2022-01-10", 1),
    (5, "Eve Li", "eve.li@company.com", 4, 65000.00, "2020-06-01", 1),
    (6, "Frank Wu", "frank.wu@company.com", 1, 105000.00, "2018-09-15", 1),
    (7, "Grace Zhou", "grace.zhou@company.com", 5, 78000.00, "2021-04-01", 1),
    (8, "Henry Sun", "henry.sun@company.com", 3, 72000.00, "2023-02-14", 1),
    (9, "Ivy Huang", "ivy.huang@company.com", 2, 68000.00, "2022-08-01", 0),
    (10, "Jack Ma", "jack.ma@company.com", 1, 120000.00, "2017-12-01", 1),
]
cursor.executemany("INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?, ?)", employees)

# Insert projects
projects = [
    (1, "Platform Upgrade", 1, "2024-01-01", "2024-12-31", "active", 1500000.00),
    (2, "Mobile App Launch", 2, "2024-03-01", "2024-09-30", "active", 800000.00),
    (3, "CRM Integration", 3, "2024-02-01", "2024-08-31", "completed", 500000.00),
    (4, "Employee Portal", 4, "2024-05-01", None, "planning", 300000.00),
    (5, "Data Warehouse", 5, "2024-04-01", "2025-03-31", "active", 1200000.00),
]
cursor.executemany("INSERT INTO projects VALUES (?, ?, ?, ?, ?, ?, ?)", projects)

# Insert salaries
salaries = [
    (1, 1, 95000.00, "2024-01-01"),
    (2, 1, 90000.00, "2023-01-01"),
    (3, 2, 82000.00, "2024-01-01"),
    (4, 3, 75000.00, "2024-01-01"),
    (5, 4, 88000.00, "2024-01-01"),
    (6, 5, 65000.00, "2024-01-01"),
    (7, 6, 105000.00, "2024-01-01"),
    (8, 6, 100000.00, "2023-01-01"),
    (9, 7, 78000.00, "2024-01-01"),
    (10, 8, 72000.00, "2024-01-01"),
    (11, 10, 120000.00, "2024-01-01"),
    (12, 10, 115000.00, "2023-01-01"),
]
cursor.executemany("INSERT INTO salaries VALUES (?, ?, ?, ?)", salaries)

conn.commit()
conn.close()

print(f"Sample database created at: {db_path}")
print(f"Tables: departments, employees, projects, salaries")
print(f"URL to use: sqlite:///{db_path}")
