# 合并仓库详情
import json
from utils import get_object_by_month_key


def join_repo_detail_by_name(repo_list, repo_detail_dir, month_count=12, end_key=None):
    """Chart observed repository totals, not failed stargazer-history zeros.

    A dated repo_list is an actual API snapshot. Missing observations remain
    null; subtracting observations measures net growth, not star events.
    """
    months = get_object_by_month_key({}, month_count, end_key)
    snapshots = {}
    for month in months:
        snapshot_path = repo_detail_dir.parent / 'organization' / month / 'repo_list.json'
        if snapshot_path.exists():
            with open(snapshot_path, encoding='utf-8') as handle:
                snapshots[month] = {item['name'].casefold(): item['star_count']
                                    for item in json.load(handle)}
    result = []
    for item in repo_list:
        filename = item['name'].split('/', 1)[-1]
        result.append({
            'name': filename,
            'star_count': item['star_count'],
            'monthly_total_stars': {
                month: snapshots.get(month, {}).get(item['name'].casefold())
                for month in months
            },
            **({'starAdd': item['starAdd']} if 'starAdd' in item else {}),
        })
    return result


# 获取星星数超过1000的仓库
def get_repo_star_more_than_1000(repo_list_path, repo_detail_dir, end_key=None):
    with open(repo_list_path, 'r', encoding='utf-8') as f:
        repo_list = json.load(f)

    # 筛选星星数超过1000的仓库
    more_than_1000_repo_list = [
        item for item in repo_list if item['star_count'] >= 1000]
    result = join_repo_detail_by_name(more_than_1000_repo_list, repo_detail_dir, end_key=end_key)

    return result


# 获取新增星星数超过1000的仓库
def get_repo_add_star_more_than_1000(previous_repo_list_path, current_repo_list_path, repo_detail_dir, end_key=None):
    with open(previous_repo_list_path, 'r', encoding='utf-8') as f:
        previous_repo_list = json.load(f)

    with open(current_repo_list_path, 'r', encoding='utf-8') as f:
        current_repo_list = json.load(f)

    # 计算差异并筛选星星数超过1000的仓库
    diff_info = []
    for item in current_repo_list:
        if item['star_count'] >= 1000:
            previous_item = next(
                (prev for prev in previous_repo_list if prev['name'].casefold() == item['name'].casefold()), None)
            diff_info.append({
                **item,
                'starAdd': item['star_count'] - (previous_item['star_count'] if previous_item else 0),
            })

    # 按新增星星数排序
    diff_info.sort(key=lambda x: x['starAdd'], reverse=True)
    result = join_repo_detail_by_name(diff_info, repo_detail_dir, end_key=end_key)

    return result


# 获取新增星星数最多的5个仓库
def get_add_star_top5_repo(previous_repo_list_path, current_repo_list_path, repo_detail_dir, end_key=None):
    with open(previous_repo_list_path, 'r', encoding='utf-8') as f:
        previous_repo_list = json.load(f)

    with open(current_repo_list_path, 'r', encoding='utf-8') as f:
        current_repo_list = json.load(f)

    # 计算每个仓库的新增星星数
    diff_info = []
    for item in current_repo_list:
        previous_item = next(
            (prev for prev in previous_repo_list if prev['name'].casefold() == item['name'].casefold()), None)
        diff_info.append({
            **item,
            'starAdd': item['star_count'] - (previous_item['star_count'] if previous_item else 0),
        })

    # 按新增星星数排序并取前5个
    diff_info.sort(key=lambda x: x['starAdd'], reverse=True)
    top5_repo = diff_info[:5]
    result = join_repo_detail_by_name(top5_repo, repo_detail_dir, end_key=end_key)

    return result


# 获取新增星星数最多的3个新仓库
def get_add_star_top3_new_repo(previous_repo_list_path, current_repo_list_path, repo_detail_dir, end_key=None):
    with open(previous_repo_list_path, 'r', encoding='utf-8') as f:
        previous_repo_list = json.load(f)

    with open(current_repo_list_path, 'r', encoding='utf-8') as f:
        current_repo_list = json.load(f)

    # 筛选星星数大于10的旧仓库
    previous_repo_star_more_than_10 = [
        repo for repo in previous_repo_list if repo['star_count'] > 10]
    previous_repo_names = [repo['name'].casefold()
                           for repo in previous_repo_star_more_than_10]

    # 找出新仓库
    new_repo_list = [
        repo for repo in current_repo_list if repo['name'].casefold() not in previous_repo_names]

    previous_counts = {item['name'].casefold(): item['star_count'] for item in previous_repo_list}
    new_repo_list = [{**repo, 'starAdd': repo['star_count'] - previous_counts.get(repo['name'].casefold(), 0)} for repo in new_repo_list]

    # 按星星数排序
    new_repo_list.sort(key=lambda x: x['star_count'], reverse=True)

    # 获取仓库详情并取前3个
    detail_repo_list = join_repo_detail_by_name(new_repo_list[:3], repo_detail_dir, 4, end_key=end_key)
    top3_new_repo = detail_repo_list[:3]

    return top3_new_repo
