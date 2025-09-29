-- 低效连接场景测试数据库Schema
CREATE DATABASE IF NOT EXISTS sql_eval_test;
USE sql_eval_test;

-- 员工表
CREATE TABLE IF NOT EXISTS employees (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    department_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 部门表
CREATE TABLE IF NOT EXISTS departments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    manager_id INT
);

-- 现有索引
CREATE INDEX IF NOT EXISTS idx_employees_dept ON employees(department_id);
CREATE INDEX IF NOT EXISTS idx_dept_manager ON departments(manager_id);
