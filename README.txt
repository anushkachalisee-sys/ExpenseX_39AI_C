================================================================================
                         EXPENSEX - PERSONAL FINANCE MANAGER
                              Flask OOP Web Application
================================================================================

Project Name    : ExpenseX (FlaskApp-OOP)
Version         : 1.0 (Academic / Team Project)
Language        : Python 3.11+
Framework       : Flask 3.1
Database        : MySQL (via PyMySQL)
Architecture    : MVC + Object-Oriented Design (Routes -> Controllers -> Models)
Default URL     : http://127.0.0.1:5000
Document Type   : README.txt (Project Documentation)
Last Updated    : June 2026

================================================================================
TABLE OF CONTENTS
================================================================================

  1.  Project Overview
  2.  Key Features
  3.  Technology Stack
  4.  System Architecture
  5.  Prerequisites
  6.  Installation Guide
  7.  Environment Configuration (.env)
  8.  Database Setup
  9.  Running the Application
 10.  Default Login Credentials
 11.  Complete Project Structure
 12.  Application Routes Reference
 13.  Controllers Documentation
 14.  Models Documentation
 15.  Database Schema
 16.  Authentication and Authorization
 17.  CSRF Protection
 18.  Multi-Currency Support
 19.  User Panel Features (Detailed)
 20.  Admin Panel Features (Detailed)
 21.  Reports and Export Formats
 22.  Budget, Goals, and Achievements
 23.  Global Search
 24.  Frontend and Templates
 25.  Static Assets (CSS / JavaScript)
 26.  Testing Guide (pytest)
 27.  Troubleshooting
 28.  Security Considerations
 29.  Team and Contribution Areas
 30.  Git Branches Overview
 31.  Frequently Asked Questions (FAQ)
 32.  License and Academic Use

================================================================================
1. PROJECT OVERVIEW
================================================================================

ExpenseX is a full-stack personal finance management web application built with
Flask using Object-Oriented Programming principles. The application allows
registered users to track income and expenses, organize transactions with
categories, set budgets and savings goals, view analytical reports with charts,
and export financial data. A separate admin console provides platform-wide
management including user administration, audit logs, and global category
management.

The project is designed as a collaborative team assignment where different
members contributed specific modules (authentication, transactions, categories,
budget, reports, admin panel, testing). The codebase follows a clean separation
of concerns:

    Browser Request
         |
         v
    Routes (Blueprints)     -- URL mapping and decorator-based access control
         |
         v
    Controllers             -- Business logic, validation, flash messages
         |
         v
    Models                  -- Database queries (SQL via PyMySQL)
         |
         v
    MySQL Database

Templates (Jinja2) render HTML responses. Static CSS and JavaScript provide
the modern dark/light UI with charts powered by Chart.js on the reports and
admin dashboard pages.

================================================================================
2. KEY FEATURES
================================================================================

USER FEATURES:
  [x] User registration and login with secure password hashing
  [x] Personal dashboard with income/expense summary and health score
  [x] Login streak tracking and achievement unlocking
  [x] Income and expense transaction management (CRUD)
  [x] Transaction search across description, notes, category, amount, date
  [x] Custom and global categories (income / expense types)
  [x] Monthly and daily budget limits with overspend alerts
  [x] Savings goals with progress tracking and deadlines
  [x] Gamified achievements (milestones, streaks, goal completion)
  [x] Financial reports with interactive charts (pie, line, bar)
  [x] Report filtering: weekly, monthly, yearly, custom date range
  [x] Export reports as CSV, PDF, and Excel
  [x] Multi-currency display (NPR, INR, USD, GBP) — stored as NPR internally
  [x] User profile management (name, email, password, currency)
  [x] Dark / light theme toggle (persisted in localStorage)
  [x] Responsive sidebar navigation with FAB quick-add button

ADMIN FEATURES:
  [x] Admin dashboard with platform statistics and signup chart
  [x] Activity feed from audit log
  [x] User management (list, view detail, toggle active/inactive)
  [x] Change user roles (user / admin)
  [x] Delete users (with last-admin protection)
  [x] Platform-wide audit log with filters (month, user, type)
  [x] Export audit log to Excel
  [x] Global category management (add / delete system-wide categories)

================================================================================
3. TECHNOLOGY STACK
================================================================================

BACKEND:
  - Python 3.11+
  - Flask 3.1.0          Web framework and routing
  - PyMySQL 1.1.1        MySQL database connector
  - cryptography 44.0.0  Required by PyMySQL for secure connections
  - python-dotenv 1.0.1  Environment variable loading from .env file
  - flask-wtf 1.2.2      CSRF support utilities
  - Werkzeug             Password hashing (generate_password_hash)

REPORT EXPORT:
  - openpyxl 3.1.5       Excel (.xlsx) generation
  - reportlab 4.2.5      PDF report generation

TESTING:
  - pytest 8.3.4         Test runner (teacher-recommended style)
  - unittest               Standard library test framework (used inside test files)

FRONTEND:
  - Jinja2 templates       Server-side HTML rendering
  - Chart.js 4.4         Interactive charts on Reports and Admin pages
  - Feather Icons          SVG icon set via unpkg CDN
  - Google Fonts           Instrument Sans, Instrument Serif, JetBrains Mono
  - Custom CSS             style.css, user.css, admin.css
  - Vanilla JavaScript     main.js (theme, FAB, search, modals, sparklines)

DATABASE:
  - MySQL 8.x or MariaDB   Relational database
  - Database name default: flask_finance

================================================================================
4. SYSTEM ARCHITECTURE
================================================================================

The application uses a layered MVC-inspired architecture with OOP route classes:

  app/
    __init__.py           Application factory (create_app)
    auth.py               Auth decorators and password utilities
    currency.py           Currency conversion and formatting
    database.py           Database connection, migrations, seeding
    controllers/          Business logic classes (one per module)
    models/               Data access classes (SQL queries)
    routes/               Blueprint registration classes
    templates/            Jinja2 HTML templates
    static/               CSS, JavaScript, avatars

APPLICATION FACTORY PATTERN:
  run.py imports create_app() from app/__init__.py. On startup, create_app():
    1. Loads configuration from config.py and .env
    2. Creates all database tables (if not exist) via Database.create_tables()
    3. Seeds default admin user and global categories
    4. Registers all blueprints (auth, transactions, categories, budget,
       reports, admin)
    5. Sets up CSRF token generation, context processors, error handlers

BLUEPRINT REGISTRATION:
  Blueprint Name    URL Prefix           Route Class
  --------------    ----------           -----------
  auth              (none)               AuthRoutes
  transactions      /transactions        TransactionRoutes
  categories        /categories          CategoryRoutes
  budget            /budget              BudgetRoutes
  reports           /reports             ReportRoutes
  admin             /admin               AdminRoutes

REQUEST FLOW EXAMPLE (Add Expense):
  1. User submits POST /transactions/add
  2. TransactionRoutes.add() called (decorated with @user_required)
  3. user_required checks session for user_id and non-admin role
  4. TransactionController.add() validates CSRF, parses form, converts currency
  5. TransactionModel.create() inserts row into MySQL
  6. BudgetModel.check_and_unlock_achievements() may unlock badges
  7. log_activity() writes to activity_log table
  8. Flash message + redirect to expense list

================================================================================
5. PREREQUISITES
================================================================================

Before installing ExpenseX, ensure the following are available on your system:

  SOFTWARE                          MINIMUM VERSION    NOTES
  --------                          ---------------    -----
  Python                            3.11+              python --version
  pip                               latest             Package installer
  MySQL Server                      8.0+               Or MariaDB 10.5+
  Git                               any                For cloning repository
  Web Browser                       modern             Chrome, Firefox, Edge

OPTIONAL:
  - MySQL Workbench or phpMyAdmin for visual database management
  - VS Code or Cursor IDE for development
  - Postman for manual API/route testing (not required)

DISK SPACE:
  Approximately 200 MB including Python virtual environment and dependencies.

NETWORK:
  Internet required on first run for:
    - pip install -r requirements.txt
    - CDN resources (Chart.js, Feather Icons, Google Fonts)

================================================================================
6. INSTALLATION GUIDE
================================================================================

Follow these steps to set up ExpenseX from scratch on Windows, macOS, or Linux.

STEP 1 — CLONE THE REPOSITORY
  git clone <your-repository-url>
  cd FlaskApp-OOP

STEP 2 — CREATE A VIRTUAL ENVIRONMENT
  Windows:
    python -m venv venv
    venv\Scripts\activate

  macOS / Linux:
    python3 -m venv venv
    source venv/bin/activate

STEP 3 — INSTALL PYTHON DEPENDENCIES
  pip install -r requirements.txt

  Expected packages installed:
    Flask, pymysql, cryptography, flask-wtf, python-dotenv,
    openpyxl, reportlab, pytest

STEP 4 — CREATE ENVIRONMENT FILE
  Create a file named .env in the project root (see Section 7).

STEP 5 — SET UP MYSQL DATABASE
  Option A: Let the app auto-create tables on first run (recommended)
  Option B: Run setup_db.sql manually (see Section 8)

STEP 6 — RUN THE APPLICATION
  python run.py

  Open browser: http://127.0.0.1:5000

STEP 7 — VERIFY INSTALLATION
  - Visit /login and log in with default admin credentials (Section 10)
  - Or register a new user account at /register
  - Run tests: python -m pytest test/ -v

================================================================================
7. ENVIRONMENT CONFIGURATION (.env)
================================================================================

Create a file named .env in the project root directory with these variables:

  SECRET_KEY=your-random-secret-key-here-change-in-production
  MYSQL_HOST=localhost
  MYSQL_USER=root
  MYSQL_PASSWORD=your_mysql_password
  MYSQL_DATABASE=flask_finance
  FLASK_DEBUG=1
  FLASK_HOST=127.0.0.1
  FLASK_PORT=5000

VARIABLE DESCRIPTIONS:

  SECRET_KEY
    Used by Flask to sign session cookies. MUST be changed in production.
    Generate a strong key: python -c "import secrets; print(secrets.token_hex(32))"

  MYSQL_HOST
    Hostname of MySQL server. Use localhost for local development.

  MYSQL_USER
    MySQL username with CREATE/INSERT/SELECT/UPDATE/DELETE privileges.

  MYSQL_PASSWORD
    Password for the MySQL user. Leave empty if root has no password locally.

  MYSQL_DATABASE
    Name of the database. Default: flask_finance
    Also accepts MYSQL_DB as an alias.

  FLASK_DEBUG
    Set to 1 for development (auto-reload, detailed errors).
    Set to 0 in production.

  FLASK_HOST / FLASK_PORT
    Host and port for the development server (read by run.py).

IMPORTANT: Never commit .env to Git. It is listed in .gitignore.

================================================================================
8. DATABASE SETUP
================================================================================

OPTION A — AUTOMATIC (Recommended)
  The app calls Database.create_tables() on every startup via create_app().
  This will:
    - Create all tables if they do not exist
    - Run schema migrations (add missing columns)
    - Insert default admin user (admin@expensex.com)
    - Seed global categories (Salary, Food, Rent, etc.)

OPTION B — MANUAL SQL SCRIPT
  mysql -u root -p < setup_db.sql

  The setup_db.sql file:
    - Creates database flask_finance
    - Creates all 7 tables
    - Inserts default admin user
    - Inserts 8 global categories

TABLES CREATED:
  1. users           User accounts (regular + admin)
  2. categories      Income/expense categories (user-owned or global)
  3. transactions    All financial transactions
  4. budgets         Monthly/daily spending limits per user
  5. achievements    Unlocked user achievement badges
  6. goals           Savings goals with progress tracking
  7. activity_log    Audit trail for admin and system events

SCHEMA MIGRATIONS:
  database.py includes migrate_schema() which safely adds columns to existing
  databases without dropping data:
    - users.currency, users.is_active, users.avatar
    - transactions.is_recurring, transactions.recurrence, transactions.notes
    - categories.user_id nullable (for global categories)

================================================================================
9. RUNNING THE APPLICATION
================================================================================

DEVELOPMENT SERVER:
  python run.py

  Equivalent to:
    set FLASK_APP=run.py        (Windows)
    export FLASK_APP=run.py     (Linux/Mac)
    flask run

CUSTOM HOST/PORT (via .env):
  FLASK_HOST=0.0.0.0
  FLASK_PORT=8080

STOPPING THE SERVER:
  Press Ctrl+C in the terminal.

FIRST RUN CHECKLIST:
  [ ] MySQL service is running
  [ ] .env file exists with correct credentials
  [ ] Virtual environment is activated
  [ ] pip install -r requirements.txt completed successfully
  [ ] No port conflict on 5000

================================================================================
10. DEFAULT LOGIN CREDENTIALS
================================================================================

DEFAULT ADMIN ACCOUNT (auto-seeded on first run):

  Email    : admin@expensex.com
  Password : admin123
  Role     : admin

After login, admin users are redirected to: /admin/

REGULAR USERS:
  Register at /register with any email and password (minimum 6 characters).
  New users receive copies of global categories automatically on registration.

SECURITY WARNING:
  Change the default admin password immediately in production environments.
  The default password is for development and demonstration purposes only.

================================================================================
11. COMPLETE PROJECT STRUCTURE
================================================================================

FlaskApp-OOP/
|
|-- .env                          Environment variables (not in Git)
|-- .gitignore                    Git ignore rules
|-- config.py                     Flask configuration loader
|-- requirements.txt              Python dependencies
|-- run.py                        Application entry point
|-- setup_db.sql                  Manual database setup script
|-- README.txt                    This documentation file
|
|-- app/
|   |-- __init__.py               create_app() factory
|   |-- auth.py                   Decorators: login_required, user_required,
|   |                             admin_required; password hashing; CSRF
|   |-- currency.py               NPR/INR/USD/GBP conversion helpers
|   |-- database.py               Database class, migrations, seeding
|   |
|   |-- controllers/
|   |   |-- auth_controller.py    Login, register, dashboard, profile
|   |   |-- admin_controller.py   Admin dashboard, users, audit, categories
|   |   |-- budget_controller.py  Budget limits, goals, achievements
|   |   |-- category_controller.py  User category CRUD
|   |   |-- report_controller.py  Charts, filters, CSV/PDF/Excel export
|   |   |-- transaction_controller.py  Income/expense CRUD, search
|   |
|   |-- models/
|   |   |-- __init__.py
|   |   |-- admin.py              AdminModel — platform stats, user mgmt
|   |   |-- budget.py             BudgetModel — budgets, goals, achievements
|   |   |-- category.py           CategoryModel — category CRUD and queries
|   |   |-- transaction.py        TransactionModel — transaction queries
|   |   |-- user.py               UserModel — user account operations
|   |
|   |-- routes/
|   |   |-- auth_routes.py        AuthRoutes blueprint
|   |   |-- admin_routes.py       AdminRoutes blueprint
|   |   |-- budget_routes.py      BudgetRoutes blueprint
|   |   |-- category_routes.py    CategoryRoutes blueprint
|   |   |-- report_routes.py      ReportRoutes blueprint
|   |   |-- transaction_routes.py TransactionRoutes blueprint
|   |
|   |-- static/
|   |   |-- css/
|   |   |   |-- style.css         Core design system and components
|   |   |   |-- user.css          User panel extras (goals, reports filters)
|   |   |   |-- admin.css         Admin panel styling
|   |   |-- js/
|   |       |-- main.js           Theme, FAB, search, modals, sparklines
|   |
|   |-- templates/
|       |-- base_user.html        User layout (sidebar, topbar, FAB)
|       |-- base_admin.html       Admin layout
|       |-- auth/                 login, register, dashboard, profile
|       |-- admin/                dashboard, users, user_detail, audit,
|       |                         categories, profile
|       |-- budget/               index.html (budget + goals)
|       |-- categories/           list.html, form.html
|       |-- transactions/         income, expense, form, search, pagination
|       |-- reports/              index.html (charts + filters)
|       |-- components/           Reusable Jinja2 partials
|       |-- errors/               403, 404, 500 pages
|
|-- test/
    |-- __init__.py
    |-- stub_app.py               Shared Flask stubs for unit tests
    |-- test_flask.py             Teacher-style login_required tests
    |-- test_auth_controller.py
    |-- test_admin_controller.py
    |-- test_budget_controller.py
    |-- test_category_controller.py
    |-- test_transaction_controller.py
    |-- test_report_controller.py

================================================================================
12. APPLICATION ROUTES REFERENCE
================================================================================

AUTH ROUTES (Blueprint: auth)
  Method   URL                    Endpoint              Access
  ------   ---                    --------              ------
  GET      /                      auth.home             Public
  GET/POST /login                 auth.login            Public
  GET/POST /register              auth.register         Public
  GET      /logout                 auth.logout           Public
  GET      /dashboard              auth.dashboard        User only
  GET/POST /profile                auth.profile          Login required
  POST     /profile/currency       auth.set_currency     User only

TRANSACTION ROUTES (Blueprint: transactions, prefix: /transactions)
  Method   URL                              Endpoint                    Access
  ------   ---                              --------                    ------
  GET      /transactions/income             transactions.list_income    User
  GET      /transactions/expense            transactions.list_expense   User
  GET      /transactions/search             transactions.search         User
  GET/POST /transactions/add                transactions.add            User
  GET/POST /transactions/edit/<id>          transactions.edit           User
  POST     /transactions/delete/<id>        transactions.delete         User

CATEGORY ROUTES (Blueprint: categories, prefix: /categories)
  Method   URL                              Endpoint                    Access
  ------   ---                              --------                    ------
  GET      /categories/                     categories.list_all         User
  GET/POST /categories/add                  categories.add              User
  GET/POST /categories/edit/<id>            categories.edit             User
  POST     /categories/delete/<id>          categories.delete           User

BUDGET ROUTES (Blueprint: budget, prefix: /budget)
  Method   URL                              Endpoint                    Access
  ------   ---                              --------                    ------
  GET      /budget/                         budget.index                User
  POST     /budget/set                      budget.set_budget           User
  POST     /budget/goal/add                 budget.add_goal             User
  POST     /budget/goal/update/<id>         budget.update_goal          User
  POST     /budget/goal/delete/<id>         budget.delete_goal          User

REPORT ROUTES (Blueprint: reports, prefix: /reports)
  Method   URL                              Endpoint                    Access
  ------   ---                              --------                    ------
  GET      /reports/                        reports.index               User
  GET      /reports/export/csv              reports.export_csv          User
  GET      /reports/export/pdf              reports.export_pdf          User
  GET      /reports/export/excel            reports.export_excel        User

ADMIN ROUTES (Blueprint: admin, prefix: /admin)
  Method   URL                              Endpoint                    Access
  ------   ---                              --------                    ------
  GET      /admin/                          admin.dashboard             Admin
  GET      /admin/users                     admin.users                 Admin
  GET      /admin/users/<id>                admin.user_detail           Admin
  POST     /admin/users/<id>/toggle         admin.toggle_status         Admin
  POST     /admin/users/<id>/role           admin.change_role           Admin
  POST     /admin/users/<id>/delete         admin.delete_user           Admin
  GET      /admin/audit                     admin.audit_log             Admin
  GET      /admin/audit/export/excel        admin.audit_export          Admin
  GET      /admin/categories                admin.global_categories     Admin
  POST     /admin/categories/add            admin.add_global_category   Admin
  POST     /admin/categories/<id>/delete    admin.delete_global_category Admin

TOTAL REGISTERED ROUTES: 30+ (excluding static files and error handlers)

================================================================================
13. CONTROLLERS DOCUMENTATION
================================================================================

Each controller is a Python class with methods called by route handlers.
Controllers handle form parsing, validation, flash messages, and rendering.

AUTH CONTROLLER (auth_controller.py)
  home()           Redirect to dashboard or login based on session
  login()          Authenticate user, set session, update streak
  register()       Create account, copy global categories, redirect to login
  logout()         Clear session
  dashboard()      Build dashboard stats, sparklines, health score, alerts
  profile()        Update name, email, password, currency
  update_currency() Quick currency change from sidebar pills

TRANSACTION CONTROLLER (transaction_controller.py)
  list_income()    Paginated income list with month/category filters
  list_expense()   Paginated expense list with month/category filters
  search()         Full-text search across all user transactions
  add()            Create new income or expense transaction
  edit()           Update existing transaction
  delete()         Remove transaction and log activity

CATEGORY CONTROLLER (category_controller.py)
  list_all()       Show all user + global categories with transaction counts
  add()            Create user-owned category
  edit()           Update user category (global categories are read-only)
  delete()         Delete user category, nullify linked transactions

BUDGET CONTROLLER (budget_controller.py)
  index()          Show budget limits, monthly summary, goals, achievements
  set_budget()     Save monthly and daily spending limits
  add_goal()       Create savings goal with optional deadline
  update_goal()    Update goal progress; unlock achievement on completion
  delete_goal()    Remove savings goal

REPORT CONTROLLER (report_controller.py)
  index()          Render charts: category pie, daily line, 6-month bar
  export_csv()     Download all transactions as CSV
  export_pdf()     Download formatted PDF report (ReportLab)
  export_excel()   Download Excel workbook (openpyxl)

ADMIN CONTROLLER (admin_controller.py)
  dashboard()      Platform stats, activity feed, signup chart, top users
  users()          Paginated user list with role/status controls
  user_detail()    Single user profile with transaction history
  toggle_status()  Activate or deactivate user account
  change_role()    Promote/demote between user and admin roles
  delete_user()    Delete user (blocks deletion of last admin)
  audit_log()      Filtered platform-wide transaction audit view
  audit_export_excel() Export audit data to Excel
  global_categories() List system-wide categories
  add_global_category() Create global category
  delete_global_category() Remove global category

================================================================================
14. MODELS DOCUMENTATION
================================================================================

Models encapsulate all SQL queries. Each model class uses static methods and
opens/closes a Database connection per call.

USER MODEL (user.py)
  find_by_email(), find_by_id(), create(), update_profile()
  get_totals(), update_streak(), is_active_user(), email_exists_for_other()

TRANSACTION MODEL (transaction.py)
  PER_PAGE = 20 (pagination constant)
  count_by_type(), list_by_type(), find_by_id(), create(), update(), delete()
  get_monthly_summary(), get_prev_month_summary(), get_today_expense()
  get_recent(), get_all_for_export(), search(), count_search()
  get_expense_by_category(), get_daily_expenses(), get_six_month_comparison()
  get_summary_for_range(), get_expense_by_category_range()

CATEGORY MODEL (category.py)
  get_all(), get_all_with_counts(), get_by_type(), find_by_id()
  duplicate_exists(), create(), update(), delete()
  copy_global_to_user() — called on registration

BUDGET MODEL (budget.py)
  ACHIEVEMENTS — list of achievement definitions with check lambdas
  get_budget(), upsert_budget(), get_goals(), find_goal()
  add_goal(), update_goal(), delete_goal()
  get_achievements(), unlock_achievement(), check_and_unlock_achievements()
  unlock_goal_achievement()

ADMIN MODEL (admin.py)
  PER_PAGE = 20
  get_all_users(), count_users(), get_user_by_id()
  toggle_user_status(), change_user_role(), count_admins(), delete_user()
  get_user_transactions(), get_all_transactions(), count_all_transactions()
  get_platform_stats(), get_activity_feed(), get_signups_by_month()
  get_top_active_users(), get_global_categories()
  create_global_category(), delete_global_category(), global_category_exists()

================================================================================
15. DATABASE SCHEMA
================================================================================

USERS TABLE
  id            INT AUTO_INCREMENT PRIMARY KEY
  name          VARCHAR(100) NOT NULL
  email         VARCHAR(150) UNIQUE NOT NULL
  password      VARCHAR(255) NOT NULL (Werkzeug hash or legacy SHA256)
  role          ENUM('user', 'admin') DEFAULT 'user'
  is_active     TINYINT(1) DEFAULT 1
  avatar        VARCHAR(255) NULL
  currency      VARCHAR(10) DEFAULT 'NPR'
  streak        INT DEFAULT 0
  last_login    DATE
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP

CATEGORIES TABLE
  id            INT AUTO_INCREMENT PRIMARY KEY
  user_id       INT NULL (NULL = global category)
  name          VARCHAR(100) NOT NULL
  type          ENUM('income', 'expense') NOT NULL
  created_at    TIMESTAMP

TRANSACTIONS TABLE
  id            INT AUTO_INCREMENT PRIMARY KEY
  user_id       INT NOT NULL (FK -> users)
  category_id   INT NULL (FK -> categories, SET NULL on delete)
  type          ENUM('income', 'expense') NOT NULL
  amount        DECIMAL(12,2) NOT NULL (stored in NPR)
  description   VARCHAR(255)
  notes         TEXT
  date          DATE NOT NULL
  is_recurring  TINYINT(1) DEFAULT 0
  recurrence    VARCHAR(20)
  created_at    TIMESTAMP

BUDGETS TABLE
  id            INT AUTO_INCREMENT PRIMARY KEY
  user_id       INT UNIQUE NOT NULL (FK -> users)
  monthly_limit DECIMAL(12,2) DEFAULT 0
  daily_limit   DECIMAL(12,2) DEFAULT 0
  updated_at    TIMESTAMP

GOALS TABLE
  id              INT AUTO_INCREMENT PRIMARY KEY
  user_id         INT NOT NULL (FK -> users)
  title           VARCHAR(100) NOT NULL
  target_amount   DECIMAL(12,2) NOT NULL
  current_amount  DECIMAL(12,2) DEFAULT 0
  deadline        DATE
  completed       TINYINT(1) DEFAULT 0
  created_at      TIMESTAMP

ACHIEVEMENTS TABLE
  id            INT AUTO_INCREMENT PRIMARY KEY
  user_id       INT NOT NULL (FK -> users)
  title         VARCHAR(100) NOT NULL
  description   VARCHAR(255)
  icon          VARCHAR(50) DEFAULT 'award'
  unlocked_at   TIMESTAMP

ACTIVITY_LOG TABLE
  id            INT AUTO_INCREMENT PRIMARY KEY
  user_id       INT NULL (FK -> users, SET NULL on delete)
  user_name     VARCHAR(100)
  action        VARCHAR(100) NOT NULL
  detail        VARCHAR(255)
  created_at    TIMESTAMP

GLOBAL CATEGORIES (seeded automatically):
  Income  : Salary, Freelance
  Expense : Food, Transport, Rent, Utilities, Shopping, Healthcare

================================================================================
16. AUTHENTICATION AND AUTHORIZATION
================================================================================

SESSION-BASED AUTH:
  Flask sessions store: user_id, user_name, role, currency, streak, csrf_token
  Session cookie is signed with SECRET_KEY from config.

THREE ACCESS DECORATORS (app/auth.py):

  @login_required
    Requires user_id in session.
    Used for: profile page (accessible by both users and admins).
    Redirects guests to /login.

  @user_required
    Requires user_id AND role != 'admin'.
    Used for: all user panel pages (dashboard, transactions, budget, etc.).
    Redirects guests to /login.
    Redirects admins to /admin/.

  @admin_required
    Requires user_id AND role == 'admin'.
    Used for: all admin panel pages.
    Redirects guests to /login.
    Redirects regular users to /dashboard with "Access denied" flash.

PASSWORD SECURITY:
  New passwords hashed with Werkzeug generate_password_hash (pbkdf2/sha256).
  Legacy SHA256 hashes (from setup_db.sql) still verified for backward compatibility.
  Minimum password length: 6 characters (enforced in register and profile).

LOGIN STREAK:
  On each login, UserModel.update_streak() compares last_login date with today.
  Consecutive daily logins increment streak counter stored in session and database.

INACTIVE USERS:
  Admin can deactivate accounts (is_active = 0).
  Deactivated users cannot log in — blocked in AuthController.login().

================================================================================
17. CSRF PROTECTION
================================================================================

Cross-Site Request Forgery protection is implemented manually:

  1. before_request in create_app() ensures session["csrf_token"] exists
  2. All POST forms include: <input type="hidden" name="csrf_token" value="...">
  3. Controllers call validate_csrf() before processing POST data
  4. validate_csrf() compares form token with session token using secrets.compare_digest

If CSRF validation fails, a flash message is shown and the action is rejected.
This protects: transaction create/edit/delete, category CRUD, budget/goal forms,
admin user management actions, profile updates.

================================================================================
18. MULTI-CURRENCY SUPPORT
================================================================================

All amounts are stored internally in NPR (Nepali Rupee).
Display currency is user-selectable and stored in session + users.currency column.

SUPPORTED CURRENCIES:
  Code   Symbol   Name              Display Rate (vs NPR)
  ----   ------   ----              ---------------------
  NPR    Rs.      Nepali Rupee      1.0 (base)
  INR    Rs.      Indian Rupee      0.628
  USD    $        US Dollar         0.00752
  GBP    GBP      British Pound     0.00593

HELPER FUNCTIONS (app/currency.py):
  format_currency(amount_npr, code)  Format for display (supports Cr/L suffixes)
  display_amount(amount_npr, code)   Convert NPR to display value for form inputs
  to_npr(amount_display, code)       Convert user input back to NPR for storage

Currency can be changed from:
  - Sidebar currency pills (POST /profile/currency)
  - Profile page currency selector
  - Reports charts auto-convert using session currency rate

================================================================================
19. USER PANEL FEATURES (DETAILED)
================================================================================

DASHBOARD (/dashboard)
  - Four stat cards: Total Income, Total Expenses, Balance, Login Streak
  - Trend percentages vs previous month with sparkline mini-charts
  - Monthly analytics bars (income, expense, budget usage, remaining)
  - Budget overspend alerts (monthly and daily limit warnings)
  - Recent transactions table (last 5 entries)
  - Financial health score arc (0-100 based on income/expense ratio)
  - Unlocked achievements display

INCOME & EXPENSES (/transactions/income, /transactions/expense)
  - Filter by month and category
  - Paginated table (20 items per page)
  - Add, edit, delete with CSRF protection
  - Recurring transaction support (optional)
  - Notes field for additional details
  - Page total amount displayed in header

SEARCH (/transactions/search?q=...)
  - Global topbar search — press Enter to search
  - Searches: description, notes, category name, type, amount, date
  - Shows both income and expense results in one table
  - Paginated results

CATEGORIES (/categories/)
  - Grid view of all categories with transaction counts
  - Global categories shown with dashed border (read-only)
  - User categories: add, edit, delete
  - Separate income and expense type per category

BUDGET & GOALS (/budget/)
  - Set monthly and daily spending limits
  - View current month income, expenses, today's spending
  - Savings goals with progress rings, bars, and deadlines
  - Update goal progress inline via expandable details panel
  - Achievement gallery (6 predefined achievements)

REPORTS (/reports/)
  - Period filter: Monthly, Weekly, Yearly, Custom date range
  - Summary cards: Period Income, Period Expense, Net
  - Doughnut chart: Expenses by Category
  - Line chart: Daily Expenses for selected month
  - Bar chart: 6-Month Income vs Expense comparison
  - Export buttons: CSV, PDF, Excel

PROFILE (/profile)
  - Update name, email, password
  - Change display currency
  - Admin users see admin/profile.html template variant

================================================================================
20. ADMIN PANEL FEATURES (DETAILED)
================================================================================

ADMIN OVERVIEW (/admin/)
  - Platform statistics: total users, active users, transactions, volume
  - Activity feed (last 15 actions from activity_log)
  - User signups bar chart (last 6 months, Chart.js)
  - Most active users table (top 5 by transaction count)

USER MANAGEMENT (/admin/users)
  - Paginated user list (20 per page)
  - Live search by name or email (JavaScript filter)
  - Inline role dropdown (user / admin) with instant POST
  - Toggle active/inactive status
  - View user detail page
  - Delete user (cannot delete self or last admin)

USER DETAIL (/admin/users/<id>)
  - User info: name, email, role, status, join date
  - Financial totals: income, expense, balance
  - Full transaction history table
  - Delete user button with confirmation

AUDIT LOG (/admin/audit)
  - All platform transactions with user name
  - Filters: month, user, transaction type
  - Paginated (30 per page)
  - Export to Excel (/admin/audit/export/excel)

GLOBAL CATEGORIES (/admin/categories)
  - List all system-wide categories (user_id IS NULL)
  - Add new global category (name + type)
  - Delete global category (nullifies linked transaction category_id)
  - Global categories are copied to new users on registration

================================================================================
21. REPORTS AND EXPORT FORMATS
================================================================================

CSV EXPORT (/reports/export/csv)
  Columns: Date, Type, Category, Amount (NPR), Description, Notes
  Content-Type: text/csv
  Filename: expensex_report.csv

PDF EXPORT (/reports/export/pdf)
  Generated with ReportLab
  Styled dark-theme table matching app design
  Currency formatted using user's display currency
  Filename: expensex_report.pdf

EXCEL EXPORT (/reports/export/excel)
  Generated with openpyxl
  Styled header row, auto-sized columns
  Sheet name: Transactions
  Filename: expensex_report.xlsx

ADMIN AUDIT EXCEL (/admin/audit/export/excel)
  Columns: Date, User, Type, Amount (NPR), Category, Description
  Respects current audit log filters (month, user, type)
  Filename: expensex_audit.xlsx

================================================================================
22. BUDGET, GOALS, AND ACHIEVEMENTS
================================================================================

BUDGET LIMITS:
  Stored per user in budgets table (one row per user).
  Limits entered in display currency, converted to NPR before saving.
  Dashboard shows alerts when monthly or daily limits are reached/exceeded.

SAVINGS GOALS:
  Stored in goals table with title, target_amount, current_amount, deadline.
  Progress calculated as percentage (capped at 100%).
  Completing a goal (current >= target) sets completed = 1.
  Completing first goal unlocks "Goal Achiever" achievement.

ACHIEVEMENTS (6 predefined in BudgetModel.ACHIEVEMENTS):
  1. Income Milestone    — Earned NPR 10,000+ total income
  2. Expense Tracker     — Tracked NPR 500+ in expenses
  3. 7-Day Streak        — Logged in 7 days in a row
  4. 30-Day Streak       — Logged in 30 days in a row
  5. Saver               — Total income exceeds total expenses
  6. Goal Achiever       — Completed a savings goal

Achievements checked automatically after transactions and on dashboard load.
Unlocked achievements stored in achievements table and shown on dashboard/budget.

================================================================================
23. GLOBAL SEARCH
================================================================================

The topbar search input (id="global-search") is available on all user pages.

HOW TO USE:
  1. Type a search term in the topbar search box
  2. Press Enter
  3. Redirected to /transactions/search?q=your+term

SEARCH MATCHES:
  - Transaction description
  - Transaction notes
  - Category name
  - Transaction type (income / expense)
  - Amount (numeric partial match)
  - Date (YYYY-MM-DD partial match)

Results show paginated table with edit/delete actions for each match.
Search query is preserved in the topbar input on the results page.

================================================================================
24. FRONTEND AND TEMPLATES
================================================================================

TEMPLATE INHERITANCE:
  User pages extend base_user.html
  Admin pages extend base_admin.html
  Error pages (403, 404, 500) are standalone

BASE USER LAYOUT (base_user.html):
  - Fixed sidebar with logo, user card, navigation sections
  - Topbar with page title, global search, topbar actions block
  - Flash message stack
  - FAB (Floating Action Button) for quick add income/expense
  - Confirm modal for destructive actions
  - Currency pills in sidebar footer

REUSABLE COMPONENTS (templates/components/):
  alert.html, badge.html, confirm_modal.html, currency_selector.html,
  empty_state.html, export_buttons.html, form_group.html,
  month_analytics.html, nav_item.html, page_header.html, pagination.html,
  stat_card.html, tab_panels.html, table.html, topbar_actions.html,
  user_avatar.html

JINJA2 GLOBALS (injected via context_processor):
  today, currencies, format_currency, display_amount, app_name,
  alert_count, user_initials

ERROR PAGES:
  403 — Access Forbidden (links back to appropriate dashboard)
  404 — Page Not Found
  500 — Server Error

================================================================================
25. STATIC ASSETS (CSS / JAVASCRIPT)
================================================================================

style.css — Core Design System:
  - CSS custom properties for colors, spacing, typography, shadows
  - Dark theme default; .light class on <html> enables light mode
  - Components: buttons, cards, forms, tables, badges, alerts, modals
  - Stat cards, chart layouts, pagination, filter bars
  - Responsive breakpoints at 900px and 640px

user.css — User Panel Extras:
  - Reports filter compact layout
  - Goals section: cards, progress rings, progress bars, edit panels
  - Chart sizing overrides

admin.css — Admin Panel:
  - Admin badge, admin avatar styling
  - Admin stat grid, activity feed, admin layout
  - Admin topbar badge

main.js — Client-Side Logic:
  - Theme toggle with localStorage persistence (key: expensex-theme)
  - FAB open/close menu
  - Sidebar mobile toggle
  - Auto-dismiss flash alerts after 5 seconds
  - Global search Enter key handler (redirect to /transactions/search)
  - Admin user table live filter (user-search input)
  - Confirm modal for forms with data-confirm attribute
  - Dashboard sparkline animation (drawSparkline)
  - Health score arc animation (animateHealthScore)

================================================================================
26. TESTING GUIDE (pytest)
================================================================================

TEST LOCATION: test/ folder in project root

TEST FILES:
  test_flask.py                  Teacher-style @login_required basics (2 tests)
  test_auth_controller.py        User dashboard access (3 tests)
  test_admin_controller.py       Admin @admin_required access (4 tests)
  test_budget_controller.py      Budget page access (2 tests)
  test_category_controller.py    Categories page access (2 tests)
  test_transaction_controller.py Transaction pages access (3 tests)
  test_report_controller.py      Reports page access (2 tests)
  stub_app.py                    Shared Flask stub routes for url_for

TEST STYLE:
  Simple unittest.TestCase classes (matching teacher's example).
  Each test builds a minimal Flask app with stub auth/admin blueprints.
  Tests verify HTTP status codes: 302 (redirect) and 200 (success).
  No database or MySQL required for tests.

RUN ALL TESTS:
  python -m pytest test/ -v

RUN SINGLE FILE (teacher style):
  python -m pytest test/test_flask.py -v

RUN SPECIFIC CONTROLLER TESTS:
  python -m pytest test/test_admin_controller.py -v
  python -m pytest test/test_transaction_controller.py -v

EXPECTED OUTPUT:
  18 passed (all test files combined)

USING unittest INSTEAD OF pytest:
  python -m unittest discover -s test -v

================================================================================
27. TROUBLESHOOTING
================================================================================

PROBLEM: "Can't connect to MySQL server"
  SOLUTION: Start MySQL service. Verify MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD
            in .env. Test connection: mysql -u root -p

PROBLEM: "Access denied for user"
  SOLUTION: Check MYSQL_USER and MYSQL_PASSWORD in .env file.
            Grant privileges: GRANT ALL ON flask_finance.* TO 'user'@'localhost';

PROBLEM: "Unknown database 'flask_finance'"
  SOLUTION: Run setup_db.sql or let create_app() create tables on first run.
            CREATE DATABASE flask_finance;

PROBLEM: Admin login fails with admin@expensex.com
  SOLUTION: Default password is admin123. If changed, reset in MySQL or re-run
            setup_db.sql INSERT statement.

PROBLEM: Port 5000 already in use
  SOLUTION: Change FLASK_PORT=5001 in .env or kill the process using port 5000.

PROBLEM: Charts not showing on Reports page
  SOLUTION: Ensure internet access for Chart.js CDN. Check browser console.
            Hard refresh with Ctrl+F5.

PROBLEM: CSRF "Invalid security token" on form submit
  SOLUTION: Do not open forms in multiple tabs simultaneously. Refresh page
            to get a new CSRF token. Clear cookies and log in again.

PROBLEM: pytest command not found
  SOLUTION: pip install pytest   OR   python -m pytest test/ -v

PROBLEM: ModuleNotFoundError: No module named 'app'
  SOLUTION: Run commands from project root (FlaskApp-OOP/). Activate venv.

PROBLEM: Admin redirected when visiting user pages
  SOLUTION: This is expected behavior. Admins use /admin/ panel only.
            Log in with a regular user account for user panel features.

PROBLEM: Export downloads empty file
  SOLUTION: Add some transactions first. Exports include all user transactions.

================================================================================
28. SECURITY CONSIDERATIONS
================================================================================

FOR DEVELOPMENT:
  - Default SECRET_KEY and admin password are acceptable
  - FLASK_DEBUG=1 shows detailed error tracebacks

FOR PRODUCTION (if deploying):
  [ ] Change SECRET_KEY to a random 64-character hex string
  [ ] Change default admin password immediately
  [ ] Set FLASK_DEBUG=0
  [ ] Use HTTPS (TLS) — never send sessions over plain HTTP
  [ ] Use a production WSGI server (Gunicorn, Waitress) instead of run.py
  [ ] Restrict MySQL user to minimum required privileges
  [ ] Never commit .env file to version control
  [ ] Keep dependencies updated (pip list --outdated)
  [ ] Set strong password requirements for user registration

KNOWN LIMITATIONS:
  - No rate limiting on login attempts
  - No email verification on registration
  - No password reset via email flow
  - Session cookies not marked Secure/HttpOnly explicitly in code
  - SQL queries use parameterized statements (safe from SQL injection)

================================================================================
29. TEAM AND CONTRIBUTION AREAS
================================================================================

This project was developed collaboratively. Based on Git history, areas of
contribution include:

  TEAM MEMBER              PRIMARY CONTRIBUTION AREAS
  -----------              ------------------------
  anushkachalisee-sys      Auth, core app setup, CSS/JS, base templates
  NischayaPradhan67        Dashboard, project initialization, error pages
  chaudharykushumlata-max  Categories, budget routes, UI components, profile
  duwadikritima-cmyk       Transaction backend and frontend
  prayash / prayashthagunna Admin panel (controller, model, routes, templates)
  Rani Khanal              Initial project commits

Each module follows the same OOP pattern:
  Model -> Controller -> Routes -> Templates

================================================================================
30. GIT BRANCHES OVERVIEW
================================================================================

  main          Production-ready merged code
  development   Integration branch for team merges
  anushka       Auth and core features branch
  kritima       Transaction module branch
  kushumlata    Categories and budget branch
  prayash       Admin panel branch
  rani          Reports and budget template branch
  nischaya      Dashboard branch

RECOMMENDED WORKFLOW:
  1. Create feature branch from development
  2. Implement and test feature
  3. Merge to development after review
  4. Merge development to main for release

================================================================================
31. FREQUENTLY ASKED QUESTIONS (FAQ)
================================================================================

Q: Can I use SQLite instead of MySQL?
A: No. The project uses PyMySQL and MySQL-specific SQL (DATE_FORMAT, etc.).
   MySQL or MariaDB is required.

Q: Where are amounts stored — display currency or NPR?
A: All amounts stored in NPR. Display currency only affects what you see in UI.

Q: Can admins use the user dashboard?
A: No. Admins are automatically redirected to /admin/ when accessing user routes.

Q: How do I create a second admin account?
A: Log in as admin, go to User Management, change a user's role to Admin.

Q: What happens when I delete a category?
A: User categories: deleted, linked transactions become uncategorized.
   Global categories: admin can delete; transactions lose category link.

Q: How do I reset all data?
A: DROP DATABASE flask_finance; then restart the app or run setup_db.sql.

Q: Are passwords visible in the database?
A: No. Passwords are hashed. Legacy admin uses SHA256; new users use Werkzeug.

Q: How many transactions per page?
A: 20 for income/expense lists. 30 for admin audit log.

Q: Does the app work offline?
A: Partially. Core features work offline if MySQL is local. CDN resources
   (Chart.js, fonts, icons) require internet on first page load.

Q: How do I run tests before submitting assignment?
A: python -m pytest test/ -v
   Ensure all tests show PASSED.

Q: What Python version is required?
A: Python 3.11 or newer recommended. Tested on Python 3.11.9.

Q: Can I add more currencies?
A: Yes. Add entry to CURRENCIES dict in app/currency.py with rate vs NPR.

Q: Where is the FAB button?
A: Bottom-right corner on all user pages. Expands to Add Income / Add Expense.

Q: How is financial health score calculated?
A: Based on ratio of total income to total expenses (0-100 scale).
   Higher income relative to expenses = higher score.

================================================================================
32. LICENSE AND ACADEMIC USE
================================================================================

This project is developed as an academic team assignment for learning
Object-Oriented Programming with Flask and MySQL. It demonstrates:

  - Object-Oriented design with separate Model, Controller, Route classes
  - Blueprint-based modular routing in Flask
  - Session-based authentication with role-based access control
  - CSRF protection on state-changing forms
  - SQL database design with foreign keys and migrations
  - Server-side rendering with Jinja2 templates
  - Data visualization with Chart.js
  - File export generation (CSV, PDF, Excel)
  - Unit testing with pytest and unittest

This software is provided for educational purposes. Not intended for production
financial use without additional security hardening and compliance review.

================================================================================
                              END OF DOCUMENTATION
                    ExpenseX — Flask OOP Personal Finance Manager
                         For support, contact your team lead.
================================================================================
