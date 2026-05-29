CREATE DATABASE IF NOT EXISTS flask_finance;
USE flask_finance;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('user','admin') DEFAULT 'user',
    is_active TINYINT(1) DEFAULT 1,
    avatar VARCHAR(255) DEFAULT NULL,
    currency VARCHAR(10) DEFAULT 'NPR',
    streak INT DEFAULT 0,
    last_login DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    name VARCHAR(100) NOT NULL,
    type ENUM('income','expense') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    category_id INT,
    type ENUM('income','expense') NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    description VARCHAR(255),
    notes TEXT,
    date DATE NOT NULL,
    is_recurring TINYINT(1) DEFAULT 0,
    recurrence VARCHAR(20) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS budgets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    monthly_limit DECIMAL(12,2) DEFAULT 0,
    daily_limit DECIMAL(12,2) DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS achievements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    icon VARCHAR(50) DEFAULT 'award',
    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS goals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    target_amount DECIMAL(12,2) NOT NULL,
    current_amount DECIMAL(12,2) DEFAULT 0,
    deadline DATE,
    completed TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS activity_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    user_name VARCHAR(100),
    action VARCHAR(100) NOT NULL,
    detail VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

INSERT INTO users (name, email, password, role, currency, is_active)
SELECT 'Admin', 'admin@expensex.com',
       '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',
       'admin', 'NPR', 1
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'admin@expensex.com');

INSERT INTO categories (user_id, name, type) SELECT NULL, 'Salary', 'income' WHERE NOT EXISTS (SELECT 1 FROM categories WHERE user_id IS NULL AND name = 'Salary');
INSERT INTO categories (user_id, name, type) SELECT NULL, 'Freelance', 'income' WHERE NOT EXISTS (SELECT 1 FROM categories WHERE user_id IS NULL AND name = 'Freelance');
INSERT INTO categories (user_id, name, type) SELECT NULL, 'Food', 'expense' WHERE NOT EXISTS (SELECT 1 FROM categories WHERE user_id IS NULL AND name = 'Food');
INSERT INTO categories (user_id, name, type) SELECT NULL, 'Transport', 'expense' WHERE NOT EXISTS (SELECT 1 FROM categories WHERE user_id IS NULL AND name = 'Transport');
INSERT INTO categories (user_id, name, type) SELECT NULL, 'Rent', 'expense' WHERE NOT EXISTS (SELECT 1 FROM categories WHERE user_id IS NULL AND name = 'Rent');
INSERT INTO categories (user_id, name, type) SELECT NULL, 'Utilities', 'expense' WHERE NOT EXISTS (SELECT 1 FROM categories WHERE user_id IS NULL AND name = 'Utilities');
INSERT INTO categories (user_id, name, type) SELECT NULL, 'Shopping', 'expense' WHERE NOT EXISTS (SELECT 1 FROM categories WHERE user_id IS NULL AND name = 'Shopping');
INSERT INTO categories (user_id, name, type) SELECT NULL, 'Healthcare', 'expense' WHERE NOT EXISTS (SELECT 1 FROM categories WHERE user_id IS NULL AND name = 'Healthcare');
