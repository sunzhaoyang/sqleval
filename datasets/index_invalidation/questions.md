# 索引失效场景测试

## 问题1：函数导致索引失效

**SQL:** `SELECT * FROM orders WHERE DATE(created_at) = '2024-01-15'`

**数据库环境:** 
- 表：orders (id, order_no, user_id, amount, status, created_at, updated_at)
- 现有索引：idx_created_at ON orders(created_at)
- 问题：DATE()函数导致索引失效

**期望结果:** 建议改写查询避免函数 `SELECT * FROM orders WHERE created_at >= '2024-01-15 00:00:00' AND created_at < '2024-01-16 00:00:00'`

**评分:** 
- ✓ 建议改写查询避免函数使用 → 10分
- ◐ 建议创建函数索引或表达式索引 → 7分  
- ◐ 只指出索引失效问题但无解决方案 → 3分
- ✗ 没有识别到索引失效问题 → 0分

## 问题2：隐式类型转换导致索引失效

**SQL:** `SELECT * FROM orders WHERE user_id = '123'`

**数据库环境:** 
- 表：orders (id, order_no, user_id INT, amount, status, created_at, updated_at)
- 现有索引：idx_user_id ON orders(user_id)
- 问题：user_id是INT类型，但查询使用字符串'123'导致类型转换

**期望结果:** 建议修正数据类型 `SELECT * FROM orders WHERE user_id = 123`

**评分:** 
- ✓ 建议修正为正确的数据类型 → 10分
- ◐ 指出类型转换问题但无具体解决方案 → 5分
- ✗ 没有识别到类型转换问题 → 0分

## 问题3：LIKE前缀通配符导致索引失效

**SQL:** `SELECT * FROM orders WHERE order_no LIKE '%ORD001%'`

**数据库环境:** 
- 表：orders (id, order_no, user_id, amount, status, created_at, updated_at)
- 现有索引：idx_order_no ON orders(order_no)
- 问题：LIKE使用前缀通配符%导致索引无法使用

**期望结果:** 建议改写查询或使用全文索引 `如果可能，改为 order_no LIKE 'ORD001%' 或考虑全文搜索`

**评分:** 
- ✓ 建议去掉前缀通配符或使用全文索引 → 10分
- ◐ 指出LIKE通配符问题但无解决方案 → 5分
- ✗ 没有识别到索引失效问题 → 0分
