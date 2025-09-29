-- 低效连接场景测试数据
INSERT IGNORE INTO departments (id, name, manager_id) VALUES
(1, '技术部', 101),
(2, '产品部', 102),
(3, '运营部', 103),
(4, '市场部', 104);

INSERT IGNORE INTO employees (id, name, email, department_id) VALUES
(1, '张三', 'zhangsan@company.com', 1),
(2, '李四', 'lisi@company.com', 1),
(3, '王五', 'wangwu@company.com', 2),
(4, '赵六', 'zhaoliu@company.com', 2),
(5, '钱七', 'qianqi@company.com', 3),
(6, '孙八', 'sunba@company.com', 3),
(7, '周九', 'zhoujiu@company.com', 4),
(8, '吴十', 'wushi@company.com', 1);
