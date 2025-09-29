-- 索引失效场景测试数据库Schema
CREATE DATABASE IF NOT EXISTS sql_eval_test;
USE sql_eval_test;

-- 订单表
CREATE TABLE IF NOT EXISTS orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_no VARCHAR(32) NOT NULL,
    user_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    status TINYINT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 创建索引（测试索引失效场景）
CREATE INDEX IF NOT EXISTS idx_created_at ON orders(created_at);
CREATE INDEX IF NOT EXISTS idx_amount ON orders(amount);
CREATE INDEX IF NOT EXISTS idx_status ON orders(status);
