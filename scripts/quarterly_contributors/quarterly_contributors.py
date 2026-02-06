#!/usr/bin/env python3
"""
季度贡献者统计脚本
功能：统计指定季度内所有成员的有效贡献，并按等级分类
- 优秀贡献者：有效commit >= 10次
- 卓越贡献者：有效commit >= 50次
- 有效commit定义：至少包含一个文件新增行数 >= 10行

优化特性：
1. 本地缓存机制 - 避免重复API调用
2. 增量更新 - 只处理新的commit
3. 进度显示 - 实时显示处理进度
4. JSON输出 - 生成前端可用的数据格式
5. 机器人过滤 - 使用共享的过滤规则
"""

import os
import json
import time
import sys
import re
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import requests

# 添加父目录到路径，以便导入共享模块
sys.path.insert(0, str(Path(__file__).parent.parent))
from bot_filter import is_bot_account

# 配置
CONFIG = {
    'GITHUB_TOKEN': os.getenv('GITHUB_TOKEN') or os.getenv('GITHUB_KEY'),
    'ORG_NAME': 'datawhalechina',
    'API_BASE': 'https://api.github.com',
    # 缓存目录 (相对于 scripts/quarterly_contributors/)
    'CACHE_DIR': Path(__file__).parent.parent.parent / 'cache' / 'quarterly_stats',
    # 输出目录
    'OUTPUT_DIR': Path(__file__).parent.parent.parent / 'docs' / 'public' / 'data' / 'datawhalechina',
    # 有效commit的阈值（单文件新增行数）
    'VALID_COMMIT_THRESHOLD': 10,
    # 贡献者等级阈值
    'EXCELLENT_THRESHOLD': 10,  # 优秀贡献者
    'OUTSTANDING_THRESHOLD': 50,  # 卓越贡献者
    # API调用控制
    'MAX_RETRIES': 3,
    'RETRY_DELAY': 2,
    'REQUEST_DELAY': 0.1,  # 请求间隔（秒）
}


def get_headers():
    """获取API请求头"""
    headers = {
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'User-Agent': 'quarterly-contributors-bot'
    }
    if CONFIG['GITHUB_TOKEN']:
        headers['Authorization'] = f"Bearer {CONFIG['GITHUB_TOKEN']}"
    return headers


def extract_username_from_email(email):
    """
    尝试从邮箱中提取GitHub用户名
    支持的格式：
    - 12345678+username@users.noreply.github.com
    - username@users.noreply.github.com
    """
    if not email:
        return None

    # GitHub noreply 邮箱格式
    noreply_pattern = r'^(?:\d+\+)?([^@]+)@users\.noreply\.github\.com$'
    match = re.match(noreply_pattern, email, re.IGNORECASE)
    if match:
        return match.group(1)

    return None


def search_user_by_email(email):
    """
    通过邮箱搜索GitHub用户
    注意：这会消耗额外的API调用
    """
    if not email or '@' not in email:
        return None

    # 跳过明显无效的邮箱
    if 'noreply' in email.lower() or 'localhost' in email.lower():
        return None

    url = f"{CONFIG['API_BASE']}/search/users?q={email}+in:email"
    try:
        data = fetch_api(url)
        if data and data.get('total_count', 0) == 1:
            # 只有精确匹配一个用户时才返回
            return data['items'][0]['login']
    except Exception:
        pass

    return None


def check_rate_limit():
    """检查API速率限制"""
    url = f"{CONFIG['API_BASE']}/rate_limit"
    try:
        response = requests.get(url, headers=get_headers(), timeout=10)
        if response.status_code == 200:
            data = response.json()
            core = data['resources']['core']
            remaining = core['remaining']
            limit = core['limit']
            reset_time = datetime.fromtimestamp(core['reset'])

            print(f"📊 API速率限制: {remaining}/{limit} 剩余")
            print(f"⏰ 重置时间: {reset_time.strftime('%Y-%m-%d %H:%M:%S')}")

            if remaining < 100:
                print(f"⚠️  警告: API调用次数不足100次，建议等待重置")
                return False
            return True
    except Exception as e:
        print(f"❌ 检查速率限制失败: {e}")
        return True  # 继续执行


def fetch_api(url, retries=None):
    """发送API请求（带重试和速率限制处理）"""
    if retries is None:
        retries = CONFIG['MAX_RETRIES']

    for attempt in range(retries):
        try:
            time.sleep(CONFIG['REQUEST_DELAY'])
            response = requests.get(url, headers=get_headers(), timeout=30)

            # 检查速率限制
            remaining = response.headers.get('X-RateLimit-Remaining')
            if remaining and int(remaining) < 10:
                reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                wait_time = max(reset_time - int(time.time()), 0) + 1
                print(f"⏳ API速率限制接近，等待 {wait_time} 秒...")
                time.sleep(wait_time)
                continue

            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            if response.status_code == 403:
                print(f"❌ API速率限制或权限问题")
                return None
            elif response.status_code == 404:
                return None
            print(f"⚠️  HTTP错误 {response.status_code}: {e}")

        except Exception as e:
            print(f"⚠️  请求失败 (尝试 {attempt + 1}/{retries}): {e}")

        if attempt < retries - 1:
            wait_time = CONFIG['RETRY_DELAY'] * (2 ** attempt)
            print(f"⏳ 等待 {wait_time} 秒后重试...")
            time.sleep(wait_time)

    return None


def get_quarter_date_range(year, quarter):
    """
    获取指定季度的日期范围

    Args:
        year: 年份
        quarter: 季度 (1-4)

    Returns:
        (start_date, end_date) ISO格式字符串
    """
    quarter_months = {
        1: (1, 3),
        2: (4, 6),
        3: (7, 9),
        4: (10, 12)
    }

    start_month, end_month = quarter_months[quarter]
    start_date = datetime(year, start_month, 1)

    # 计算季度结束日期（下个季度第一天）
    if quarter == 4:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, end_month + 1, 1)

    return (
        start_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
        end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    )


class CacheManager:
    """缓存管理器 - 管理commit详情的本地缓存"""

    def __init__(self, cache_dir):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / 'commit_details.json'
        self.cache = self._load_cache()

    def _load_cache(self):
        """加载缓存"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  加载缓存失败: {e}")
                return {}
        return {}

    def get(self, repo, sha):
        """获取缓存的commit详情"""
        key = f"{repo}:{sha}"
        return self.cache.get(key)

    def set(self, repo, sha, data):
        """设置缓存"""
        key = f"{repo}:{sha}"
        self.cache[key] = data

    def save(self):
        """保存缓存到文件"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
            print(f"💾 缓存已保存: {len(self.cache)} 条记录")
        except Exception as e:
            print(f"❌ 保存缓存失败: {e}")

    def size(self):
        """返回缓存大小"""
        return len(self.cache)

    def clear(self):
        """清理缓存目录"""
        try:
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
                print(f"🗑️  缓存目录已清理: {self.cache_dir}")
        except Exception as e:
            print(f"⚠️  清理缓存失败: {e}")


def get_org_repos(org_name):
    """获取组织的所有公开仓库"""
    print(f"\n📁 获取组织 {org_name} 的仓库列表...")
    all_repos = []
    page = 1

    while True:
        url = f"{CONFIG['API_BASE']}/orgs/{org_name}/repos?per_page=100&page={page}&type=public&sort=updated"
        repos = fetch_api(url)

        if not repos or len(repos) == 0:
            break

        # 过滤fork仓库
        original_repos = [repo for repo in repos if not repo.get('fork', False)]
        all_repos.extend(original_repos)

        print(f"  ✓ 第{page}页: {len(original_repos)} 个原创仓库")

        if len(repos) < 100:
            break

        page += 1

    print(f"✅ 总共找到 {len(all_repos)} 个仓库")
    return all_repos


def get_commits_in_range(org_name, repo_name, since, until):
    """获取指定时间范围内的commits"""
    url = f"{CONFIG['API_BASE']}/repos/{org_name}/{repo_name}/commits"
    params = {
        'since': since,
        'until': until,
        'per_page': 100
    }

    all_commits = []
    page = 1

    while True:
        page_url = f"{url}?since={params['since']}&until={params['until']}&per_page={params['per_page']}&page={page}"
        commits = fetch_api(page_url)

        if not commits or len(commits) == 0:
            break

        all_commits.extend(commits)

        if len(commits) < 100:
            break

        page += 1

    return all_commits


def get_commit_details(org_name, repo_name, sha, cache_manager):
    """获取commit的详细信息（带缓存）"""
    # 先检查缓存
    cached = cache_manager.get(repo_name, sha)
    if cached:
        return cached

    # 从API获取
    url = f"{CONFIG['API_BASE']}/repos/{org_name}/{repo_name}/commits/{sha}"
    data = fetch_api(url)

    if data:
        # 提取需要的信息
        details = {
            'sha': sha[:8],
            'author': data['commit']['author']['name'],
            'author_email': data['commit']['author'].get('email', ''),
            'author_login': data['author']['login'] if data.get('author') else None,
            'date': data['commit']['author']['date'],
            'message': data['commit']['message'].split('\n')[0][:100],
            'files': []
        }

        # 提取文件变更信息
        if 'files' in data:
            for file in data['files']:
                details['files'].append({
                    'filename': file['filename'],
                    'additions': file.get('additions', 0),
                    'deletions': file.get('deletions', 0),
                    'changes': file.get('changes', 0)
                })

        # 缓存结果
        cache_manager.set(repo_name, sha, details)
        return details

    return None


def is_valid_commit(commit_details):
    """
    判断是否为有效commit
    有效commit定义：至少有一个文件的新增行数 >= 阈值
    """
    if not commit_details or 'files' not in commit_details:
        return False

    threshold = CONFIG['VALID_COMMIT_THRESHOLD']
    for file in commit_details['files']:
        if file.get('additions', 0) >= threshold:
            return True

    return False


def process_repository(org_name, repo_name, since, until, cache_manager, stats):
    """
    处理单个仓库的统计

    Args:
        org_name: 组织名称
        repo_name: 仓库名称
        since: 开始时间
        until: 结束时间
        cache_manager: 缓存管理器
        stats: 统计数据字典（会被修改）

    Returns:
        处理的commit数量
    """
    print(f"\n  📦 处理仓库: {repo_name}")

    # 获取时间范围内的commits
    commits = get_commits_in_range(org_name, repo_name, since, until)
    if not commits:
        print(f"    ℹ️  无commit")
        return 0

    print(f"    ✓ 找到 {len(commits)} 个commit")

    valid_count = 0
    processed_count = 0

    for i, commit in enumerate(commits):
        sha = commit['sha']
        # 从列表API中提取author login（列表API有时能关联到用户，详情API却不行）
        list_author_login = commit.get('author', {}).get('login') if commit.get('author') else None

        # 获取commit详情
        details = get_commit_details(org_name, repo_name, sha, cache_manager)
        if not details:
            continue

        processed_count += 1

        # 判断是否为有效commit
        if is_valid_commit(details):
            valid_count += 1

            # 获取作者信息 - 多种方式尝试解析GitHub用户名
            author_login = details.get('author_login')
            is_verified = True

            # 方式1: 使用列表API中的author login
            if not author_login and list_author_login:
                author_login = list_author_login

            # 方式2: 从邮箱中提取用户名（GitHub noreply格式）
            if not author_login:
                author_email = details.get('author_email', '')
                author_login = extract_username_from_email(author_email)
                if author_login:
                    print(f"    📧 从邮箱解析用户名: {author_login}")

            # 方式3: 通过邮箱搜索GitHub用户（消耗额外API）
            if not author_login:
                author_email = details.get('author_email', '')
                if author_email and '@' in author_email:
                    author_login = search_user_by_email(author_email)
                    if author_login:
                        print(f"    🔍 通过邮箱搜索到用户: {author_login}")

            # 方式4: 无法解析，使用commit作者名，标记为未验证
            if not author_login:
                author_login = details.get('author', 'Unknown')
                is_verified = False
                print(f"    ⚠️  未能解析GitHub用户名，使用作者名: {author_login}")

            # 检查是否为机器人账户（使用共享的过滤规则）
            if is_bot_account(author_login):
                print(f"    🤖 跳过机器人账户: {author_login}")
                continue

            # 记录到统计数据
            if author_login not in stats:
                stats[author_login] = {
                    'username': author_login,
                    'verified': is_verified,
                    'valid_commits': 0,
                    'total_commits': 0,
                    'repos': set(),
                    'commits_detail': []
                }
            # 如果之前是未验证的，现在有验证的commit，更新为已验证
            elif is_verified and not stats[author_login].get('verified'):
                stats[author_login]['verified'] = True

            stats[author_login]['valid_commits'] += 1
            stats[author_login]['total_commits'] += 1
            stats[author_login]['repos'].add(repo_name)
            stats[author_login]['commits_detail'].append({
                'repo': repo_name,
                'sha': details['sha'],
                'message': details['message'],
                'date': details['date'],
                'files_count': len(details['files']),
                'total_additions': sum(f['additions'] for f in details['files'])
            })

        # 显示进度
        if (i + 1) % 50 == 0:
            print(f"    📊 进度: {i + 1}/{len(commits)} commits")

    print(f"    ✅ 有效commit: {valid_count}/{processed_count}")
    return processed_count


def classify_contributors(stats):
    """
    对贡献者进行分级

    Returns:
        {
            'outstanding': [...],  # 卓越贡献者 (>=50)
            'excellent': [...],    # 优秀贡献者 (>=10)
            'active': [...]        # 活跃贡献者 (<10)
        }
    """
    outstanding = []
    excellent = []
    active = []

    for username, data in stats.items():
        valid_commits = data['valid_commits']

        contributor = {
            'username': username,
            'verified': data.get('verified', True),
            'valid_commits': valid_commits,
            'total_commits': data['total_commits'],
            'repos_count': len(data['repos']),
            'repos': sorted(list(data['repos'])),
            'recent_commits': sorted(
                data['commits_detail'],
                key=lambda x: x['date'],
                reverse=True
            )[:10]  # 只保留最近10个commit
        }

        if valid_commits >= CONFIG['OUTSTANDING_THRESHOLD']:
            outstanding.append(contributor)
        elif valid_commits >= CONFIG['EXCELLENT_THRESHOLD']:
            excellent.append(contributor)
        else:
            active.append(contributor)

    # 按有效commit数量降序排序
    outstanding.sort(key=lambda x: x['valid_commits'], reverse=True)
    excellent.sort(key=lambda x: x['valid_commits'], reverse=True)
    active.sort(key=lambda x: x['valid_commits'], reverse=True)

    return {
        'outstanding': outstanding,
        'excellent': excellent,
        'active': active
    }


def save_results(year, quarter, classified, stats, output_dir):
    """保存统计结果到JSON文件"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 生成文件名
    filename = f"quarterly_contributors_{year}_Q{quarter}.json"
    output_file = output_dir / filename

    # 准备输出数据
    result = {
        'meta': {
            'year': year,
            'quarter': quarter,
            'generated_at': datetime.now().isoformat(),
            'total_contributors': len(stats),
            'outstanding_count': len(classified['outstanding']),
            'excellent_count': len(classified['excellent']),
            'active_count': len(classified['active']),
            'thresholds': {
                'outstanding': CONFIG['OUTSTANDING_THRESHOLD'],
                'excellent': CONFIG['EXCELLENT_THRESHOLD'],
                'valid_commit_threshold': CONFIG['VALID_COMMIT_THRESHOLD']
            }
        },
        'contributors': classified
    }

    # 保存到文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n💾 结果已保存到: {output_file}")
    return output_file


def print_summary(classified):
    """打印统计摘要"""
    print("\n" + "="*60)
    print("📊 统计摘要")
    print("="*60)

    print(f"\n🏆 卓越贡献者 (>={CONFIG['OUTSTANDING_THRESHOLD']}次有效commit): {len(classified['outstanding'])}人")
    for contributor in classified['outstanding'][:5]:
        print(f"  - {contributor['username']}: {contributor['valid_commits']}次 ({contributor['repos_count']}个仓库)")

    print(f"\n⭐ 优秀贡献者 (>={CONFIG['EXCELLENT_THRESHOLD']}次有效commit): {len(classified['excellent'])}人")
    for contributor in classified['excellent'][:5]:
        print(f"  - {contributor['username']}: {contributor['valid_commits']}次 ({contributor['repos_count']}个仓库)")

    print(f"\n👥 活跃贡献者 (<{CONFIG['EXCELLENT_THRESHOLD']}次有效commit): {len(classified['active'])}人")

    print("\n" + "="*60)


def cleanup_cache():
    """清理整个缓存目录"""
    cache_root = Path(__file__).parent.parent.parent / 'cache'
    try:
        if cache_root.exists():
            shutil.rmtree(cache_root)
            print(f"🗑️  缓存目录已清理: {cache_root}")
            return True
    except Exception as e:
        print(f"⚠️  清理缓存失败: {e}")
    return False


def main(year, quarter):
    """
    主函数：统计指定季度的贡献者

    Args:
        year: 年份
        quarter: 季度 (1-4)
    """
    print("="*60)
    print(f"🚀 开始统计 {year}年 Q{quarter} 季度贡献者")
    print("="*60)

    # 检查API速率限制
    if not check_rate_limit():
        print("⚠️  API调用次数不足，建议稍后再试")
        return

    # 初始化缓存管理器
    cache_manager = CacheManager(CONFIG['CACHE_DIR'])
    print(f"📦 缓存已加载: {cache_manager.size()} 条记录")

    # 获取季度日期范围
    since, until = get_quarter_date_range(year, quarter)
    print(f"📅 统计时间范围: {since} 至 {until}")

    # 获取组织仓库
    repos = get_org_repos(CONFIG['ORG_NAME'])
    if not repos:
        print("❌ 未找到任何仓库")
        return

    # 统计数据
    stats = {}
    total_commits = 0
    start_time = time.time()

    # 处理每个仓库
    for i, repo in enumerate(repos):
        repo_name = repo['name']
        print(f"\n[{i+1}/{len(repos)}] 处理仓库: {repo_name}")

        try:
            commit_count = process_repository(
                CONFIG['ORG_NAME'],
                repo_name,
                since,
                until,
                cache_manager,
                stats
            )
            total_commits += commit_count

            # 每处理10个仓库保存一次缓存
            if (i + 1) % 10 == 0:
                cache_manager.save()

        except Exception as e:
            print(f"  ❌ 处理失败: {e}")
            continue

    # 保存最终缓存
    cache_manager.save()

    # 对贡献者进行分级
    print("\n📊 正在分级贡献者...")
    classified = classify_contributors(stats)

    # 打印摘要
    print_summary(classified)

    # 保存结果
    output_file = save_results(
        year,
        quarter,
        classified,
        stats,
        CONFIG['OUTPUT_DIR']
    )

    # 显示执行统计
    elapsed_time = time.time() - start_time
    print(f"\n⏱️  总耗时: {elapsed_time:.1f} 秒")
    print(f"📊 处理仓库: {len(repos)} 个")
    print(f"📊 总commit数: {total_commits}")
    print(f"📊 总贡献者: {len(stats)} 人")

    # 清理缓存目录
    print("\n🧹 清理缓存...")
    cleanup_cache()

    print("\n✅ 统计完成！")
    return output_file


def get_previous_quarter():
    """
    获取上一个季度的年份和季度
    例如：当前是2026年2月(Q1)，返回 (2025, 4)
    """
    now = datetime.now()
    current_quarter = (now.month - 1) // 3 + 1

    if current_quarter == 1:
        # 当前是Q1，上季度是去年Q4
        return now.year - 1, 4
    else:
        # 其他情况，上季度是今年的前一个季度
        return now.year, current_quarter - 1


def get_current_quarter():
    """获取当前季度的年份和季度"""
    now = datetime.now()
    current_quarter = (now.month - 1) // 3 + 1
    return now.year, current_quarter


if __name__ == '__main__':
    # 解析命令行参数
    if len(sys.argv) == 1:
        # 无参数时显示帮助
        print("用法:")
        print("  python quarterly_contributors.py --last      # 统计上季度")
        print("  python quarterly_contributors.py --current   # 统计当前季度")
        print("  python quarterly_contributors.py <年份> <季度>  # 统计指定季度")
        print("")
        print("示例:")
        print("  python quarterly_contributors.py --last")
        print("  python quarterly_contributors.py 2025 4")
        sys.exit(0)

    try:
        if sys.argv[1] == '--last':
            # 统计上季度
            year, quarter = get_previous_quarter()
            print(f"📅 自动选择上季度: {year}年 Q{quarter}")
            main(year, quarter)
        elif sys.argv[1] == '--current':
            # 统计当前季度
            year, quarter = get_current_quarter()
            print(f"📅 自动选择当前季度: {year}年 Q{quarter}")
            main(year, quarter)
        elif len(sys.argv) >= 3:
            # 指定年份和季度
            year = int(sys.argv[1])
            quarter = int(sys.argv[2])

            if quarter not in [1, 2, 3, 4]:
                print("❌ 季度必须是 1-4 之间的数字")
                sys.exit(1)

            main(year, quarter)
        else:
            print("❌ 参数不足，请使用 --last 或指定年份和季度")
            sys.exit(1)

    except ValueError:
        print("❌ 参数格式错误，年份和季度必须是数字")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断执行")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
