import hashlib

import pymysql
import pymysql.cursors

import config


class Database:
    def __init__(self):
        self.conn = pymysql.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=config.MYSQL_DATABASE,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )
        self.cursor = self.conn.cursor()

    def execute(self, query, params=None):
        self.cursor.execute(query, params or ())
        return self.cursor.lastrowid

    def fetch_one(self, query, params=None):
        self.cursor.execute(query, params or ())
        return self.cursor.fetchone()

    def fetch_all(self, query, params=None):
        self.cursor.execute(query, params or ())
        return self.cursor.fetchall()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def _column_exists(self, table, column):
        row = self.fetch_one(
            """
            SELECT COUNT(*) AS cnt FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s
            """,
            (config.MYSQL_DATABASE, table, column),
        )
        return row and row["cnt"] > 0

    def _add_column_if_missing(self, table, column, definition):
        if not self._column_exists(table, column):
            self.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    def migrate_schema(self):
        self._add_column_if_missing("users", "currency", "VARCHAR(10) DEFAULT 'NPR'")
        self._add_column_if_missing("users", "is_active", "TINYINT(1) DEFAULT 1")
        self._add_column_if_missing("users", "avatar", "VARCHAR(255) DEFAULT NULL")
        self._add_column_if_missing(
            "transactions", "is_recurring", "TINYINT(1) DEFAULT 0"
        )
        self._add_column_if_missing(
            "transactions", "recurrence", "VARCHAR(20) DEFAULT NULL"
        )
        self._add_column_if_missing("transactions", "notes", "TEXT DEFAULT NULL")
        if self._column_exists("categories", "user_id"):
            col = self.fetch_one(
                """
                SELECT IS_NULLABLE FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'categories'
                AND COLUMN_NAME = 'user_id'
                """,
                (config.MYSQL_DATABASE,),
            )
            if col and col.get("IS_NULLABLE") == "NO":
                self.execute("ALTER TABLE categories MODIFY user_id INT NULL")

    def create_tables(self):
        tables = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(150) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role ENUM('user', 'admin') DEFAULT 'user',
                is_active TINYINT(1) DEFAULT 1,
                avatar VARCHAR(255) DEFAULT NULL,
                currency VARCHAR(10) DEFAULT 'NPR',
                streak INT DEFAULT 0,
                last_login DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NULL,
                name VARCHAR(100) NOT NULL,
                type ENUM('income', 'expense') NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                category_id INT,
                type ENUM('income', 'expense') NOT NULL,
                amount DECIMAL(12, 2) NOT NULL,
                description VARCHAR(255),
                notes TEXT,
                date DATE NOT NULL,
                is_recurring TINYINT(1) DEFAULT 0,
                recurrence VARCHAR(20) DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS budgets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL UNIQUE,
                monthly_limit DECIMAL(12, 2) DEFAULT 0,
                daily_limit DECIMAL(12, 2) DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS achievements (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                title VARCHAR(100) NOT NULL,
                description VARCHAR(255),
                icon VARCHAR(50) DEFAULT 'award',
                unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS goals (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                title VARCHAR(100) NOT NULL,
                target_amount DECIMAL(12, 2) NOT NULL,
                current_amount DECIMAL(12, 2) DEFAULT 0,
                deadline DATE,
                completed TINYINT(1) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS activity_log (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                user_name VARCHAR(100),
                action VARCHAR(100) NOT NULL,
                detail VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            )
            """,
        ]
        for table_sql in tables:
            self.execute(table_sql)

        self.migrate_schema()

        admin = self.fetch_one(
            "SELECT id FROM users WHERE email = %s",
            ("admin@expensex.com",),
        )
        if not admin:
            hashed = hashlib.sha256("admin123".encode()).hexdigest()
            self.execute(
                """
                INSERT INTO users (name, email, password, role, streak, currency, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, 1)
                """,
                ("Admin", "admin@expensex.com", hashed, "admin", 0, "NPR"),
            )

        self._seed_global_categories()

    def _seed_global_categories(self):
        defaults = [
            ("Salary", "income"),
            ("Freelance", "income"),
            ("Food", "expense"),
            ("Transport", "expense"),
            ("Rent", "expense"),
            ("Utilities", "expense"),
            ("Shopping", "expense"),
            ("Healthcare", "expense"),
        ]
        for name, cat_type in defaults:
            exists = self.fetch_one(
                """
                SELECT id FROM categories
                WHERE user_id IS NULL AND name = %s AND type = %s
                """,
                (name, cat_type),
            )
            if not exists:
                self.execute(
                    "INSERT INTO categories (user_id, name, type) VALUES (NULL, %s, %s)",
                    (name, cat_type),
                )


def log_activity(user_id, user_name, action, detail=""):
    db = Database()
    try:
        db.execute(
            """
            INSERT INTO activity_log (user_id, user_name, action, detail)
            VALUES (%s, %s, %s, %s)
            """,
            (user_id, user_name, action, detail),
        )
    finally:
        db.close()
#working