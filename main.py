"""SQL Agent 评估框架 - LLM评分版本"""

import os
import json
import re
import requests
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv
import pymysql
from jinja2 import Environment, FileSystemLoader
from agents.mock_agent import mock_agent


def get_template_env():
    """获取Jinja2模板环境"""
    return Environment(loader=FileSystemLoader('prompts'))


def scan_datasets():
    """自动扫描datasets目录下的数据集"""
    datasets_dir = Path("datasets")
    datasets = []
    
    if not datasets_dir.exists():
        logging.error("datasets目录不存在")
        return datasets
    
    # 遍历datasets下的所有子目录
    for dataset in datasets_dir.iterdir():
        if dataset.is_dir():
            dataset_name = dataset.name
            schema_file = dataset / "schema.sql"
            data_file = dataset / "data.sql"
            questions_file = dataset / "questions.md"
            
            # 检查必需文件是否存在
            if questions_file.exists():
                datasets.append({
                    "name": dataset_name,
                    "schema_file": str(schema_file),
                    "data_file": str(data_file),
                    "questions_file": str(questions_file)
                })
                logging.info(f"发现数据集: {dataset_name}")
            else:
                logging.warning(f"数据集 {dataset_name} 缺少 questions.md 文件")
    
    return datasets


def setup_database_with_connection(conn, schema_file, data_file):
    """使用已有连接设置数据库环境"""
    cursor = conn.cursor()
    
    # 执行schema
    with open(schema_file, 'r') as f:
        schema_sql = f.read()
        statements = schema_sql.split(';')
        for stmt in statements:
            stmt = stmt.strip()
            if stmt:
                try:
                    cursor.execute(stmt)
                    logging.debug(f"执行SQL: {stmt[:50]}...")
                except Exception as e:
                    if "already exists" in str(e) or "Table" in str(e):
                        logging.debug(f"表已存在，跳过: {stmt[:50]}...")
                    else:
                        logging.error(f"SQL执行失败: {e}")
    
    # 执行data
    with open(data_file, 'r') as f:
        data_sql = f.read()
        statements = data_sql.split(';')
        for stmt in statements:
            stmt = stmt.strip()
            if stmt.upper().startswith('INSERT'):
                try:
                    cursor.execute(stmt)
                    logging.debug(f"插入数据: {stmt[:30]}...")
                except Exception as e:
                    if "Duplicate entry" in str(e):
                        logging.debug("数据已存在，跳过")
                    else:
                        logging.error(f"插入数据失败: {e}")
    
    conn.commit()
    cursor.close()
    logging.debug("数据库环境准备完成")

def setup_database(schema_file, data_file):
    """连接数据库并构建环境"""
    logging.info("连接数据库...")
    
    config = {
        'host': os.getenv('DATABASE_HOST', 'localhost'),
        'port': int(os.getenv('DATABASE_PORT', 3306)),
        'user': os.getenv('DATABASE_USER', 'root'),
        'password': os.getenv('DATABASE_PASSWORD', ''),
        'database': os.getenv('DATABASE_NAME', 'sql_eval_test')
    }
    
    conn = pymysql.connect(**config)
    logging.info(f"数据库连接成功: {config['host']}:{config['port']}")
    
    # 创建表和数据
    cursor = conn.cursor()
    
    # 创建表（支持重复执行）
    with open(schema_file, 'r') as f:
        schema_sql = f.read()
        # 逐条执行SQL，忽略已存在的错误
        statements = schema_sql.split(';')
        for stmt in statements:
            stmt = stmt.strip()
            if stmt:
                try:
                    cursor.execute(stmt)
                    logging.debug(f"执行SQL: {stmt[:50]}...")
                except Exception as e:
                    if "already exists" in str(e) or "Table" in str(e):
                        logging.debug(f"表已存在，跳过: {stmt[:50]}...")
                    else:
                        logging.error(f"SQL执行失败: {e}")
    
    # 插入数据
    with open(data_file, 'r') as f:
        data_sql = f.read()
        statements = data_sql.split(';')
        for stmt in statements:
            stmt = stmt.strip()
            if stmt.upper().startswith('INSERT'):
                try:
                    cursor.execute(stmt)
                    logging.debug(f"插入数据: {stmt[:30]}...")
                except Exception as e:
                    if "Duplicate entry" in str(e):
                        logging.debug("数据已存在，跳过")
                    else:
                        logging.error(f"插入数据失败: {e}")
    
    conn.commit()
    cursor.close()
    
    logging.info("数据库环境准备完成")
    return conn


def parse_questions(md_file):
    """解析 questions.md 文件"""
    logging.info(f"解析问题文件: {md_file}")
    
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    sections = content.split('## 问题')[1:]
    questions = []
    
    for section in sections:
        # 提取标题
        title_match = re.search(r'(\d+)[：:]\s*([^\n]+)', section)
        title = title_match.group(2) if title_match else "未命名问题"
        
        # 提取SQL
        sql_match = re.search(r'\*\*SQL:\*\*\s*`([^`]+)`', section)
        sql = sql_match.group(1) if sql_match else ""
        
        # 提取期望结果
        result_match = re.search(r'\*\*期望结果:\*\*\s*([^\n]+)', section)
        expected = result_match.group(1) if result_match else ""
        
        # 提取评分规则
        scoring_match = re.search(r'\*\*评分:\*\*.*?(.*?)(?=---|$)', section, re.DOTALL)
        scoring_rules = scoring_match.group(1).strip() if scoring_match else ""
        
        if sql:
            questions.append({
                'title': title,
                'sql': sql.strip(),
                'expected': expected,
                'scoring_rules': scoring_rules
            })
    
    logging.info(f"解析到 {len(questions)} 个问题")
    return questions


# Agent相关代码已抽取到 agents/ 目录


async def evaluate_with_llm(agent_response, expected_result, scoring_rules, sql_query):
    """使用LLM评分"""
    if not agent_response:
        return {"score": 0, "explanation": "Agent没有给出回答"}
    
    agent_optimization = agent_response.get('optimization', '')
    agent_reasoning = agent_response.get('reasoning', '')
    
    # 使用Jinja2渲染模板
    env = get_template_env()
    template = env.get_template('evaluation.tpl')
    
    prompt = template.render(
        sql_query=sql_query,
        db_context='用户表(users)包含age、city等字段',
        expected_result=expected_result,
        agent_optimization=agent_optimization,
        agent_reasoning=agent_reasoning,
        scoring_rules=scoring_rules
    )
    
    try:
        headers = {
            'Authorization': f'Bearer {os.getenv("EVAL_LLM_API_KEY")}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': os.getenv('EVAL_LLM_MODEL', 'gpt-4'),
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': 300,
            'temperature': 0.1
        }
        
        response = requests.post(
            f"{os.getenv('EVAL_LLM_BASE_URL', 'https://api.openai.com/v1')}/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        response.raise_for_status()
        result = response.json()
        llm_response = result['choices'][0]['message']['content']
        
        # 解析JSON响应
        eval_outcome = json.loads(llm_response)
        return eval_outcome
        
    except Exception as e:
        logging.error(f"LLM评分失败: {e}")
        return {"score": 0, "explanation": f"评分失败: {str(e)}"}


def load_scenario_weights():
    """从meta文件读取场景权重"""
    weights = {}
    try:
        with open('datasets/meta.txt', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    name, score = line.split('=')
                    weights[name.strip()] = int(score.strip())
    except FileNotFoundError:
        logging.warning("未找到 datasets/meta.txt 文件，使用默认权重")
        weights = {'example': 40, 'index_invalidation': 30, 'inefficient_join': 30}
    return weights

def calculate_final_scores(results):
    """计算最终得分"""
    scenario_weights = load_scenario_weights()
    
    # 按场景分组统计
    scenario_stats = {}
    for result in results:
        dataset = result['dataset']
        if dataset not in scenario_stats:
            scenario_stats[dataset] = {'scores': [], 'questions': []}
        scenario_stats[dataset]['scores'].append(result['score'])
        scenario_stats[dataset]['questions'].append(result)
    
    # 计算每个场景的得分
    final_scores = {}
    for dataset, stats in scenario_stats.items():
        weight = scenario_weights.get(dataset, 0)
        avg_score = sum(stats['scores']) / len(stats['scores']) / 10  # 转换为0-1
        final_scores[dataset] = {
            'weight': weight,
            'actual_score': weight * avg_score,
            'question_count': len(stats['scores']),
            'avg_per_question': weight / len(stats['scores'])
        }
    
    return final_scores, sum(s['actual_score'] for s in final_scores.values())

def generate_summary_table(results):
    """生成汇总表格"""
    from datetime import datetime
    
    scenario_weights = load_scenario_weights()
    final_scores, total_final_score = calculate_final_scores(results)
    
    print(f"\n📊 SQL Agent 评估汇总表格")
    print(f"评估时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 90)
    
    # 表头
    print(f"{'评测集':<18} {'评测案例':<25} {'问题分数':<12} {'场景得分':<15}")
    print("-" * 90)
    
    # 按数据集分组显示
    for dataset in scenario_weights.keys():
        dataset_results = [r for r in results if r['dataset'] == dataset]
        if not dataset_results:
            continue
            
        final_info = final_scores[dataset]
        per_question_weight = final_info['avg_per_question']
        
        # 显示第一行（包含数据集名称和场景得分）
        first_result = dataset_results[0]
        first_title = first_result['title'][:22] + "..." if len(first_result['title']) > 25 else first_result['title']
        first_score = f"{first_result['score']}/10"
        first_weighted = f"({per_question_weight:.1f}分)"
        scenario_score = f"{final_info['actual_score']:.1f}/{final_info['weight']}"
        
        print(f"{dataset:<18} {first_title:<25} {first_score:<8}{first_weighted:<4} {scenario_score}")
        
        # 显示其他问题
        for result in dataset_results[1:]:
            title_short = result['title'][:22] + "..." if len(result['title']) > 25 else result['title']
            score_display = f"{result['score']}/10"
            weighted_display = f"({per_question_weight:.1f}分)"
            print(f"{'':<18} {title_short:<25} {score_display:<8}{weighted_display:<4} {''}")
        
        print("-" * 90)
    
    # 总计行
    print(f"{'总计':<18} {f'{len(results)}个问题':<25} {'':<12} {total_final_score:.1f}/100")
    print("=" * 90)

def generate_detailed_report(results):
    """生成详细报告到markdown文件"""
    from datetime import datetime
    import os
    
    # 确保reports目录存在
    os.makedirs('reports', exist_ok=True)
    
    report_content = f"""# SQL Agent 评估详细报告

**评估时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**评估问题总数**: {len(results)}  
**总分**: {sum(r['score'] for r in results)}/{len(results) * 10}  
**平均分**: {sum(r['score'] for r in results) / len(results):.1f}/10  

---

"""
    
    # 按数据集分组
    datasets = {}
    for result in results:
        dataset = result['dataset']
        if dataset not in datasets:
            datasets[dataset] = []
        datasets[dataset].append(result)
    
    for dataset_name, dataset_results in datasets.items():
        dataset_score = sum(r['score'] for r in dataset_results)
        dataset_avg = dataset_score / len(dataset_results)
        
        report_content += f"""## 数据集: {dataset_name}

**得分**: {dataset_score}/{len(dataset_results) * 10} (平均: {dataset_avg:.1f}/10)  
**问题数**: {len(dataset_results)}

"""
        
        for i, result in enumerate(dataset_results, 1):
            report_content += f"""### 问题 {i}: {result['title']}

**SQL查询**:
```sql
{result['sql']}
```

**期望结果**: {result['expected']}

**Agent回答**:
- **优化建议**: {result['agent_optimization'] or '无建议'}
- **理由说明**: {result['agent_reasoning']}

**评分结果**: {result['score']}/10

**评分理由**: {result['explanation']}

---

"""
    
    # 写入文件
    with open('reports/evaluation_report.md', 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    logging.info("详细报告已保存到 reports/evaluation_report.md")

def setup_logging():
    """设置日志配置"""
    # 确保logs目录存在
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/eval.log'),
            logging.StreamHandler()
        ]
    )
    # 设置第三方库日志级别
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)


async def main():
    """主函数"""
    setup_logging()
    
    print("🚀 SQL Agent 评估开始")
    
    # 1. 扫描可用数据集
    load_dotenv('config/.env')
    datasets = scan_datasets()
    
    if not datasets:
        print("❌ 没有发现可用的数据集")
        return
    
    # 2. 建立数据库连接（一次性连接）
    logging.info("建立数据库连接...")
    config = {
        'host': os.getenv('DATABASE_HOST', 'localhost'),
        'port': int(os.getenv('DATABASE_PORT', 3306)),
        'user': os.getenv('DATABASE_USER', 'root'),
        'password': os.getenv('DATABASE_PASSWORD', ''),
        'database': os.getenv('DATABASE_NAME', 'sql_eval_test')
    }
    conn = pymysql.connect(**config)
    logging.info(f"数据库连接成功: {config['host']}:{config['port']}")
    
    # 3. 遍历所有数据集进行评估
    results = []
    all_total_score = 0
    all_question_count = 0
    
    for dataset in datasets:
        logging.info(f"开始评估数据集: {dataset['name']}")
        
        # 构建数据库环境（复用连接）
        setup_database_with_connection(conn, dataset['schema_file'], dataset['data_file'])
        
        # 解析问题
        questions = parse_questions(Path(dataset['questions_file']))
        
        # 运行评估
        dataset_total_score = 0
        
        for i, q in enumerate(questions, 1):
            # Agent处理
            agent_result = mock_agent(q['sql'])
            
            # LLM评分
            eval_result = await evaluate_with_llm(agent_result, q['expected'], q['scoring_rules'], q['sql'])
            score = eval_result['score']
            
            # 收集结果
            results.append({
                'dataset': dataset['name'],
                'question_id': i,
                'title': q['title'],
                'sql': q['sql'],
                'expected': q['expected'],
                'agent_optimization': agent_result['optimization'],
                'agent_reasoning': agent_result['reasoning'],
                'score': score,
                'explanation': eval_result['explanation'].strip()
            })
            
            dataset_total_score += score
        
        all_total_score += dataset_total_score
        all_question_count += len(questions)
        
        logging.info(f"数据集 {dataset['name']} 评估完成，得分: {dataset_total_score}/{len(questions) * 10}")
    
    conn.close()
    
    # 4. 生成汇总表格和详细报告
    generate_summary_table(results)
    generate_detailed_report(results)
    
    print(f"\n🏆 总体评估完成!")
    print(f"总分: {all_total_score}/{all_question_count * 10}")
    print(f"总平均分: {all_total_score / all_question_count:.1f}/10")
    print(f"📊 汇总表格已显示在控制台")
    print(f"📝 详细报告已保存到 reports/evaluation_report.md")


if __name__ == "__main__":
    asyncio.run(main())