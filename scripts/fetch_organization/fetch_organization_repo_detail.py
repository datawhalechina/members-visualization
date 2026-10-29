import requests
from datetime import datetime, timedelta, timezone
from copy import deepcopy


def get_github_repo_by_organization_name(organization_name, token='', ignore_repo_name_list=[]):
    output = []
    need_next_page = True
    page = 1
    page_size = 100

    while need_next_page:
        try:
            print(f"fetch organization: {organization_name}, page: {page}")
            headers = {
                'accept': 'application/vnd.github+json',
            }

            if token:
                headers['authorization'] = f'Bearer {token}'

            url = f"https://api.github.com/orgs/{organization_name}/repos?per_page={page_size}&page={page}"
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()  # 抛出HTTP错误
            data = response.json()

            for item in data:
                if item['name'] in ignore_repo_name_list:
                    continue
                output.append({
                    'name': item['full_name'],
                    'star_count': item['stargazers_count']
                })

            need_next_page = len(data) == page_size
            page += 1

        except Exception as e:
            print(f"fetch organization error: {organization_name}, {e}")
            raise RuntimeError(f'Cannot fetch complete repository list: {organization_name}') from e

    # 按star_count降序排序
    return sorted(output, key=lambda x: x['star_count'], reverse=True)


def get_github_star_count(organization_name, repo, token='', monthly_stars=None,
                          monthly_total_stars=None, star_count=0, incremental=False):
    """Read anonymous weekly aggregates instead of the restricted stargazer list.

    https://docs.github.com/en/rest/activity/starring#get-repository-star-history
    Weeks arrive newest first; days run Sunday to Saturday. GitHub does not
    guarantee that its day boundaries align with UTC, so these aggregates
    should not be described as exact UTC-month event counts. Never manufacture
    zero-growth months after a failed or incomplete HTTP response.
    """
    headers = {'accept': 'application/vnd.github+json',
               'X-GitHub-Api-Version': '2026-03-10'}
    if token:
        headers['authorization'] = f'Bearer {token}'
    counts = {}
    oldest_day = None
    partial_history = False
    page_size = 30
    for page in range(1, 101):
        url = (f'https://api.github.com/repos/{organization_name}/{repo}'
               f'/stargazers/history?per_page={page_size}&page={page}')
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        weeks = response.json()
        if not isinstance(weeks, list):
            raise ValueError(f'Invalid star history response for {repo}')
        for week in weeks:
            days = week.get('days')
            if not isinstance(days, list) or len(days) != 7:
                raise ValueError(f'Invalid weekly star history for {repo}')
            start = datetime.fromtimestamp(week['week'], timezone.utc)
            for offset, count in enumerate(days):
                if not isinstance(count, int) or count < 0:
                    raise ValueError(f'Invalid daily star count for {repo}')
                day = start + timedelta(days=offset)
                oldest_day = min(day, oldest_day) if oldest_day else day
                month = f'{day.year}-{day.month}'
                counts[month] = counts.get(month, 0) + count
        if len(weeks) < page_size or 'next' not in response.links:
            break
        if incremental:
            # Keep the oldest (possibly partial) month from the complete cache.
            partial_history = True
            break
    else:
        raise RuntimeError(f'Incomplete star history for {repo}: pagination limit')

    if not counts and star_count:
        raise RuntimeError(f'Empty star history for {repo} with {star_count} stars')
    if partial_history and oldest_day and monthly_stars:
        boundary = (oldest_day.year, oldest_day.month)
        counts = {key: value for key, value in counts.items()
                  if tuple(map(int, key.split('-'))) > boundary}
        counts.update({key: value for key, value in monthly_stars.items()
                       if tuple(map(int, key.split('-'))) <= boundary})
    ordered = sorted(counts, key=lambda key: tuple(map(int, key.split('-'))))
    cumulative = 0
    totals = {}
    for month in ordered:
        cumulative += counts[month]
        totals[month] = cumulative
    return {
        'repo_name': repo,
        'monthly_stars': {month: counts[month] for month in ordered},
        'monthly_total_stars': totals,
        'star_count': star_count,
        'history_source': 'github_weekly_aggregates',
        'history_updated_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
    }


# 填充没有接收到数据的月份，输入一个类似于「2025-1」的日期字符串，如果在「2025-1」之前有没有数据的情况，那么该月的monthly_stars是0，monthly_total_stars是前一个月的monthly_total_stars
def fill_missing_months(input, key):
    end_date = datetime.strptime(key, "%Y-%m")
    star_date_list = list(input['monthly_stars'].keys())
    if len(star_date_list) == 0:
        return input
    start_date_str = star_date_list[0]
    start_date = datetime.strptime(start_date_str, "%Y-%m")
    start_year = start_date.year
    start_month = start_date.month
    end_year = end_date.year
    end_month = end_date.month
    previous_key = f"{start_year}-{start_month}"
    output = {
        "repo_name": input["repo_name"],
        "monthly_stars": {},
        "monthly_total_stars": {},
        "star_count": input["star_count"],
    }
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            if year == start_year and month < start_month:
                continue
            if year == end_year and month > end_month:
                break
            date_str = f"{year}-{month}"
            if date_str not in input['monthly_stars']:
                input['monthly_stars'][date_str] = 0
            if date_str not in input['monthly_total_stars']:
                input['monthly_total_stars'][date_str] = input['monthly_total_stars'][previous_key]
            output["monthly_stars"][date_str] = input["monthly_stars"][date_str]
            output["monthly_total_stars"][date_str] = input["monthly_total_stars"][date_str]
            previous_key = date_str

    return output


def fetch_organization_repo_detail(organization_name, token, ignore_repo_name_list, origin_repo_detail_list, month_key):
    repo_list = get_github_repo_by_organization_name(organization_name, token, ignore_repo_name_list)
    if not repo_list:
        raise RuntimeError('Refusing to replace organization data with an empty repository list')
    cached = {item['repo_name'].casefold(): item for item in origin_repo_detail_list}
    repo_detail_list = []
    failed = []
    for repo in repo_list:
        repo_name = repo['name'].split('/')[1]
        origin = cached.get(repo_name.casefold(), {})
        try:
            output = get_github_star_count(
                organization_name, repo_name, token,
                origin.get('monthly_stars'), origin.get('monthly_total_stars'),
                repo['star_count'],
                incremental=origin.get('history_source') == 'github_weekly_aggregates')
            repo_detail_list.append(fill_missing_months(output, month_key))
            # fill_missing_months only reshapes the monthly values.
            repo_detail_list[-1].update({key: output[key] for key in
                                        ('history_source', 'history_updated_at')})
        except (requests.RequestException, ValueError, KeyError, TypeError, RuntimeError) as error:
            print(f'WARNING: preserving cached star history for {repo_name}: {error}')
            failed.append(repo_name)
            if origin:
                repo_detail_list.append(deepcopy(origin))
    return {'repo_list': repo_list, 'repo_detail_list': repo_detail_list,
            'history_failures': failed}
