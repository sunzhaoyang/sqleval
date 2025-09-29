"""简单的Mock Agent - 随机返回几个预设答案中的一个."""

import random


def mock_agent(sql_query):
    """Mock Agent - 随机返回优化建议"""
    import logging
    
    logging.debug(f"Agent处理查询: {sql_query[:50]}...")
    
    responses = [
        {
            'optimization': 'CREATE INDEX idx_age_city ON users(age, city);',
            'reasoning': '查询同时使用了age和city作为WHERE条件，建议创建复合索引提高查询性能'
        },
        {
            'optimization': 'CREATE INDEX idx_age ON users(age);',
            'reasoning': '查询中包含age字段的过滤条件，建议创建age字段的索引'
        },
        {
            'optimization': 'CREATE INDEX idx_city ON users(city);',
            'reasoning': '查询中包含city字段的过滤条件，建议创建city字段的索引'
        },
        {
            'optimization': 'CREATE INDEX idx_id ON users(id);',
            'reasoning': '建议在id字段上创建索引以优化查询'
        },
        {
            'optimization': '',
            'reasoning': '当前查询性能良好，无需优化'
        }
    ]
    
    selected = random.choice(responses)
    logging.debug(f"Agent选择回答: {selected['reasoning']}")
    return selected
