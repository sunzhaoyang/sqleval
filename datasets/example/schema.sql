-- 简化的测试数据库Schema - 只保留用户表
CREATE DATABASE IF NOT EXISTS sql_eval_test;
USE sql_eval_test;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    city VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    salary DECIMAL(10,2)
);

-- 现有索引只有：PRIMARY KEY (id), UNIQUE INDEX (email)