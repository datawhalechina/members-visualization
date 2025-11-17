import math
import requests
from datetime import datetime


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
            response = requests.get(url, headers=headers)
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
            need_next_page = False

    # 按star_count降序排序
    return sorted(output, key=lambda x: x['star_count'], reverse=True)


def get_github_star_count(organization_name, repo, token='', monthly_stars={}, monthly_total_stars={}, star_count=0):
    output = {
        'repo_name': repo,
        'monthly_stars': monthly_stars,
        'monthly_total_stars': monthly_total_stars,
        'star_count': star_count
    }

    start_update_date = datetime.strptime("2010-1", "%Y-%m")

    # 在已有数据的基础上采集新数据，采集标准是去掉最后一个月的数据
    if len(list(output['monthly_total_stars'].keys())) > 1:
        need_delete_key = list(output['monthly_total_stars'].keys())[-1]
        output['star_count'] = list(output['monthly_total_stars'].values())[-2]
        start_update_date = datetime.strptime(need_delete_key, "%Y-%m")
        del output['monthly_total_stars'][need_delete_key]
        del output['monthly_stars'][need_delete_key]
    elif len(list(output['monthly_total_stars'].keys())) <= 1:
        output['star_count'] = 0
        output["monthly_stars"] = {}
        output["monthly_total_stars"] = {}

    need_next_page = True
    page_size = 100
    page = math.floor(output['star_count'] / page_size) + 1
    total_stars = output['star_count']

    while need_next_page:
        try:
            print(f"fetch repo: {repo}, page: {page}")
            headers = {
                'accept': 'application/vnd.github.v3.star+json',
            }

            if token:
                headers['authorization'] = f'token {token}'

            url = f"https://api.github.com/repos/{organization_name}/{repo}/stargazers?per_page={page_size}&page={page}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            for item in data:
                starred_at = item['starred_at']
                date = datetime.strptime(starred_at, '%Y-%m-%dT%H:%M:%SZ')
                if date < start_update_date:
                    continue
                total_stars += 1
                month_key = f"{date.year}-{date.month}"

                # 更新月度stars计数
                if month_key in output['monthly_stars']:
                    output['monthly_stars'][month_key] += 1
                else:
                    output['monthly_stars'][month_key] = 1

                # 更新月度总stars计数
                output['monthly_total_stars'][month_key] = total_stars

            need_next_page = len(data) == page_size
            page += 1

        except Exception as e:
            print(f"fetch repo error: {repo}, {e}")
            need_next_page = False

    output['star_count'] = total_stars
    return output


def fetch_organization_repo_detail(organization_name, token, ignore_repo_name_list, origin_repo_detail_list):
    repo_list = get_github_repo_by_organization_name(organization_name, token, ignore_repo_name_list)
    print(f"{organization_name} repo_list:", repo_list)

    repo_detail_list = []
    for repo in repo_list:
        # 从full_name中提取仓库名（假设格式为"org/repo"）
        repo_name = repo['name'].split('/')[1]
        if repo_name in ignore_repo_name_list:
            continue
        # 从origin_repo_detail_list中查找是否有匹配的仓库详情
        origin_monthly_stars = {}
        origin_monthly_total_stars = {}
        origin_star_count = 0
        for detail in origin_repo_detail_list:
            if detail['repo_name'] == repo_name:
                origin_monthly_stars = detail['monthly_stars']
                origin_monthly_total_stars = detail['monthly_total_stars']
                origin_star_count = detail['star_count']
                break
        output = get_github_star_count(organization_name, repo_name, token,
                                       origin_monthly_stars, origin_monthly_total_stars, origin_star_count)
        repo_detail_list.append(output)
        print(f"{organization_name} {repo_name} repo_detail:", output)

    # 按star_count降序排序
    repo_detail_list.sort(key=lambda x: x['star_count'], reverse=True)

    return {
        'repo_list': repo_list,
        'repo_detail_list': repo_detail_list
    }
