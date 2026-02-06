#!/usr/bin/env python3
"""
机器人账户过滤模块
提供统一的机器人账户检测逻辑，供 fetch_members 和 quarterly_contributors 共用
"""

import re

# 严格的机器人账户列表 - 只包含确认的官方机器人
BOT_USERNAMES = {
    # GitHub 官方机器人
    'actions-user',
    'github-actions',
    'github-actions[bot]',
    'web-flow',
    'github-merge-queue[bot]',

    # Dependabot 系列
    'dependabot',
    'dependabot[bot]',
    'dependabot-preview[bot]',

    # 常见的第三方官方机器人（带[bot]后缀的）
    'renovate[bot]',
    'greenkeeper[bot]',
    'codecov[bot]',
    'whitesource-bolt-for-github[bot]',
    'allcontributors[bot]',
    'imgbot[bot]',
    'stale[bot]',
    'pre-commit-ci[bot]',
    'mergify[bot]',
    'sonarcloud[bot]',
    'deepsource-autofix[bot]',
    'gitpod-io[bot]',
    'restyled-io[bot]',

    # 确认的第三方机器人（无[bot]后缀但确认是机器人）
    'snyk-bot',
    'semantic-release-bot',
    'pyup-bot',
    'pyup.io-bot',
    'houndci-bot',
    'coveralls',
    'travis-ci',
    'circleci',
    'claude',

    # 明确的无效账户
    'noreply',
    'no-reply',
    'invalid-email-address'
}

# 严格的机器人模式 - 只匹配明确的机器人格式
BOT_PATTERNS = [
    r'.*\[bot\]$',      # 以[bot]结尾的用户名（GitHub官方机器人格式）
    r'^\d+\+.*@users\.noreply\.github\.com$',  # GitHub noreply邮箱格式的用户名
]


def is_bot_account(username, user_details=None):
    """
    严格判断是否为机器人账户
    原则：宁可漏过少数机器人，也不要误判任何真实用户

    Args:
        username: GitHub 用户名
        user_details: 可选的用户详情字典（包含 type, company 等字段）

    Returns:
        bool: True 表示是机器人账户，False 表示是真实用户
    """
    if not username:
        return True  # 空用户名视为无效

    # 1. 精确匹配已知的机器人用户名（不区分大小写）
    if username.lower() in BOT_USERNAMES:
        return True

    # 2. 检查用户名是否匹配严格的机器人模式
    for pattern in BOT_PATTERNS:
        if re.match(pattern, username, re.IGNORECASE):
            return True

    # 3. 如果有用户详情，进行GitHub官方的机器人类型检查
    if user_details:
        # GitHub官方的账户类型检查（最可靠的方法）
        account_type = user_details.get('type', '').lower()
        if account_type == 'bot':
            return True

        # 检查公司字段是否为GitHub官方机器人服务
        company = (user_details.get('company') or '').lower()
        if company in ['@actions', '@github', '@dependabot', '@renovatebot']:
            return True

    # 4. 其他情况一律认为是真实用户
    return False
