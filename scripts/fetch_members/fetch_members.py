#!/usr/bin/env python3
"""
数据拉取脚本 (Python 版本)
从 GitHub API 获取组织成员信息并转换为 CSV 格式
"""

import os
import sys
import csv
import json
import time
from datetime import datetime, timedelta
from collections import defaultdict
try:
    import requests
except ImportError:
    requests = None
from pathlib import Path

# 添加父目录到路径，以便导入共享模块
sys.path.insert(0, str(Path(__file__).parent.parent))
from bot_filter import is_bot_account

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv 不是必需的，如果没有安装就忽略
    pass

# 配置
CONFIG = {
    'ORG_NAME': os.getenv('GITHUB_ORG', 'datawhalechina'),
    'GITHUB_TOKEN': os.getenv('GITHUB_TOKEN'),
    'OUTPUT_FILE': Path(__file__).parent.parent.parent / 'docs' / 'public' / 'data' / 'members.csv',
    'OUTPUT_JSON_FILE': Path(__file__).parent.parent.parent / 'docs' / 'public' / 'data' / 'members.json',
    # 周commit数据文件
    'COMMITS_FILE': Path(__file__).parent.parent.parent / 'docs' / 'public' / 'data' / 'commits_weekly.json',
    # 头像缓存目录
    'AVATARS_DIR': Path(__file__).parent.parent.parent / 'docs' / 'public' / 'avatars',
    'API_BASE': 'https://api.github.com',
    # 最小贡献行数阈值（降低以包含更多贡献者）
    # 修改为 0，确保所有贡献者都被采集，包括只有少量代码变更的新贡献者
    # 注意：GitHub API 的 contributions 字段表示代码行数变更，不是 commit 数量
    'MIN_CONTRIBUTIONS': int(os.getenv('MIN_CONTRIBUTIONS', '0')),
    'MAX_REPOS_PER_PAGE': 100,  # 每页最大仓库数
    'MAX_CONTRIBUTORS_PER_REPO': 100,  # 每个仓库最大贡献者数
    'MAX_USER_REPOS': 100,  # 获取用户仓库的最大数量
    'COMMIT_DAYS_RANGE': 7,  # 获取最近N天的commit数据
    'MAX_COMMITS_PER_REPO': 200,  # 每个仓库最大commit数
    # topic/关键词 → 领域映射（用于 bio、topics、仓库名匹配）
    'DEFAULT_DOMAINS': {
        'machine-learning': '机器学习',
        'deep-learning': '深度学习',
        'natural-language-processing': 'NLP',
        'computer-vision': '计算机视觉',
        'data-mining': '数据挖掘',
        'recommendation-system': '推荐系统',
        'reinforcement-learning': '强化学习',
        'artificial-intelligence': '人工智能',
        'llm': 'LLM',
        'data-science': '数据科学',
        'frontend': '前端开发',
        'backend': '后端开发',
        'fullstack': '全栈开发',
        'bigdata': '大数据',
        'embodied-ai': '具身智能',
        'robotics': '具身智能',
        'medical-imaging': '医学影像',
        'agent': 'AI Agent',
        'multi-agent': 'AI Agent',
        'multimodal': '多模态',
        'rag': 'RAG',
        'data-analysis': '数据分析',
        'graph-neural-network': '图神经网络',
    },
    # 仓库名 → 领域 直接映射（优先级最高，解决歧义）
    'REPO_DOMAIN_MAP': {
        # 面试求职（不是 CV）
        'daily-interview': '面试求职',
        'get-job': '面试求职',
        'huawei-od-python': '面试求职',
        # 具身智能 / 机器人
        'easy-robot': '具身智能',
        'easy-ros2arm': '具身智能',
        'every-embodied': '具身智能',
        'ai-hardware-robotics': '具身智能',
        'white-cloud-robotics': '具身智能',
        # 医学影像
        'med-imaging-primer': '医学影像',
        # AI Agent
        'agent-tutorial': 'AI Agent',
        'agentic-ai': 'AI Agent',
        'hello-agents': 'AI Agent',
        'wow-agent': 'AI Agent',
        'handy-multi-agent': 'AI Agent',
        'hugging-multi-agent': 'AI Agent',
        'easy-langent': 'AI Agent',
        # AI 工具教程
        'handy-ollama': 'AI工具',
        'handy-n8n': 'AI工具',
        'self-dify': 'AI工具',
        'coze-ai-assistant': 'AI工具',
        'self-llm': 'AI工具',
        'unlock-hf': 'AI工具',
        'unlock-deepseek': 'AI工具',
        'smart-prompt': 'AI工具',
        'easy-vibe': 'AI工具',
        'vibe-vibe': 'AI工具',
        # 框架教程
        'thorough-pytorch': '框架教程',
        'openmmlab-tutorial': '框架教程',
        'd2l-ai-solutions-manual': '框架教程',
        'fantastic-matplotlib': '框架教程',
        'joyful-pandas': '框架教程',
        'powerful-numpy': '框架教程',
        'wow-plotly': '框架教程',
        # RAG
        'all-in-rag': 'RAG',
        'wow-rag': 'RAG',
        'easy-vectordb': 'RAG',
        'easy-vecdb': 'RAG',
        # LLM
        'llm-cookbook': 'LLM',
        'llm-universe': 'LLM',
        'llm-deploy': 'LLM',
        'llm-research': 'LLM',
        'llmbook': 'LLM',
        'llms-from-scratch-cn': 'LLM',
        'so-large-lm': 'LLM',
        'happy-llm': 'LLM',
        'base-llm': 'LLM',
        'hugging-llm': 'LLM',
        'hands-on-llm': 'LLM',
        'hands-on-llama': 'LLM',
        'code-your-own-llm': 'LLM',
        'tiny-universe': 'LLM',
        'post-training-of-llms': 'LLM',
        'leegenai-tutorial': 'LLM',
        # 多模态
        'hugging-audio': '多模态',
        'sora-tutorial': '多模态',
        'hugging-vis': '多模态',
        'vced': '多模态',
        # 计算机视觉（真正的 CV 项目）
        'dive-into-cv-pytorch': '计算机视觉',
        'deep-learning-for-computer-vision': '计算机视觉',
        'magic-cv': '计算机视觉',
        'team-learning-cv': '计算机视觉',
        'yolo-master': '计算机视觉',
        'easy-dip': '计算机视觉',
        # NLP
        'easy-nlp': 'NLP',
        'base-nlp': 'NLP',
        'hands-dirty-nlp': 'NLP',
        'learn-nlp-with-transformers': 'NLP',
        'team-learning-nlp': 'NLP',
        'hand-bert': 'NLP',
        'fun-transformer': 'NLP',
        # 强化学习
        'easy-rl': '强化学习',
        'joyrl': '强化学习',
        'joyrl-book': '强化学习',
        'hugging-rl': '强化学习',
        'key-book': '强化学习',
        'fun-marl': '强化学习',
        'team-learning-rl': '强化学习',
        # 推荐系统
        'fun-rec': '推荐系统',
        'torch-rechub': '推荐系统',
        'fun-ir': '推荐系统',
        # 数据竞赛
        'competition-baseline': '数据竞赛',
        'coggle': '数据竞赛',
        # 数据分析
        'hands-on-data-analysis': '数据分析',
        'team-learning-data-mining': '数据分析',
        # 编程基础
        'learn-python-the-smart-way': '编程基础',
        'learn-python-the-smart-way-v2': '编程基础',
        'leetcode-notes': '编程基础',
        'team-learning-program': '编程基础',
        'team-learning-sql': '编程基础',
        'wonderful-sql': '编程基础',
        'cstart': '编程基础',
        'go-talent': '编程基础',
        # 全栈开发
        'wow-fullstack': '全栈开发',
        'whale-web': '前端开发',
        'sweettalk-django': '后端开发',
    }
}


def get_headers():
    """获取请求头"""
    headers = {
        'User-Agent': 'members-visualization-bot',
        'Accept': 'application/vnd.github.v3+json'
    }

    if CONFIG['GITHUB_TOKEN']:
        headers['Authorization'] = f"Bearer {CONFIG['GITHUB_TOKEN']}"

    return headers


def fetch_api(url, retries=3):
    """发送 API 请求（带重试逻辑）"""
    if not CONFIG['GITHUB_TOKEN']:
        print("⚠️  未设置 GITHUB_TOKEN，可能会遇到 API 速率限制")

    for attempt in range(retries):
        try:
            print(f"🔄 请求 {url} (尝试 {attempt + 1}/{retries})")

            response = requests.get(url, headers=get_headers(), timeout=30)

            # 检查速率限制
            remaining = response.headers.get('X-RateLimit-Remaining')
            reset_time = response.headers.get('X-RateLimit-Reset')

            if remaining:
                print(f"📊 API 剩余请求次数: {remaining}")

            if response.status_code == 403 and remaining == '0':
                if reset_time and attempt < retries - 1:
                    reset_timestamp = int(reset_time)
                    wait_time = reset_timestamp - int(time.time()) + 1
                    if wait_time > 0:
                        print(f"⏳ API 速率限制，等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                        continue
                raise requests.exceptions.HTTPError(f"API 速率限制已达上限")

            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            print(f"❌ 请求失败 (尝试 {attempt + 1}/{retries}): {url}")
            print(f"错误: {e}")

            if attempt == retries - 1:
                return None

            # 指数退避延迟
            wait_time = (2 ** attempt)
            print(f"⏳ 等待 {wait_time} 秒后重试...")
            time.sleep(wait_time)

    return None


def get_org_repos(org_name):
    """获取组织仓库列表（支持分页）"""
    print(f"正在获取组织 {org_name} 的仓库列表...")

    all_repos = []
    page = 1
    per_page = CONFIG['MAX_REPOS_PER_PAGE']

    while True:
        url = f"{CONFIG['API_BASE']}/orgs/{org_name}/repos?per_page={per_page}&page={page}&type=public&sort=updated"
        repos = fetch_api(url)

        if not repos or len(repos) == 0:
            break

        # 过滤掉 fork 的仓库，只保留原创仓库
        original_repos = [
            repo for repo in repos if not repo.get('fork', False)]
        all_repos.extend(original_repos)

        print(f"获取第 {page} 页：{len(repos)} 个仓库（{len(original_repos)} 个原创）")

        # 测试模式：限制总仓库数
        if CONFIG.get('TEST_MODE', False) and len(all_repos) >= CONFIG.get('TEST_MAX_REPOS', 5):
            print(
                f"🧪 测试模式：已达到仓库数限制 ({CONFIG.get('TEST_MAX_REPOS', 5)} 个)，停止获取")
            all_repos = all_repos[:CONFIG.get('TEST_MAX_REPOS', 5)]  # 确保不超过限制
            break

        # 如果返回的仓库数少于每页限制，说明已经是最后一页
        if len(repos) < per_page:
            break

        page += 1

        # 安全限制：最多获取20页（2000个仓库）
        if page > 20:
            print("⚠️ 达到页数限制，停止获取")
            break

    print(f"总共找到 {len(all_repos)} 个原创仓库")
    return all_repos


def get_repo_contributors(org_name, repo_name):
    """获取仓库贡献者（过滤机器人账户）"""
    all_contributors = []
    page = 1
    per_page = 100

    while True:
        url = f"{CONFIG['API_BASE']}/repos/{org_name}/{repo_name}/contributors?per_page={per_page}&page={page}"
        contributors = fetch_api(url)

        if not contributors or len(contributors) == 0:
            break

        all_contributors.extend(contributors)

        # 如果返回的贡献者数少于每页限制，说明已经是最后一页
        if len(contributors) < per_page:
            break

        page += 1

        # 安全限制：最多获取10页（1000个贡献者）
        if page > 10:
            print(f"    ⚠️ 仓库 {repo_name} 贡献者过多，已达页数限制")
            break

    # 过滤掉贡献数低于阈值的贡献者和机器人账户
    qualified_contributors = []
    for contributor in all_contributors:
        username = contributor['login']
        contributions = contributor.get('contributions', 0)

        # 检查是否为机器人账户
        if is_bot_account(username):
            print(f"    🤖 跳过机器人账户: {username}")
            continue

        if contributions >= CONFIG['MIN_CONTRIBUTIONS']:
            qualified_contributors.append({
                'login': contributor['login'],
                'contributions': contributions,
                'html_url': contributor['html_url'],
                'avatar_url': contributor['avatar_url']
            })

    print(
        f"    📊 总贡献者: {len(all_contributors)}, 符合条件(≥{CONFIG['MIN_CONTRIBUTIONS']}行): {len(qualified_contributors)}")
    return qualified_contributors


def collect_contributors_from_repos(org_name):
    """从组织仓库中收集贡献者数据"""
    print(f"🚀 开始从 {org_name} 组织仓库收集贡献者数据...")

    # 获取组织所有仓库
    repos = get_org_repos(org_name)
    if not repos:
        print("❌ 未找到任何仓库")
        return {}

    # {username: {repos: [repo_names], total_contributions: int, user_info: dict}}
    contributors_data = {}

    for i, repo in enumerate(repos):
        repo_name = repo['name']
        print(f"\n📁 处理仓库 {i + 1}/{len(repos)}: {repo_name}")

        try:
            # 获取仓库贡献者
            contributors = get_repo_contributors(org_name, repo_name)
            print(
                f"  ✓ 找到 {len(contributors)} 个符合条件的贡献者（≥{CONFIG['MIN_CONTRIBUTIONS']}行）")

            for contributor in contributors:
                username = contributor['login']
                contributions = contributor['contributions']

                if username not in contributors_data:
                    contributors_data[username] = {
                        'repos': [],
                        'total_contributions': 0,
                        'user_info': {
                            'html_url': contributor['html_url'],
                            'avatar_url': contributor['avatar_url']
                        }
                    }

                contributors_data[username]['repos'].append(repo_name)
                contributors_data[username]['total_contributions'] += contributions

            # API 速率限制控制
            delay = 0.1 if CONFIG['GITHUB_TOKEN'] else 0.5
            time.sleep(delay)

        except Exception as e:
            print(f"  ⚠️ 处理仓库 {repo_name} 时出错: {e}")
            continue

    print(f"\n🎉 收集完成！总共发现 {len(contributors_data)} 个贡献者")
    return contributors_data


def download_avatar(avatar_url, username):
    """下载并缓存用户头像"""
    if not avatar_url or not requests:
        return None

    # 确保头像目录存在
    CONFIG['AVATARS_DIR'].mkdir(parents=True, exist_ok=True)

    # 头像文件路径
    avatar_filename = f"{username}.jpg"
    avatar_path = CONFIG['AVATARS_DIR'] / avatar_filename

    # 如果头像已存在，直接返回相对路径
    if avatar_path.exists():
        return f"avatars/{avatar_filename}"

    try:
        print(f"  📸 下载头像: {username}")
        response = requests.get(avatar_url, timeout=30)
        response.raise_for_status()

        with open(avatar_path, 'wb') as f:
            f.write(response.content)

        return f"avatars/{avatar_filename}"
    except Exception as e:
        print(f"  ⚠️ 头像下载失败 {username}: {e}")
        return None


def ensure_avatar_exists(username, avatar_url):
    """确保指定用户的头像文件存在，如果不存在则下载"""
    if not username or not avatar_url:
        return False

    # 确保头像目录存在
    CONFIG['AVATARS_DIR'].mkdir(parents=True, exist_ok=True)

    # 头像文件路径
    avatar_filename = f"{username}.jpg"
    avatar_path = CONFIG['AVATARS_DIR'] / avatar_filename

    # 如果头像已存在，无需下载
    if avatar_path.exists():
        return True

    try:
        # 静默下载头像，避免过多输出
        response = requests.get(avatar_url, timeout=10)
        response.raise_for_status()

        with open(avatar_path, 'wb') as f:
            f.write(response.content)

        print(f"      📸 新增头像: {username}")
        return True

    except Exception as e:
        # 静默处理错误，避免中断数据收集流程
        return False


def get_user_details(username):
    """获取用户详细信息"""
    url = f"{CONFIG['API_BASE']}/users/{username}"
    return fetch_api(url)


def get_user_repos(username, max_repos=None):
    """获取用户仓库信息"""
    if max_repos is None:
        max_repos = CONFIG['MAX_USER_REPOS']

    url = f"{CONFIG['API_BASE']}/users/{username}/repos?sort=updated&per_page={max_repos}"
    repos = fetch_api(url)
    return repos if repos else []


def calculate_user_stats(user_details, user_repos):
    """计算用户统计信息（个人仓库数据，用于参考）"""
    if not user_details:
        return {
            'public_repos': 0,
            'total_stars': 0,
            'followers': 0,
            'following': 0
        }

    # 从用户详情获取基本统计
    stats = {
        'public_repos': user_details.get('public_repos', 0),
        'followers': user_details.get('followers', 0),
        'following': user_details.get('following', 0),
        'total_stars': 0
    }

    # 计算总 Stars（从用户个人仓库中累加）
    if user_repos:
        stats['total_stars'] = sum(
            repo.get('stargazers_count', 0) for repo in user_repos)

    return stats


def calculate_org_contribution_stats(username, contrib_info, org_repos_cache):
    """
    计算用户在组织仓库中的贡献统计

    Args:
        username: 用户名
        contrib_info: 贡献者信息，包含参与的仓库列表和贡献数
        org_repos_cache: 组织仓库缓存，格式为 {repo_name: repo_data}

    Returns:
        dict: 组织贡献统计数据
    """
    stats = {
        'org_repos_count': 0,        # 参与的组织仓库数量
        'org_total_stars': 0,         # 参与的组织仓库总 stars
        'org_total_forks': 0,         # 参与的组织仓库总 forks
        'org_total_contributions': 0, # 在组织中的总贡献数（代码行数）
        'org_avg_stars_per_repo': 0   # 平均每个参与仓库的 stars
    }

    if not contrib_info or not contrib_info.get('repos'):
        return stats

    participated_repos = contrib_info.get('repos', [])
    stats['org_repos_count'] = len(participated_repos)
    stats['org_total_contributions'] = contrib_info.get('total_contributions', 0)

    # 累加参与的组织仓库的 stars 和 forks
    for repo_name in participated_repos:
        if repo_name in org_repos_cache:
            repo_data = org_repos_cache[repo_name]
            stats['org_total_stars'] += repo_data.get('stargazers_count', 0)
            stats['org_total_forks'] += repo_data.get('forks_count', 0)

    # 计算平均值
    if stats['org_repos_count'] > 0:
        stats['org_avg_stars_per_repo'] = stats['org_total_stars'] / stats['org_repos_count']

    return stats


def infer_domains_from_repos(repo_names, user_bio='', user_repos=None):
    """根据仓库名称直接映射、topics、用户简介推断研究方向"""
    domains = set()

    # 1. 优先：仓库名直接映射（最准确）
    repo_domain_map = CONFIG.get('REPO_DOMAIN_MAP', {})
    for repo_name in repo_names:
        if repo_name in repo_domain_map:
            domains.add(repo_domain_map[repo_name])

    # 2. 从用户简介中提取关键词
    text = (user_bio or '').lower()
    for key, value in CONFIG['DEFAULT_DOMAINS'].items():
        if key in text or value.lower() in text:
            domains.add(value)

    # 3. 收集所有仓库的 topics
    all_topics = []
    if user_repos:
        for repo in user_repos:
            if isinstance(repo, dict) and 'topics' in repo:
                topics = repo.get('topics', [])
                if topics:
                    all_topics.extend(topics)

    # 从 topics 中匹配
    topics_text = ' '.join(all_topics).lower()
    for key, value in CONFIG['DEFAULT_DOMAINS'].items():
        if key in topics_text:
            domains.add(value)

    # 4. 从仓库名称中匹配（补充，排除已直接映射的）
    unmapped_repos = [r for r in repo_names if r not in repo_domain_map]
    repo_text = ' '.join(unmapped_repos).lower()
    for key, value in CONFIG['DEFAULT_DOMAINS'].items():
        if key in repo_text:
            domains.add(value)

    # 5. 关键词模式推断（topics 优先，仓库名补充）
    search_text = topics_text if topics_text.strip() else repo_text

    keyword_rules = [
        (['machine-learning', 'sklearn'], '机器学习'),
        (['deep-learning', 'pytorch', 'tensorflow'], '深度学习'),
        (['nlp', 'natural-language', 'bert', 'transformer'], 'NLP'),
        (['recommendation', 'recommender-system', 'ctr-prediction'], '推荐系统'),
        (['computer-vision', 'opencv', 'yolo', 'image-classification'], '计算机视觉'),
        (['web', 'frontend', 'react', 'vue', 'javascript'], '前端开发'),
        (['gpt', 'llm', 'chatbot', 'llama', 'large-language-model'], 'LLM'),
        (['rag', 'retrieval-augmented'], 'RAG'),
        (['agent', 'multi-agent', 'agentic'], 'AI Agent'),
        (['embodied', 'robotics', 'robot', 'ros2'], '具身智能'),
        (['medical-imaging', 'medical-image'], '医学影像'),
        (['multimodal', 'audio', 'speech', 'text-to-image'], '多模态'),
        (['reinforcement-learning', 'reinforcement'], '强化学习'),
        (['hive', 'spark', 'hadoop'], '大数据'),
        (['competition', 'kaggle'], '数据竞赛'),
        (['database', 'sql', 'nosql', 'mongodb', 'mysql'], '数据库'),
    ]
    for keywords, domain in keyword_rules:
        if any(kw in search_text for kw in keywords):
            domains.add(domain)

    # 如果没有找到任何领域，设置默认值
    if not domains:
        domains.add('数据科学')

    return list(domains)


def compute_primary_domain(repo_names, domains, repo_commits=None):
    """根据各领域的commit次数，返回commit最多的领域；无commit数据时按仓库数回退"""
    repo_domain_map = CONFIG.get('REPO_DOMAIN_MAP', {})
    counts = {}
    if repo_commits:
        for repo, cnt in repo_commits.items():
            d = repo_domain_map.get(repo)
            if d:
                counts[d] = counts.get(d, 0) + cnt
    else:
        for repo in repo_names:
            d = repo_domain_map.get(repo)
            if d:
                counts[d] = counts.get(d, 0) + 1
    if counts:
        return max(counts, key=counts.get)
    return domains[0] if domains else '数据科学'


def clean_csv_field(text):
    """清理CSV字段中的换行符和其他问题字符"""
    if not text:
        return ''

    # 转换为字符串并清理
    text = str(text)

    # 替换换行符为空格
    text = text.replace('\n', ' ').replace('\r', ' ')

    # 替换多个连续空格为单个空格
    import re
    text = re.sub(r'\s+', ' ', text)

    # 去除首尾空格
    text = text.strip()

    return text


def save_to_csv(members, output_file):
    """保存数据到 CSV 文件"""
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        # 写入表头（包含所有字段，包括组织贡献数据）
        writer.writerow([
            'id', 'name', 'github', 'domain', 'primary_domain', 'repositories',
            'public_repos', 'total_stars', 'followers', 'following',
            'org_repos_count', 'org_total_stars', 'org_total_forks',
            'org_total_contributions', 'org_avg_stars_per_repo',
            'avatar', 'bio', 'location', 'company'
        ])

        # 写入数据
        for member in members:
            writer.writerow([
                clean_csv_field(member['id']),
                clean_csv_field(member['name']),
                clean_csv_field(member['github']),
                ';'.join(member['domains']),
                clean_csv_field(member.get('primary_domain', '')),
                ';'.join(member.get('repositories', [])),
                member.get('public_repos', 0),
                member.get('total_stars', 0),
                member.get('followers', 0),
                member.get('following', 0),
                member.get('org_repos_count', 0),
                member.get('org_total_stars', 0),
                member.get('org_total_forks', 0),
                member.get('org_total_contributions', 0),
                round(member.get('org_avg_stars_per_repo', 0), 2),
                clean_csv_field(member.get('avatar', '')),
                clean_csv_field(member.get('bio', '')),
                clean_csv_field(member.get('location', '')),
                clean_csv_field(member.get('company', ''))
            ])


def save_to_json(members, output_file):
    """保存数据到 json 文件"""
    # 写入数据
    input_data = []

    with open(output_file, 'w', newline='', encoding='utf-8') as jsonfile:
        for member in members:
            input_data.append({
                'id': clean_csv_field(member['id']),
                'name': clean_csv_field(member['name']),
                'github': clean_csv_field(member['github']),
                'domain': ';'.join(member['domains']),
                'primary_domain': member.get('primary_domain', ''),
                'repositories': ';'.join(member.get('repositories', [])),
                # 个人数据
                'public_repos': member.get('public_repos', 0),
                'total_stars': member.get('total_stars', 0),
                'followers': member.get('followers', 0),
                'following': member.get('following', 0),
                # 组织贡献数据
                'org_repos_count': member.get('org_repos_count', 0),
                'org_total_stars': member.get('org_total_stars', 0),
                'org_total_forks': member.get('org_total_forks', 0),
                'org_total_contributions': member.get('org_total_contributions', 0),
                'org_avg_stars_per_repo': round(member.get('org_avg_stars_per_repo', 0), 2),
                # 其他信息
                'avatar': clean_csv_field(member.get('avatar', '')),
                'bio': clean_csv_field(member.get('bio', '')),
                'location': clean_csv_field(member.get('location', '')),
                'company': clean_csv_field(member.get('company', ''))
            })
        json.dump(input_data, jsonfile, ensure_ascii=False, indent=4)


def check_existing_data():
    """检查现有数据文件"""
    return os.path.exists(CONFIG['OUTPUT_FILE']) or os.path.exists(CONFIG['OUTPUT_JSON_FILE'])


def backup_existing_data():
    """备份现有数据（已禁用，直接覆盖）"""
    # 不再创建备份文件，直接覆盖以节省空间
    if os.path.exists(CONFIG['OUTPUT_FILE']):
        print(f"📋 发现现有数据，将直接覆盖: {CONFIG['OUTPUT_FILE']}")
    if os.path.exists(CONFIG['OUTPUT_JSON_FILE']):
        print(f"📋 发现现有JSON数据，将直接覆盖: {CONFIG['OUTPUT_JSON_FILE']}")
    return None


def main():
    """主函数 - 统一版本，始终收集commit数据"""
    print("🚀 开始执行数据拉取脚本（包含commit数据）...")
    print(f"📁 输出文件: {CONFIG['OUTPUT_FILE']}, {CONFIG['OUTPUT_JSON_FILE']}")
    print(f"📊 Commit数据文件: {CONFIG['COMMITS_FILE']}")
    print(f"🏢 组织名称: {CONFIG['ORG_NAME']}")
    print(f"🔑 Token 状态: {'已配置' if CONFIG['GITHUB_TOKEN'] else '未配置'}")

    # 当未安装 requests 时优雅降级
    if requests is None:
        print("⚠️ 缺少 requests 库，跳过网络请求。")
        if check_existing_data():
            print("🔄 使用现有数据继续构建...")
            sys.exit(0)
        else:
            print("💥 没有现有数据可用，构建失败")
            sys.exit(1)

    has_existing_data = check_existing_data()
    overall_start_time = time.time()

    try:
        if has_existing_data:
            backup_existing_data()

        # 统一数据收集（同时获取成员和commit数据）
        contributors_data, all_commits, org_repos_cache, api_stats = collect_unified_data(
            CONFIG['ORG_NAME'], include_commits=True)

        if not contributors_data:
            print("⚠️  未找到任何贡献者数据")
            if has_existing_data:
                print("🔄 使用现有数据继续构建...")
                sys.exit(0)
            else:
                print("💥 没有现有数据可用，构建失败")
                sys.exit(1)

        # 预先聚合commit数据，用于计算primary_domain
        user_commits_agg = {}
        if all_commits:
            user_commits_agg = aggregate_commits_by_user(all_commits)

        # 处理成员数据
        print(f"\n👥 开始处理 {len(contributors_data)} 个成员的详细信息...")
        processed_members = []

        for username, contrib_info in contributors_data.items():
            print(f"\n👤 处理成员: {username}")

            try:
                # 获取用户详细信息
                user_details = get_user_details(username)
                api_stats['users'] += 1
                api_stats['total'] += 1

                if user_details:
                    print(f"  ✓ 获取用户信息: {user_details.get('name', 'N/A')}")

                # 获取用户仓库信息
                user_repos = get_user_repos(username)
                api_stats['user_repos'] += 1
                api_stats['total'] += 1
                print(f"  ✓ 获取用户仓库: {len(user_repos) if user_repos else 0} 个")

                # 计算用户统计信息（个人仓库数据）
                user_stats = calculate_user_stats(user_details, user_repos)
                print(
                    f"  ✓ 个人统计: {user_stats['public_repos']} 仓库, {user_stats['total_stars']} Stars, {user_stats['followers']} 关注者")

                # 计算组织贡献统计
                org_stats = calculate_org_contribution_stats(
                    username, contrib_info, org_repos_cache)
                print(
                    f"  ✓ 组织贡献: {org_stats['org_repos_count']} 个仓库, {org_stats['org_total_stars']} Stars, {org_stats['org_total_contributions']} 贡献数")

                # 下载并缓存头像
                avatar_url = user_details.get(
                    'avatar_url') if user_details else contrib_info['user_info'].get('avatar_url')
                local_avatar = download_avatar(avatar_url, username)

                # 推断研究方向（基于仓库 topics、参与的仓库名称和用户简介）
                user_bio = user_details.get('bio') if user_details else ''
                domains = infer_domains_from_repos(
                    contrib_info['repos'], user_bio, user_repos)
                print(f"  ✓ 推断研究方向: {', '.join(domains)}")

                repo_commits = user_commits_agg.get(username, {}).get('repo_commits', None)
                primary_domain = compute_primary_domain(contrib_info['repos'], domains, repo_commits)

                processed_members.append({
                    'id': username,
                    'name': user_details.get('name') if user_details else username,
                    'github': contrib_info['user_info']['html_url'],
                    'domains': domains,
                    'primary_domain': primary_domain,
                    'repositories': contrib_info['repos'],  # 参与的组织仓库列表
                    # 个人数据（保留用于参考）
                    'public_repos': user_stats['public_repos'],  # 个人公开仓库数
                    'total_stars': user_stats['total_stars'],  # 个人仓库总 Stars 数
                    'followers': user_stats['followers'],  # 关注者数
                    'following': user_stats['following'],  # 关注数
                    # 组织贡献数据（用于榜单排名）
                    'org_repos_count': org_stats['org_repos_count'],  # 参与的组织仓库数量
                    'org_total_stars': org_stats['org_total_stars'],  # 参与的组织仓库总 stars
                    'org_total_forks': org_stats['org_total_forks'],  # 参与的组织仓库总 forks
                    'org_total_contributions': org_stats['org_total_contributions'],  # 在组织中的总贡献数
                    'org_avg_stars_per_repo': org_stats['org_avg_stars_per_repo'],  # 平均每个参与仓库的 stars
                    # 其他信息
                    'avatar': local_avatar,  # 本地头像路径
                    'bio': user_details.get('bio') if user_details else '',
                    'location': user_details.get('location') if user_details else '',
                    'company': user_details.get('company') if user_details else ''
                })

            except Exception as e:
                print(f"  ❌ 处理成员 {username} 时出错: {e}")
                continue

        if processed_members:
            # 保存成员数据
            save_to_csv(processed_members, CONFIG['OUTPUT_FILE'])
            save_to_json(processed_members, CONFIG['OUTPUT_JSON_FILE'])

            print(f"✅ 成功处理 {len(processed_members)} 个成员")

            # 处理并保存commit数据
            if all_commits:
                print(f"\n📊 处理 {len(all_commits)} 个commit数据...")

                commits_data = {
                    'update_time': datetime.now().isoformat(),
                    'days_range': CONFIG['COMMIT_DAYS_RANGE'],
                    'total_commits': len(all_commits),
                    'total_repos': len(set(commit['repo'] for commit in all_commits)),
                    'user_commits': user_commits_agg,
                    'optimization_stats': {
                        'api_calls': api_stats,
                        'execution_time': f"{time.time() - overall_start_time:.1f}s",
                        'optimization_enabled': True
                    }
                }

                save_commits_data(commits_data)

            # 显示执行统计
            total_time = time.time() - overall_start_time
            print(f"\n🎉 执行完成!")
            print(f"📊 性能统计:")
            print(f"  - 总API调用: {api_stats['total']} 次")
            print(f"  - 总执行时间: {total_time:.1f} 秒")

        else:
            print("❌ 没有成功处理任何成员")
            if has_existing_data:
                print("🔄 使用现有数据继续构建...")
                sys.exit(0)
            else:
                print("💥 构建失败")
                sys.exit(1)

    except Exception as e:
        print(f"💥 脚本执行失败: {e}")
        import traceback
        traceback.print_exc()

        if has_existing_data:
            print("🔄 使用现有数据继续构建...")
            sys.exit(0)
        else:
            print("💥 没有现有数据可用，构建失败")
            sys.exit(1)


def get_recent_commits_for_repo(org_name, repo_name, days=7):
    """获取指定仓库最近N天的commit数据"""

    # 计算时间范围
    since_date = datetime.now() - timedelta(days=days)
    since_iso = since_date.isoformat() + 'Z'

    url = f"{CONFIG['API_BASE']}/repos/{org_name}/{repo_name}/commits"
    params = {
        'since': since_iso,
        'per_page': CONFIG['MAX_COMMITS_PER_REPO']
    }

    try:
        response = requests.get(
            url, headers=get_headers(), params=params, timeout=30)
        if response.status_code == 200:
            commits = response.json()
            print(f"  📊 仓库 {repo_name}: 获取到 {len(commits)} 个commit")
            return commits
        else:
            print(
                f"  ⚠️  仓库 {repo_name}: 获取commit失败 (状态码: {response.status_code})")
            return []
    except Exception as e:
        print(f"  ❌ 仓库 {repo_name}: 获取commit异常: {e}")
        return []


def process_commits_data(commits, repo_name):
    """处理commit数据，提取关键信息"""

    processed_commits = []

    for commit in commits:
        try:
            # 提取commit信息
            commit_data = {
                'sha': commit['sha'][:8],  # 短SHA
                # 第一行消息，限制长度
                'message': commit['commit']['message'].split('\n')[0][:100],
                'author': {
                    'name': commit['commit']['author']['name'],
                    'email': commit['commit']['author']['email'],
                    'date': commit['commit']['author']['date']
                },
                'repo': repo_name,
                'url': commit['html_url']
            }

            # 尝试获取GitHub用户名
            if commit.get('author') and commit['author']:
                commit_data['github_username'] = commit['author']['login']
            else:
                # 如果没有GitHub用户信息，尝试从email推断
                commit_data['github_username'] = None

            # 解析日期
            commit_date = datetime.fromisoformat(
                commit_data['author']['date'].replace('Z', '+00:00'))
            commit_data['date_parsed'] = commit_date
            commit_data['date_str'] = commit_date.strftime('%Y-%m-%d')
            commit_data['hour'] = commit_date.hour

            processed_commits.append(commit_data)

        except Exception as e:
            print(f"    ⚠️  处理commit数据时出错: {e}")
            continue

    return processed_commits


def collect_weekly_commits_data(org_name, days=7):
    """收集组织所有仓库的周commit数据"""
    print(f"🚀 开始收集 {org_name} 组织最近 {days} 天的commit数据...")

    # 获取组织仓库列表
    repos = get_org_repos(org_name)
    if not repos:
        print("❌ 无法获取组织仓库列表")
        return {}

    all_commits = []
    processed_repos = 0

    for repo in repos:
        repo_name = repo['name']
        print(f"📁 处理仓库: {repo_name} ({processed_repos + 1}/{len(repos)})")

        # 获取仓库的commit数据
        commits = get_recent_commits_for_repo(org_name, repo_name, days)

        if commits:
            # 处理commit数据
            processed_commits = process_commits_data(commits, repo_name)
            all_commits.extend(processed_commits)

        processed_repos += 1

        # 添加延迟避免API速率限制
        time.sleep(0.5)

        # 每处理10个仓库显示进度
        if processed_repos % 10 == 0:
            print(f"  ✅ 已处理 {processed_repos}/{len(repos)} 个仓库")

    print(f"📊 总共收集到 {len(all_commits)} 个commit")

    # 按用户聚合commit数据
    user_commits = aggregate_commits_by_user(all_commits)

    return {
        'update_time': datetime.now().isoformat(),
        'days_range': days,
        'total_commits': len(all_commits),
        'total_repos': len(repos),
        'user_commits': user_commits,
        'raw_commits': all_commits[:1000]  # 只保存前1000个原始commit用于调试
    }


def aggregate_commits_by_user(commits):
    """按用户聚合commit数据"""
    from collections import defaultdict

    user_stats = defaultdict(lambda: {
        'total_commits': 0,
        'repos': set(),
        'daily_commits': defaultdict(int),
        'hourly_distribution': defaultdict(int),
        'commit_messages': [],
        'first_commit_date': None,
        'last_commit_date': None
    })

    for commit in commits:
        # 确定用户标识（优先使用GitHub用户名，否则使用邮箱）
        user_key = commit.get('github_username') or commit['author']['email']

        if not user_key:
            continue

        stats = user_stats[user_key]

        # 更新统计信息
        stats['total_commits'] += 1
        stats['repos'].add(commit['repo'])
        stats['daily_commits'][commit['date_str']] += 1
        stats['hourly_distribution'][commit['hour']] += 1

        # 保存commit消息（最多保存10个）
        if len(stats['commit_messages']) < 10:
            stats['commit_messages'].append({
                'message': commit['message'],
                'repo': commit['repo'],
                'date': commit['date_str'],
                'url': commit['url']
            })

        # 更新时间范围
        commit_date = commit['date_parsed']
        if not stats['first_commit_date'] or commit_date < stats['first_commit_date']:
            stats['first_commit_date'] = commit_date
        if not stats['last_commit_date'] or commit_date > stats['last_commit_date']:
            stats['last_commit_date'] = commit_date

    # 转换为可序列化的格式
    result = {}
    for user_key, stats in user_stats.items():
        result[user_key] = {
            'total_commits': stats['total_commits'],
            'repos': list(stats['repos']),
            'repo_count': len(stats['repos']),
            'daily_commits': dict(stats['daily_commits']),
            'hourly_distribution': dict(stats['hourly_distribution']),
            'commit_messages': stats['commit_messages'],
            'first_commit_date': stats['first_commit_date'].isoformat() if stats['first_commit_date'] else None,
            'last_commit_date': stats['last_commit_date'].isoformat() if stats['last_commit_date'] else None,
            'active_days': len(stats['daily_commits']),
            'avg_commits_per_day': stats['total_commits'] / max(len(stats['daily_commits']), 1)
        }

    return result


def save_commits_data(commits_data):
    """保存commit数据到JSON文件"""
    try:
        # 确保目录存在
        CONFIG['COMMITS_FILE'].parent.mkdir(parents=True, exist_ok=True)

        with open(CONFIG['COMMITS_FILE'], 'w', encoding='utf-8') as f:
            json.dump(commits_data, f, ensure_ascii=False, indent=2)

        print(f"💾 commit数据已保存到: {CONFIG['COMMITS_FILE']}")
        return True

    except Exception as e:
        print(f"❌ 保存commit数据失败: {e}")
        return False


def collect_unified_data(org_name, include_commits=False):
    """
    优化的统一数据收集函数
    在单次遍历中同时收集成员信息和commit数据
    """
    print(f"🚀 开始统一数据收集 (包含commit: {include_commits})...")

    # 性能监控变量
    api_calls = {
        'repos_list': 0,
        'contributors': 0,
        'commits': 0,
        'users': 0,
        'user_repos': 0,
        'total': 0
    }
    start_time = time.time()

    # 获取组织仓库列表（只调用一次）
    print("📁 获取组织仓库列表...")
    repos = get_org_repos(org_name)
    api_calls['repos_list'] = 1
    api_calls['total'] += 1

    if not repos:
        print("❌ 无法获取组织仓库列表")
        return None, None, api_calls

    print(f"✅ 找到 {len(repos)} 个仓库")

    # 初始化数据结构
    contributors_data = {}  # 贡献者信息
    all_commits = []       # 所有commit记录
    org_repos_cache = {}   # 组织仓库缓存 {repo_name: repo_data}
    processed_repos = 0

    # 计算时间范围（用于commit过滤）
    if include_commits:
        since_date = datetime.now() - \
            timedelta(days=CONFIG['COMMIT_DAYS_RANGE'])
        since_iso = since_date.isoformat() + 'Z'

    # 单次遍历所有仓库，同时收集贡献者和commit数据
    for repo in repos:
        repo_name = repo['name']
        print(f"\n📦 处理仓库: {repo_name} ({processed_repos + 1}/{len(repos)})")

        try:
            # 缓存仓库数据（用于后续计算组织贡献统计）
            org_repos_cache[repo_name] = {
                'name': repo_name,
                'stargazers_count': repo.get('stargazers_count', 0),
                'forks_count': repo.get('forks_count', 0),
                'watchers_count': repo.get('watchers_count', 0),
                'open_issues_count': repo.get('open_issues_count', 0)
            }

            # 1. 获取仓库贡献者信息
            print(f"  👥 获取贡献者...")
            contributors_url = f"{CONFIG['API_BASE']}/repos/{org_name}/{repo_name}/contributors"
            contributors_params = {
                'per_page': CONFIG['MAX_CONTRIBUTORS_PER_REPO']}

            contributors_full_url = f"{contributors_url}?per_page={contributors_params['per_page']}"
            contributors = fetch_api(contributors_full_url)
            api_calls['contributors'] += 1
            api_calls['total'] += 1

            if contributors:
                print(f"    ✓ 找到 {len(contributors)} 个贡献者")

                # 处理贡献者数据
                for contributor in contributors:
                    if contributor['contributions'] >= CONFIG['MIN_CONTRIBUTIONS']:
                        username = contributor['login']

                        # 检查是否为机器人账户
                        if is_bot_account(username):
                            print(f"    🤖 跳过机器人账户: {username}")
                            continue

                        if username not in contributors_data:
                            contributors_data[username] = {
                                'user_info': contributor,
                                'repos': [],
                                'total_contributions': 0
                            }

                        contributors_data[username]['repos'].append(repo_name)
                        contributors_data[username]['total_contributions'] += contributor['contributions']

            # 2. 获取commit数据（如果需要）
            if include_commits:
                print(f"  📊 获取commit数据...")
                commits_url = f"{CONFIG['API_BASE']}/repos/{org_name}/{repo_name}/commits"
                commits_params = {
                    'since': since_iso,
                    'per_page': CONFIG['MAX_COMMITS_PER_REPO']
                }

                commits_full_url = f"{commits_url}?since={commits_params['since']}&per_page={commits_params['per_page']}"
                commits = fetch_api(commits_full_url)
                api_calls['commits'] += 1
                api_calls['total'] += 1

                if commits:
                    print(f"    ✓ 找到 {len(commits)} 个commit")

                    # 处理commit数据
                    for commit in commits:
                        try:
                            commit_data = {
                                'sha': commit['sha'][:8],
                                'message': commit['commit']['message'].split('\n')[0][:100],
                                'author': {
                                    'name': commit['commit']['author']['name'],
                                    'email': commit['commit']['author']['email'],
                                    'date': commit['commit']['author']['date']
                                },
                                'repo': repo_name,
                                'url': commit['html_url']
                            }

                            # 尝试获取GitHub用户名
                            if commit.get('author') and commit['author']:
                                commit_data['github_username'] = commit['author']['login']
                                # 获取头像URL用于后续下载
                                commit_data['author_avatar_url'] = commit['author'].get(
                                    'avatar_url')
                            else:
                                commit_data['github_username'] = None
                                commit_data['author_avatar_url'] = None

                            # 检查是否为机器人账户的提交
                            if commit_data['github_username'] and is_bot_account(commit_data['github_username']):
                                print(
                                    f"      🤖 跳过机器人提交: {commit_data['github_username']}")
                                continue

                            # 检查并下载新发现贡献者的头像
                            if commit_data['github_username'] and commit_data['author_avatar_url']:
                                ensure_avatar_exists(
                                    commit_data['github_username'], commit_data['author_avatar_url'])

                                # 如果这个用户不在 contributors_data 中，添加进去
                                # 这样可以确保所有有 commit 的用户都会被采集到 members.json
                                if commit_data['github_username'] not in contributors_data:
                                    contributors_data[commit_data['github_username']] = {
                                        'user_info': {
                                            'login': commit_data['github_username'],
                                            'html_url': f"https://github.com/{commit_data['github_username']}",
                                            'avatar_url': commit_data['author_avatar_url']
                                        },
                                        'repos': [repo_name],
                                        'total_contributions': 1  # 至少有 1 个 commit
                                    }
                                    print(f"      ➕ 新增贡献者（来自commit）: {commit_data['github_username']}")
                                elif repo_name not in contributors_data[commit_data['github_username']]['repos']:
                                    # 如果用户已存在但这个仓库不在列表中，添加仓库
                                    contributors_data[commit_data['github_username']]['repos'].append(repo_name)

                            # 解析日期
                            commit_date = datetime.fromisoformat(
                                commit_data['author']['date'].replace('Z', '+00:00'))
                            commit_data['date_parsed'] = commit_date
                            commit_data['date_str'] = commit_date.strftime(
                                '%Y-%m-%d')
                            commit_data['hour'] = commit_date.hour

                            # 转换为北京时间（UTC+8）
                            beijing_time = commit_date + timedelta(hours=8)
                            commit_data['beijing_hour'] = beijing_time.hour
                            commit_data['beijing_time'] = beijing_time.isoformat()

                            # 判断是否为深夜时段（北京时间22:00-06:00）
                            is_night_owl = beijing_time.hour >= 22 or beijing_time.hour < 6
                            commit_data['is_night_owl'] = is_night_owl

                            all_commits.append(commit_data)

                        except Exception as e:
                            print(f"      ⚠️  处理commit数据时出错: {e}")
                            continue

            processed_repos += 1

            # 每处理10个仓库显示进度
            if processed_repos % 10 == 0:
                elapsed = time.time() - start_time
                print(
                    f"  📈 进度: {processed_repos}/{len(repos)} 仓库 | 耗时: {elapsed:.1f}s | API调用: {api_calls['total']}")

        except Exception as e:
            print(f"  ❌ 处理仓库 {repo_name} 时出错: {e}")
            continue

    # 统计结果
    elapsed_time = time.time() - start_time
    print(f"\n📊 数据收集完成:")
    print(f"  - 处理仓库: {processed_repos}/{len(repos)}")
    print(f"  - 缓存组织仓库: {len(org_repos_cache)} 个")
    print(f"  - 发现贡献者: {len(contributors_data)} 人")
    if include_commits:
        print(f"  - 收集commit: {len(all_commits)} 个")
    print(f"  - API调用统计: {api_calls}")
    print(f"  - 总耗时: {elapsed_time:.1f} 秒")

    return contributors_data, all_commits if include_commits else None, org_repos_cache, api_calls


def aggregate_commits_by_user(all_commits):
    """聚合commit数据按用户分组"""

    user_stats = defaultdict(lambda: {
        'total_commits': 0,
        'repos': set(),
        'repo_commits': defaultdict(int),
        'daily_commits': defaultdict(int),
        'hourly_distribution': defaultdict(int),
        'beijing_hourly_distribution': defaultdict(int),
        'night_owl_commits': 0,
        'commit_messages': [],
        'first_commit_date': None,
        'last_commit_date': None
    })

    for commit in all_commits:
        # 尝试获取GitHub用户名
        username = commit.get('github_username')
        if not username:
            # 如果没有GitHub用户名，尝试从email推断
            email = commit['author']['email']
            if email and '@' in email:
                username = email.split('@')[0]
            else:
                continue  # 跳过无法识别用户的commit

        # 双重检查：确保不是机器人账户
        if is_bot_account(username):
            continue  # 跳过机器人账户的commit

        stats = user_stats[username]

        # 更新统计
        stats['total_commits'] += 1
        stats['repos'].add(commit['repo'])
        stats['repo_commits'][commit['repo']] += 1
        stats['daily_commits'][commit['date_str']] += 1
        stats['hourly_distribution'][commit['hour']] += 1
        stats['beijing_hourly_distribution'][commit['beijing_hour']] += 1

        # 统计深夜提交
        if commit.get('is_night_owl', False):
            stats['night_owl_commits'] += 1

        # 保存commit消息（最多10个）
        if len(stats['commit_messages']) < 10:
            stats['commit_messages'].append({
                'message': commit['message'],
                'repo': commit['repo'],
                'date': commit['date_str'],
                'time': commit.get('beijing_time', ''),
                'beijing_hour': commit.get('beijing_hour', 0),
                'is_night_owl': commit.get('is_night_owl', False),
                'url': commit['url']
            })

        # 更新时间范围
        commit_date = commit['date_parsed']
        if not stats['first_commit_date'] or commit_date < stats['first_commit_date']:
            stats['first_commit_date'] = commit_date
        if not stats['last_commit_date'] or commit_date > stats['last_commit_date']:
            stats['last_commit_date'] = commit_date

    # 转换为可序列化格式
    result = {}
    for username, stats in user_stats.items():
        if stats['total_commits'] >= 1:  # 至少1个commit
            result[username] = {
                'total_commits': stats['total_commits'],
                'repos': list(stats['repos']),
                'repo_commits': dict(stats['repo_commits']),
                'repo_count': len(stats['repos']),
                'daily_commits': dict(stats['daily_commits']),
                'hourly_distribution': dict(stats['hourly_distribution']),
                'beijing_hourly_distribution': dict(stats['beijing_hourly_distribution']),
                'night_owl_commits': stats['night_owl_commits'],
                'night_owl_percentage': round((stats['night_owl_commits'] / stats['total_commits']) * 100, 1) if stats['total_commits'] > 0 else 0,
                'commit_messages': stats['commit_messages'],
                'first_commit_date': stats['first_commit_date'].isoformat() if stats['first_commit_date'] else None,
                'last_commit_date': stats['last_commit_date'].isoformat() if stats['last_commit_date'] else None,
                'active_days': len(stats['daily_commits']),
                'avg_commits_per_day': stats['total_commits'] / max(len(stats['daily_commits']), 1)
            }

    return result


def save_commits_data(commits_data):
    """保存commit数据到文件"""
    try:
        # 确保目录存在
        CONFIG['COMMITS_FILE'].parent.mkdir(parents=True, exist_ok=True)

        # 直接保存到前端目录
        with open(CONFIG['COMMITS_FILE'], 'w', encoding='utf-8') as f:
            json.dump(commits_data, f, ensure_ascii=False, indent=2)

        print(f"💾 Commit数据已保存:")
        print(f"  - 文件路径: {CONFIG['COMMITS_FILE']}")
        print(
            f"  - 活跃用户: {commits_data.get('user_commits', {}) and len(commits_data['user_commits'])} 人")
        print(f"  - 总commit数: {commits_data.get('total_commits', 0)}")

        return True

    except Exception as e:
        print(f"❌ 保存commit数据失败: {e}")
        return False


def test():
    """测试函数 - 使用较小的配置值进行快速本地测试"""
    print("🧪 开始测试模式...")

    # 临时覆盖配置值以加快测试速度（只限制总仓库数和总贡献者数）
    original_config = {}
    test_config = {
        'MAX_REPOS_PER_PAGE': 100,   # 保持正常的每页仓库数
        'MAX_CONTRIBUTORS_PER_REPO': 10,  # 限制每个仓库的贡献者数（控制总贡献者数）
    }

    # 设置测试模式标志，用于限制总仓库数
    CONFIG['TEST_MODE'] = True
    CONFIG['TEST_MAX_REPOS'] = 15  # 测试模式下最多处理5个仓库

    # 保存原始配置并应用测试配置
    for key, value in test_config.items():
        original_config[key] = CONFIG[key]
        CONFIG[key] = value
        print(f"  📝 {key}: {original_config[key]} → {value}")

    print(f"  ℹ️  保持原有配置:")
    print(f"     MIN_CONTRIBUTIONS = {CONFIG['MIN_CONTRIBUTIONS']} (贡献阈值不变)")
    print(f"     COMMIT_DAYS_RANGE = {CONFIG['COMMIT_DAYS_RANGE']} 天")
    print(
        f"  🎯 测试预期: 最多处理 {test_config['MAX_REPOS_PER_PAGE']} 个仓库，每个仓库最多 {test_config['MAX_CONTRIBUTORS_PER_REPO']} 个贡献者")

    try:
        # 运行主函数（现在默认包含commit数据收集）
        main()
    finally:
        # 恢复原始配置
        for key, value in original_config.items():
            CONFIG[key] = value
        # 清理测试模式标志
        CONFIG.pop('TEST_MODE', None)
        CONFIG.pop('TEST_MAX_REPOS', None)
        print("🔄 已恢复原始配置")


if __name__ == '__main__':
    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == '--test':
            test()
        else:
            print("❌ 未知参数。支持的参数：--test")
            print("💡 提示：脚本现在默认收集commit数据，无需 --with-commits 参数")
            sys.exit(1)
    else:
        main()
