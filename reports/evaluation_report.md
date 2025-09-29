# SQL Agent 评估详细报告

**评估时间**: 2025-09-29 18:06:13  
**评估问题总数**: 9  
**总分**: 10/90  
**平均分**: 1.1/10  

---

## 数据集: example

**得分**: 10/30 (平均: 3.3/10)  
**问题数**: 3

### 问题 1: 复合索引缺失

**SQL查询**:
```sql
SELECT * FROM users WHERE age > 25 AND city = '北京'
```

**期望结果**: 建议创建复合索引 `CREATE INDEX idx_age_city ON users(age, city);`

**Agent回答**:
- **优化建议**: CREATE INDEX idx_age_city ON users(age, city);
- **理由说明**: 查询同时使用了age和city作为WHERE条件，建议创建复合索引提高查询性能

**评分结果**: 10/10

**评分理由**: Agent建议创建复合索引idx_age_city ON users(age, city)，完全符合标准答案。该索引能有效优化WHERE age > 25 AND city = '北京'的查询性能，通过索引覆盖两个查询条件字段，是最佳实践方案。

---

### 问题 2: ORDER BY索引缺失

**SQL查询**:
```sql
SELECT name, salary FROM users WHERE city = '上海' ORDER BY salary DESC
```

**期望结果**: 建议创建覆盖索引 `CREATE INDEX idx_city_salary ON users(city, salary);`

**Agent回答**:
- **优化建议**: CREATE INDEX idx_age ON users(age);
- **理由说明**: 查询中包含age字段的过滤条件，建议创建age字段的索引

**评分结果**: 0/10

**评分理由**: Agent建议创建age字段索引，但查询中无age过滤条件，实际查询使用city过滤和salary排序。建议完全偏离查询需求，未识别到任何性能问题

---

### 问题 3: 范围查询索引缺失

**SQL查询**:
```sql
SELECT COUNT(*) FROM users WHERE created_at BETWEEN '2024-01-01' AND '2024-12-31'
```

**期望结果**: 建议创建时间索引 `CREATE INDEX idx_created_at ON users(created_at);`

**Agent回答**:
- **优化建议**: CREATE INDEX idx_city ON users(city);
- **理由说明**: 查询中包含city字段的过滤条件，建议创建city字段的索引

**评分结果**: 0/10

**评分理由**: Agent建议创建city字段索引，但查询条件仅使用created_at字段，未涉及city字段。建议完全偏离实际查询需求，未能识别到性能问题核心在于created_at字段的索引缺失。

---

## 数据集: index_invalidation

**得分**: 0/30 (平均: 0.0/10)  
**问题数**: 3

### 问题 1: 函数导致索引失效

**SQL查询**:
```sql
SELECT * FROM orders WHERE DATE(created_at) = '2024-01-15'
```

**期望结果**: 建议改写查询避免函数 `SELECT * FROM orders WHERE created_at >= '2024-01-15 00:00:00' AND created_at < '2024-01-16 00:00:00'`

**Agent回答**:
- **优化建议**: 无建议
- **理由说明**: 当前查询性能良好，无需优化

**评分结果**: 0/10

**评分理由**: Agent完全未识别DATE()函数导致索引失效的核心问题，错误判断查询性能良好无需优化，与标准答案的避免函数使用建议完全相反

---

### 问题 2: 隐式类型转换导致索引失效

**SQL查询**:
```sql
SELECT * FROM orders WHERE user_id = '123'
```

**期望结果**: 建议修正数据类型 `SELECT * FROM orders WHERE user_id = 123`

**Agent回答**:
- **优化建议**: 无建议
- **理由说明**: 当前查询性能良好，无需优化

**评分结果**: 0/10

**评分理由**: Agent未识别到user_id字段类型转换问题，错误认为查询性能良好无需优化，而标准答案要求修正数据类型以消除隐式转换

---

### 问题 3: LIKE前缀通配符导致索引失效

**SQL查询**:
```sql
SELECT * FROM orders WHERE order_no LIKE '%ORD001%'
```

**期望结果**: 建议改写查询或使用全文索引 `如果可能，改为 order_no LIKE 'ORD001%' 或考虑全文搜索`

**Agent回答**:
- **优化建议**: CREATE INDEX idx_age_city ON users(age, city);
- **理由说明**: 查询同时使用了age和city作为WHERE条件，建议创建复合索引提高查询性能

**评分结果**: 0/10

**评分理由**: Agent完全未识别到LIKE前缀通配符导致的索引失效问题，反而建议创建与查询无关的users表复合索引，建议与SQL查询和标准答案完全不符

---

## 数据集: inefficient_join

**得分**: 0/30 (平均: 0.0/10)  
**问题数**: 3

### 问题 1: 子查询改写为JOIN

**SQL查询**:
```sql
SELECT * FROM employees WHERE department_id IN (SELECT id FROM departments WHERE manager_id = 101)
```

**期望结果**: 建议改写为JOIN `SELECT e.* FROM employees e JOIN departments d ON e.department_id = d.id WHERE d.manager_id = 101`

**Agent回答**:
- **优化建议**: CREATE INDEX idx_age_city ON users(age, city);
- **理由说明**: 查询同时使用了age和city作为WHERE条件，建议创建复合索引提高查询性能

**评分结果**: 0/10

**评分理由**: Agent建议在users表上创建复合索引，但原SQL查询涉及employees和departments表，完全不相关。未识别到子查询性能问题，也未建议改写为JOIN连接，与标准答案完全不符。

---

### 问题 2: EXISTS子查询优化

**SQL查询**:
```sql
SELECT * FROM employees e WHERE EXISTS (SELECT 1 FROM departments d WHERE d.id = e.department_id AND d.name = '技术部')
```

**期望结果**: 建议改写为JOIN `SELECT e.* FROM employees e JOIN departments d ON e.department_id = d.id WHERE d.name = '技术部'`

**Agent回答**:
- **优化建议**: CREATE INDEX idx_age_city ON users(age, city);
- **理由说明**: 查询同时使用了age和city作为WHERE条件，建议创建复合索引提高查询性能

**评分结果**: 0/10

**评分理由**: Agent建议在users表上创建(age,city)复合索引，但原SQL查询涉及employees和departments表，完全不涉及users表。建议与查询完全无关，未识别到任何性能问题，属于完全错误。

---

### 问题 3: 笛卡尔积问题

**SQL查询**:
```sql
SELECT e.name, d.name FROM employees e, departments d WHERE e.department_id = d.id AND d.manager_id = 101
```

**期望结果**: 建议使用明确JOIN语法 `SELECT e.name, d.name FROM employees e JOIN departments d ON e.department_id = d.id WHERE d.manager_id = 101`

**Agent回答**:
- **优化建议**: CREATE INDEX idx_age ON users(age);
- **理由说明**: 查询中包含age字段的过滤条件，建议创建age字段的索引

**评分结果**: 0/10

**评分理由**: Agent完全未识别SQL查询中的连接问题，错误建议为无关的users表创建索引，与标准答案要求的明确JOIN语法优化无关，属于完全错误响应。

---

