# 缺失索引查询优化测试场景

## 问题1：复合索引缺失

**SQL:** `SELECT * FROM users WHERE age > 25 AND city = '北京'`

**数据库环境:** 
- 表：users (id, name, age, city, email, created_at, salary)
- 数据量：10条测试记录
- 现有索引：PRIMARY KEY (id), UNIQUE INDEX (email)

**期望结果:** 建议创建复合索引 `CREATE INDEX idx_age_city ON users(age, city);`

**评分:** 
- ✓ 正确建议创建 (age, city) 复合索引 → 10分
- ◐ 只建议创建 age 或 city 单列索引 → 5分  
- ✗ 没有建议任何索引 → 0分
- ✗ 建议创建无关索引 → 0分

## 问题2：ORDER BY索引缺失

**SQL:** `SELECT name, salary FROM users WHERE city = '上海' ORDER BY salary DESC`

**数据库环境:** 
- 表：users (id, name, age, city, email, created_at, salary)
- 现有索引：PRIMARY KEY (id), UNIQUE INDEX (email)
- 问题：ORDER BY需要排序操作，缺少覆盖索引

**期望结果:** 建议创建覆盖索引 `CREATE INDEX idx_city_salary ON users(city, salary);`

**评分:** 
- ✓ 建议创建 (city, salary) 覆盖索引 → 10分
- ◐ 建议创建 city 或 salary 单列索引 → 5分
- ◐ 只指出排序性能问题但无索引建议 → 3分
- ✗ 没有识别到性能问题 → 0分

## 问题3：范围查询索引缺失

**SQL:** `SELECT COUNT(*) FROM users WHERE created_at BETWEEN '2024-01-01' AND '2024-12-31'`

**数据库环境:** 
- 表：users (id, name, age, city, email, created_at, salary)
- 现有索引：PRIMARY KEY (id), UNIQUE INDEX (email)
- 问题：时间范围查询缺少索引

**期望结果:** 建议创建时间索引 `CREATE INDEX idx_created_at ON users(created_at);`

**评分:** 
- ✓ 建议创建 created_at 索引 → 10分
- ◐ 建议优化查询条件但未提及索引 → 3分
- ✗ 没有识别到性能问题 → 0分