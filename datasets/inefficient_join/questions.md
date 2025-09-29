# 低效连接场景测试

## 问题1：子查询改写为JOIN

**SQL:** `SELECT * FROM employees WHERE department_id IN (SELECT id FROM departments WHERE manager_id = 101)`

**数据库环境:** 
- 表：employees, departments
- 现有索引：idx_employees_dept ON employees(department_id), idx_dept_manager ON departments(manager_id)
- 问题：使用IN子查询效率低于JOIN

**期望结果:** 建议改写为JOIN `SELECT e.* FROM employees e JOIN departments d ON e.department_id = d.id WHERE d.manager_id = 101`

**评分:** 
- ✓ 建议改写为JOIN连接 → 10分
- ◐ 建议优化子查询但未提及JOIN → 5分
- ◐ 建议创建索引但未改写查询 → 3分
- ✗ 没有识别到性能问题 → 0分

## 问题2：EXISTS子查询优化

**SQL:** `SELECT * FROM employees e WHERE EXISTS (SELECT 1 FROM departments d WHERE d.id = e.department_id AND d.name = '技术部')`

**数据库环境:** 
- 表：employees, departments
- 现有索引：idx_employees_dept ON employees(department_id), idx_dept_manager ON departments(manager_id)
- 问题：EXISTS子查询可以改写为更高效的JOIN

**期望结果:** 建议改写为JOIN `SELECT e.* FROM employees e JOIN departments d ON e.department_id = d.id WHERE d.name = '技术部'`

**评分:** 
- ✓ 建议改写为JOIN连接 → 10分
- ◐ 建议优化EXISTS但未提及JOIN → 5分
- ◐ 建议创建name字段索引 → 3分
- ✗ 没有识别到性能问题 → 0分

## 问题3：笛卡尔积问题

**SQL:** `SELECT e.name, d.name FROM employees e, departments d WHERE e.department_id = d.id AND d.manager_id = 101`

**数据库环境:** 
- 表：employees, departments
- 现有索引：idx_employees_dept ON employees(department_id), idx_dept_manager ON departments(manager_id)
- 问题：使用逗号连接容易产生笛卡尔积，应使用明确的JOIN语法

**期望结果:** 建议使用明确JOIN语法 `SELECT e.name, d.name FROM employees e JOIN departments d ON e.department_id = d.id WHERE d.manager_id = 101`

**评分:** 
- ✓ 建议改写为明确的JOIN语法 → 10分
- ◐ 指出笛卡尔积风险但无具体建议 → 5分
- ✗ 没有识别到连接问题 → 0分
