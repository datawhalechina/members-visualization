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
    'OUTPUT_FILE': Path(__file__).parent.parent / 'data' / 'members.csv',
    'COMMITS_FILE': Path(__file__).parent.parent / 'data' / 'commits_weekly.json',  # 周commit数据文件
    'AVATARS_DIR': Path(__file__).parent.parent / 'docs' / 'public' / 'avatars',  # 头像缓存目录
    'API_BASE': 'https://api.github.com',
    'MIN_CONTRIBUTIONS': int(os.getenv('MIN_CONTRIBUTIONS', '10')),  # 最小贡献行数阈值（降低以包含更多贡献者）
    'MAX_REPOS_PER_PAGE': 100,  # 每页最大仓库数
    'MAX_CONTRIBUTORS_PER_REPO': 100,  # 每个仓库最大贡献者数
    'MAX_USER_REPOS': 100,  # 获取用户仓库的最大数量
    'COMMIT_DAYS_RANGE': 7,  # 获取最近N天的commit数据
    'MAX_COMMITS_PER_REPO': 200,  # 每个仓库最大commit数
    'DEFAULT_DOMAINS': {
        'machine-learning': '机器学习',
        'deep-learning': '深度学习',
        'nlp': 'NLP',
        'cv': 'CV',
        'data-mining': '数据挖掘',
        'recommendation-system': '推荐系统',
        'reinforcement-learning': '强化学习',
        'computer-vision': 'CV',
        'natural-language-processing': 'NLP',
        'artificial-intelligence': '人工智能',
        'llm': 'LLM',
        'data-science': '数据科学',
        'frontend': '前端开发',
        'backend': '后端开发',
        'fullstack': '全栈开发',
        'bigdata': '大数据'
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
        original_repos = [repo for repo in repos if not repo.get('fork', False)]
        all_repos.extend(original_repos)

        print(f"获取第 {page} 页：{len(repos)} 个仓库（{len(original_repos)} 个原创）")

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

def get_repo_contributors(owner, repo_name):
    """获取仓库贡献者列表（支持分页）"""
    all_contributors = []
    page = 1
    per_page = 100

    while True:
        url = f"{CONFIG['API_BASE']}/repos/{owner}/{repo_name}/contributors?per_page={per_page}&page={page}"
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

    # 过滤掉贡献数低于阈值的贡献者
    qualified_contributors = []
    for contributor in all_contributors:
        contributions = contributor.get('contributions', 0)
        if contributions >= CONFIG['MIN_CONTRIBUTIONS']:
            qualified_contributors.append({
                'login': contributor['login'],
                'contributions': contributions,
                'html_url': contributor['html_url'],
                'avatar_url': contributor['avatar_url']
            })

    print(f"    📊 总贡献者: {len(all_contributors)}, 符合条件(≥{CONFIG['MIN_CONTRIBUTIONS']}行): {len(qualified_contributors)}")
    return qualified_contributors

def collect_contributors_from_repos(org_name):
    """从组织仓库中收集贡献者数据"""
    print(f"🚀 开始从 {org_name} 组织仓库收集贡献者数据...")

    # 获取组织所有仓库
    repos = get_org_repos(org_name)
    if not repos:
        print("❌ 未找到任何仓库")
        return {}

    contributors_data = {}  # {username: {repos: [repo_names], total_contributions: int, user_info: dict}}

    for i, repo in enumerate(repos):
        repo_name = repo['name']
        print(f"\n📁 处理仓库 {i + 1}/{len(repos)}: {repo_name}")

        try:
            # 获取仓库贡献者
            contributors = get_repo_contributors(org_name, repo_name)
            print(f"  ✓ 找到 {len(contributors)} 个符合条件的贡献者（≥{CONFIG['MIN_CONTRIBUTIONS']}行）")

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
    """计算用户统计信息"""
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

    # 计算总 Stars（从用户仓库中累加）
    if user_repos:
        stats['total_stars'] = sum(repo.get('stargazers_count', 0) for repo in user_repos)

    return stats

def infer_domains_from_repos(repo_names, user_bio='', user_repos=None):
    """根据仓库 topics、名称和用户简介推断研究方向"""
    domains = set()

    # 从用户简介中提取关键词
    text = (user_bio or '').lower()
    for key, value in CONFIG['DEFAULT_DOMAINS'].items():
        if key in text or value.lower() in text:
            domains.add(value)

    # 收集所有仓库的 topics
    all_topics = []
    if user_repos:
        for repo in user_repos:
            if isinstance(repo, dict) and 'topics' in repo:
                topics = repo.get('topics', [])
                if topics:
                    all_topics.extend(topics)

    # 从仓库 topics 中提取关键词（优先使用 topics）
    topics_text = ' '.join(all_topics).lower()
    for key, value in CONFIG['DEFAULT_DOMAINS'].items():
        if key in topics_text or value.lower() in topics_text:
            domains.add(value)

    # 如果 topics 中没有找到足够信息，再从仓库名称中提取关键词作为补充
    repo_text = ' '.join(repo_names).lower()
    for key, value in CONFIG['DEFAULT_DOMAINS'].items():
        if key in repo_text or value.lower() in repo_text:
            domains.add(value)

    # 根据 topics 和仓库名称的常见模式推断（优先使用 topics）
    search_text = topics_text if topics_text.strip() else repo_text

    if any(keyword in search_text for keyword in ['ml', 'machine-learning', 'sklearn']):
        domains.add('机器学习')
    if any(keyword in search_text for keyword in ['dl', 'deep-learning', 'pytorch', 'tensorflow']):
        domains.add('深度学习')
    if any(keyword in search_text for keyword in ['nlp', 'natural-language', 'bert', 'transformer']):
        domains.add('NLP')
    if any(keyword in search_text for keyword in ['recommendation', 'recommendation-system', 'ctr-prediction', 'recommender-system']):
        domains.add('推荐系统')
    if any(keyword in search_text for keyword in ['cv', 'computer-vision', 'opencv', 'image', 'yolo']):
        domains.add('CV')
    if any(keyword in search_text for keyword in ['web', 'frontend', 'react', 'vue', 'javascript']):
        domains.add('前端开发')
    if any(keyword in search_text for keyword in ['gpt', 'llm', 'chatbot', 'llama']):
        domains.add('LLM')
    if any(keyword in search_text for keyword in ['rag', 'retrieval-augmented-generation', 'retrieval-augmented']):
        domains.add('RAG')
    if any(keyword in search_text for keyword in ['database', 'sql', 'nosql', 'mongodb', 'mysql']):
        domains.add('数据库开发')
    if any(keyword in search_text for keyword in ['reinforcement-learning', 'rl', 'reinforcement']):
        domains.add('强化学习')
    if any(keyword in search_text for keyword in ['hive', 'spark', 'hadoop']):
        domains.add('大数据')
    if any(keyword in search_text for keyword in ['competition']):
        domains.add('数据竞赛')

    # 如果没有找到任何领域，设置默认值
    if not domains:
        domains.add('数据科学')

    return list(domains)

def save_to_csv(members, output_file):
    """保存数据到 CSV 文件"""
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        # 写入表头（包含所有字段）
        writer.writerow([
            'id', 'name', 'github', 'domain', 'repositories',
            'public_repos', 'total_stars', 'followers', 'following',
            'avatar', 'bio', 'location', 'company'
        ])

        # 写入数据
        for member in members:
            writer.writerow([
                member['id'],
                member['name'],
                member['github'],
                ';'.join(member['domains']),
                ';'.join(member.get('repositories', [])),
                member.get('public_repos', 0),
                member.get('total_stars', 0),
                member.get('followers', 0),
                member.get('following', 0),
                member.get('avatar', ''),
                member.get('bio', ''),
                member.get('location', ''),
                member.get('company', '')
            ])

def check_existing_data():
    """检查现有数据文件"""
    return os.path.exists(CONFIG['OUTPUT_FILE'])

def backup_existing_data():
    """备份现有数据"""
    if os.path.exists(CONFIG['OUTPUT_FILE']):
        # 将Path对象转换为字符串进行操作
        output_file_str = str(CONFIG['OUTPUT_FILE'])
        backup_path = output_file_str.replace('.csv', f'.backup.{int(time.time())}.csv')
        import shutil
        shutil.copy2(CONFIG['OUTPUT_FILE'], backup_path)
        print(f"📋 已备份现有数据: {backup_path}")
        return backup_path
    return None

def main():
    """主函数"""
    print("🚀 开始执行数据拉取脚本...")
    print(f"📁 输出文件: {CONFIG['OUTPUT_FILE']}")
    print(f"🏢 组织名称: {CONFIG['ORG_NAME']}")
    print(f"🔑 Token 状态: {'已配置' if CONFIG['GITHUB_TOKEN'] else '未配置'}")

    # 当未安装 requests 时优雅降级：若有现有数据则继续构建，否则失败
    if requests is None:
        print("⚠️ 缺少 requests 库，跳过网络请求。")
        if check_existing_data():
            print("🔄 使用现有数据继续构建...")
            sys.exit(0)
        else:
            print("💥 没有现有数据可用，构建失败")
            sys.exit(1)
    has_existing_data = check_existing_data()

    try:
        print("🚀 开始拉取成员数据...")

        if has_existing_data:
            backup_existing_data()

        # 从组织仓库收集贡献者数据
        contributors_data = collect_contributors_from_repos(CONFIG['ORG_NAME'])

        if not contributors_data:
            print("⚠️  未找到任何贡献者数据")

            if has_existing_data:
                print("✅ 保持使用现有数据")
                return
            else:
                raise Exception("没有现有数据可用，且无法获取新数据")

        # 处理每个贡献者
        processed_members = []
        contributors_list = list(contributors_data.items())
        # 处理所有贡献者（可通过环境变量限制）
        max_contributors = min(len(contributors_list), int(os.getenv('MAX_CONTRIBUTORS', '200')))
        print(f"\n📊 准备处理 {max_contributors} 个贡献者（总共 {len(contributors_list)} 个）")

        for i, (username, contrib_info) in enumerate(contributors_list[:max_contributors]):
            print(f"\n👤 处理贡献者 {i + 1}/{max_contributors}: {username}")
            print(f"  📈 总贡献: {contrib_info['total_contributions']} 行")
            print(f"  📁 参与仓库: {len(contrib_info['repos'])} 个 - {', '.join(contrib_info['repos'][:3])}{'...' if len(contrib_info['repos']) > 3 else ''}")

            try:
                # 获取用户详细信息
                user_details = get_user_details(username)
                if user_details:
                    print(f"  ✓ 获取用户详情: {user_details.get('name', username)}")
                else:
                    print(f"  ⚠️ 用户详情获取失败，使用基本信息")

                # 获取用户个人仓库（用于计算 Stars 等统计信息）
                user_repos = get_user_repos(username)
                print(f"  ✓ 获取个人仓库: {len(user_repos)} 个")

                # 计算用户统计信息
                user_stats = calculate_user_stats(user_details, user_repos)
                print(f"  ✓ 统计信息: {user_stats['public_repos']} 仓库, {user_stats['total_stars']} Stars, {user_stats['followers']} 关注者")

                # 下载并缓存头像
                avatar_url = user_details.get('avatar_url') if user_details else contrib_info['user_info'].get('avatar_url')
                local_avatar = download_avatar(avatar_url, username)

                # 推断研究方向（基于仓库 topics、参与的仓库名称和用户简介）
                user_bio = user_details.get('bio') if user_details else ''
                domains = infer_domains_from_repos(contrib_info['repos'], user_bio, user_repos)
                print(f"  ✓ 推断研究方向: {', '.join(domains)}")

                processed_members.append({
                    'id': username,
                    'name': user_details.get('name') if user_details else username,
                    'github': contrib_info['user_info']['html_url'],
                    'domains': domains,
                    'repositories': contrib_info['repos'],  # 参与的组织仓库列表
                    'public_repos': user_stats['public_repos'],  # 个人公开仓库数
                    'total_stars': user_stats['total_stars'],  # 总 Stars 数
                    'followers': user_stats['followers'],  # 关注者数
                    'following': user_stats['following'],  # 关注中数
                    'avatar': local_avatar or avatar_url,  # 头像路径（优先本地缓存）
                    'bio': user_details.get('bio', '') if user_details else '',  # 个人简介
                    'location': user_details.get('location', '') if user_details else '',  # 位置
                    'company': user_details.get('company', '') if user_details else ''  # 公司
                })

                # 动态延迟以避免 API 速率限制
                delay = 0.1 if CONFIG['GITHUB_TOKEN'] else 0.3
                time.sleep(delay)

            except Exception as e:
                print(f"⚠️  处理贡献者 {username} 时出错: {e}")
                print(f"  错误类型: {type(e).__name__}")
                import traceback
                print(f"  详细错误: {traceback.format_exc()}")
                # 继续处理其他贡献者

        if not processed_members:
            raise Exception("没有成功处理任何成员数据")

        # 保存到 CSV
        save_to_csv(processed_members, CONFIG['OUTPUT_FILE'])

        print(f"✅ 成功生成 CSV 文件: {CONFIG['OUTPUT_FILE']}")
        print(f"📊 处理了 {len(processed_members)} 个成员")

    except Exception as e:
        print(f"❌ 数据拉取失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")

        if has_existing_data:
            print("🔄 使用现有数据继续构建...")
            print("💡 提示：设置 GITHUB_TOKEN 环境变量可以避免 API 速率限制")
            sys.exit(0)  # 不中断构建流程
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
        response = requests.get(url, headers=get_headers(), params=params, timeout=30)
        if response.status_code == 200:
            commits = response.json()
            print(f"  📊 仓库 {repo_name}: 获取到 {len(commits)} 个commit")
            return commits
        else:
            print(f"  ⚠️  仓库 {repo_name}: 获取commit失败 (状态码: {response.status_code})")
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
                'message': commit['commit']['message'].split('\n')[0][:100],  # 第一行消息，限制长度
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
            commit_date = datetime.fromisoformat(commit_data['author']['date'].replace('Z', '+00:00'))
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
    processed_repos = 0

    # 计算时间范围（用于commit过滤）
    if include_commits:
        since_date = datetime.now() - timedelta(days=CONFIG['COMMIT_DAYS_RANGE'])
        since_iso = since_date.isoformat() + 'Z'

    # 单次遍历所有仓库，同时收集贡献者和commit数据
    for repo in repos:
        repo_name = repo['name']
        print(f"\n📦 处理仓库: {repo_name} ({processed_repos + 1}/{len(repos)})")

        try:
            # 1. 获取仓库贡献者信息
            print(f"  👥 获取贡献者...")
            contributors_url = f"{CONFIG['API_BASE']}/repos/{org_name}/{repo_name}/contributors"
            contributors_params = {'per_page': CONFIG['MAX_CONTRIBUTORS_PER_REPO']}

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
                            else:
                                commit_data['github_username'] = None

                            # 解析日期
                            commit_date = datetime.fromisoformat(commit_data['author']['date'].replace('Z', '+00:00'))
                            commit_data['date_parsed'] = commit_date
                            commit_data['date_str'] = commit_date.strftime('%Y-%m-%d')
                            commit_data['hour'] = commit_date.hour

                            all_commits.append(commit_data)

                        except Exception as e:
                            print(f"      ⚠️  处理commit数据时出错: {e}")
                            continue

            processed_repos += 1

            # 每处理10个仓库显示进度
            if processed_repos % 10 == 0:
                elapsed = time.time() - start_time
                print(f"  📈 进度: {processed_repos}/{len(repos)} 仓库 | 耗时: {elapsed:.1f}s | API调用: {api_calls['total']}")

        except Exception as e:
            print(f"  ❌ 处理仓库 {repo_name} 时出错: {e}")
            continue

    # 统计结果
    elapsed_time = time.time() - start_time
    print(f"\n📊 数据收集完成:")
    print(f"  - 处理仓库: {processed_repos}/{len(repos)}")
    print(f"  - 发现贡献者: {len(contributors_data)} 人")
    if include_commits:
        print(f"  - 收集commit: {len(all_commits)} 个")
    print(f"  - API调用统计: {api_calls}")
    print(f"  - 总耗时: {elapsed_time:.1f} 秒")

    return contributors_data, all_commits if include_commits else None, api_calls

def aggregate_commits_by_user(all_commits):
    """聚合commit数据按用户分组"""

    user_stats = defaultdict(lambda: {
        'total_commits': 0,
        'repos': set(),
        'daily_commits': defaultdict(int),
        'hourly_distribution': defaultdict(int),
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

        stats = user_stats[username]

        # 更新统计
        stats['total_commits'] += 1
        stats['repos'].add(commit['repo'])
        stats['daily_commits'][commit['date_str']] += 1
        stats['hourly_distribution'][commit['hour']] += 1

        # 保存commit消息（最多10个）
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

    # 转换为可序列化格式
    result = {}
    for username, stats in user_stats.items():
        if stats['total_commits'] >= 1:  # 至少1个commit
            result[username] = {
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
    """保存commit数据到文件"""
    try:
        # 确保目录存在
        CONFIG['COMMITS_FILE'].parent.mkdir(parents=True, exist_ok=True)

        # 保存到主数据文件
        with open(CONFIG['COMMITS_FILE'], 'w', encoding='utf-8') as f:
            json.dump(commits_data, f, ensure_ascii=False, indent=2)

        # 同时保存到public目录供前端使用
        public_file = Path(__file__).parent.parent / 'docs' / 'public' / 'data' / 'commits_weekly.json'
        public_file.parent.mkdir(parents=True, exist_ok=True)

        with open(public_file, 'w', encoding='utf-8') as f:
            json.dump(commits_data, f, ensure_ascii=False, indent=2)

        print(f"💾 Commit数据已保存:")
        print(f"  - 主文件: {CONFIG['COMMITS_FILE']}")
        print(f"  - 前端文件: {public_file}")
        print(f"  - 活跃用户: {commits_data.get('user_commits', {}) and len(commits_data['user_commits'])} 人")
        print(f"  - 总commit数: {commits_data.get('total_commits', 0)}")

        return True

    except Exception as e:
        print(f"❌ 保存commit数据失败: {e}")
        return False

def main_with_commits():
    """主函数 - 优化版本，包含commit数据收集"""
    print("🚀 开始执行优化的数据拉取脚本（包含commit数据）...")
    print(f"📁 输出文件: {CONFIG['OUTPUT_FILE']}")
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
        contributors_data, all_commits, api_stats = collect_unified_data(CONFIG['ORG_NAME'], include_commits=True)

        if not contributors_data:
            print("⚠️  未找到任何贡献者数据")
            if has_existing_data:
                print("🔄 使用现有数据继续构建...")
                sys.exit(0)
            else:
                print("💥 没有现有数据可用，构建失败")
                sys.exit(1)

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

                # 计算用户统计信息
                user_stats = calculate_user_stats(user_details, user_repos)
                print(f"  ✓ 统计信息: {user_stats['public_repos']} 仓库, {user_stats['total_stars']} Stars, {user_stats['followers']} 关注者")

                # 下载并缓存头像
                avatar_url = user_details.get('avatar_url') if user_details else contrib_info['user_info'].get('avatar_url')
                local_avatar = download_avatar(avatar_url, username)

                # 推断研究方向（基于仓库 topics、参与的仓库名称和用户简介）
                user_bio = user_details.get('bio') if user_details else ''
                domains = infer_domains_from_repos(contrib_info['repos'], user_bio, user_repos)
                print(f"  ✓ 推断研究方向: {', '.join(domains)}")

                processed_members.append({
                    'id': username,
                    'name': user_details.get('name') if user_details else username,
                    'github': contrib_info['user_info']['html_url'],
                    'domains': domains,
                    'repositories': contrib_info['repos'],  # 参与的组织仓库列表
                    'public_repos': user_stats['public_repos'],  # 个人公开仓库数
                    'total_stars': user_stats['total_stars'],  # 总 Stars 数
                    'followers': user_stats['followers'],  # 关注者数
                    'following': user_stats['following'],  # 关注数
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
            print(f"✅ 成功处理 {len(processed_members)} 个成员")

            # 处理并保存commit数据
            if all_commits:
                print(f"\n📊 处理 {len(all_commits)} 个commit数据...")
                user_commits = aggregate_commits_by_user(all_commits)

                commits_data = {
                    'update_time': datetime.now().isoformat(),
                    'days_range': CONFIG['COMMIT_DAYS_RANGE'],
                    'total_commits': len(all_commits),
                    'total_repos': len(set(commit['repo'] for commit in all_commits)),
                    'user_commits': user_commits,
                    'optimization_stats': {
                        'api_calls': api_stats,
                        'execution_time': f"{time.time() - overall_start_time:.1f}s",
                        'optimization_enabled': True
                    }
                }

                save_commits_data(commits_data)

            # 显示优化效果
            total_time = time.time() - overall_start_time
            print(f"\n🎉 优化版本执行完成!")
            print(f"📊 性能统计:")
            print(f"  - 总API调用: {api_stats['total']} 次")
            print(f"  - 仓库列表: {api_stats['repos_list']} 次")
            print(f"  - 贡献者API: {api_stats['contributors']} 次")
            print(f"  - Commit API: {api_stats['commits']} 次")
            print(f"  - 用户详情: {api_stats['users']} 次")
            print(f"  - 用户仓库: {api_stats['user_repos']} 次")
            print(f"  - 总执行时间: {total_time:.1f} 秒")

            # 估算优化效果
            estimated_old_calls = api_stats['repos_list'] * 2 + api_stats['contributors'] + api_stats['commits'] + api_stats['users'] + api_stats['user_repos']
            saved_calls = estimated_old_calls - api_stats['total']
            print(f"  - 预估节省API调用: {saved_calls} 次 ({saved_calls/estimated_old_calls*100:.1f}%)")

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

if __name__ == '__main__':
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == '--with-commits':
        main_with_commits()
    else:
        main()
