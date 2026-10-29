import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from fetch_organization_from_star_history import fetch_organization_from_star_history
from fetch_organization_repo_detail import fetch_organization_repo_detail
from analyze_organization import get_top10_knowledge_sharing_organization_info
from analyze_repo import get_add_star_top3_new_repo, get_add_star_top5_repo, get_repo_star_more_than_1000
from utils import ensure_dir_and_write_file, ensure_dir_and_write_files, read_file, resolve_repo_path


# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


CONFIG = {
    'GITHUB_TOKEN': os.getenv('GITHUB_TOKEN'),
    'DATAWHALE_ORGANIZATION_NAME': "datawhalechina",
    'TOP_10_KNOWLEDGE_SHARING_ORGANIZATION': [
        "freeCodeCamp",
        "TheAlgorithms",
        "EbookFoundation",
        "ossu",
        "doocs",
        "h5bp",
        "datawhalechina",
        "dair-ai",
        "jobbole",
        "papers-we-love",
    ],
    'DATA_DIR': Path(__file__).parent.parent.parent / 'docs' / 'public' / 'data' / 'datawhalechina',
    'REPO_DATA_DIR': Path(__file__).parent.parent.parent / 'docs' / 'public' / 'data' / 'datawhalechina' / 'repo',
    'ORGANIZATION_DATA_DIR': Path(__file__).parent.parent.parent / 'docs' / 'public' / 'data' / 'datawhalechina' / 'organization',
    'TOP_10_KNOWLEDGE_SHARING_ORGANIZATION_FILE_NAME': "top_10_knowledge_sharing_organization.json",
    'REPO_DATA_LIST_FILE_NAME': "repo_list.json",
    'ANALYZED_DATASOURCE_FILE_NAME': Path(__file__).parent.parent.parent / 'docs' / 'public' / 'data' / 'datawhalechina' / 'organization_datasource.json',
    'FETCH_TIME_KEY_FILE_NAME': Path(__file__).parent.parent.parent / 'docs' / 'public' / 'data' / 'datawhalechina' / 'fetch_time_key.json',
}


def fetch_organization_data(key):
    # 确保数据目录存在
    CONFIG['DATA_DIR'].mkdir(parents=True, exist_ok=True)
    CONFIG['REPO_DATA_DIR'].mkdir(parents=True, exist_ok=True)
    CONFIG['ORGANIZATION_DATA_DIR'].mkdir(parents=True, exist_ok=True)

    # 加载环境变量
    github_token = os.getenv('GITHUB_TOKEN')

    # 0. 从repo_list.json中加载已有的仓库详情数据
    origin_repo_detail_list = []
    repo_data_list_file_path = CONFIG['ORGANIZATION_DATA_DIR'] / \
        CONFIG['REPO_DATA_LIST_FILE_NAME']
    repo_data_list_file_path_with_key = CONFIG['ORGANIZATION_DATA_DIR'] / \
        key / CONFIG['REPO_DATA_LIST_FILE_NAME']
    origin_repo_data_list = json.loads(read_file(repo_data_list_file_path))
    for repo_detail in origin_repo_data_list:
        repo_name = repo_detail['name'].split('/')[1]
        repo_detail_path = resolve_repo_path(CONFIG['REPO_DATA_DIR'], repo_name)
        repo_detail_data = read_file(repo_detail_path)
        if repo_detail_data is not None:
            origin_repo_detail_list.append(json.loads(repo_detail_data))

    # 1. 从starHistory网站中获取开源组织列表
    star_history_res = fetch_organization_from_star_history(
        10, CONFIG['TOP_10_KNOWLEDGE_SHARING_ORGANIZATION']
    )
    top_10_knowledge_sharing_organization_path = CONFIG['ORGANIZATION_DATA_DIR'] / \
        CONFIG['TOP_10_KNOWLEDGE_SHARING_ORGANIZATION_FILE_NAME']
    top_10_knowledge_sharing_organization_path_with_key = CONFIG['ORGANIZATION_DATA_DIR'] / \
        key / CONFIG['TOP_10_KNOWLEDGE_SHARING_ORGANIZATION_FILE_NAME']
    if not star_history_res['top_10_knowledge_sharing_organization']:
        raise RuntimeError('Organization ranking fetch returned no usable data')
    ensure_dir_and_write_files([top_10_knowledge_sharing_organization_path, top_10_knowledge_sharing_organization_path_with_key], json.dumps(
        star_history_res["top_10_knowledge_sharing_organization"], indent=2, ensure_ascii=False))

    # 2. 获取Datawhale的仓库列表和仓库详情，并进行写入
    repo_detail_res = fetch_organization_repo_detail(
        CONFIG['DATAWHALE_ORGANIZATION_NAME'], github_token, ['.github'], origin_repo_detail_list, key)
    ensure_dir_and_write_files([repo_data_list_file_path, repo_data_list_file_path_with_key], json.dumps(
        repo_detail_res["repo_list"], indent=2, ensure_ascii=False))

    if repo_detail_res.get('history_failures'):
        print('::warning::Star history refresh failed; cached histories preserved: '
              + ', '.join(repo_detail_res['history_failures']))

    # 3.写入每个仓库的详情
    for repo_detail in repo_detail_res["repo_detail_list"]:
        repo_detail_path = resolve_repo_path(CONFIG['REPO_DATA_DIR'], repo_detail['repo_name'])
        ensure_dir_and_write_file(repo_detail_path, json.dumps(
            repo_detail, indent=2, ensure_ascii=False))


def analyze_organization_data(previous_key, current_key):
    # 合并仓库详情
    previous_top_10_organization_path = CONFIG['ORGANIZATION_DATA_DIR'] / \
        previous_key / \
        CONFIG['TOP_10_KNOWLEDGE_SHARING_ORGANIZATION_FILE_NAME']
    current_top_10_organization_path = CONFIG['ORGANIZATION_DATA_DIR'] / \
        current_key / CONFIG['TOP_10_KNOWLEDGE_SHARING_ORGANIZATION_FILE_NAME']
    previous_repo_list_path = CONFIG['ORGANIZATION_DATA_DIR'] / \
        previous_key / CONFIG['REPO_DATA_LIST_FILE_NAME']
    current_repo_list_path = CONFIG['ORGANIZATION_DATA_DIR'] / \
        current_key / CONFIG['REPO_DATA_LIST_FILE_NAME']

    # 获取所有需要的数据
    top10_knowledge_sharing_organization_info = get_top10_knowledge_sharing_organization_info(
        previous_top_10_organization_path, current_top_10_organization_path)
    project_info = get_repo_star_more_than_1000(
        current_repo_list_path, CONFIG['REPO_DATA_DIR'], end_key=current_key)
    project_add_top5_info = get_add_star_top5_repo(
        previous_repo_list_path, current_repo_list_path, CONFIG['REPO_DATA_DIR'], end_key=current_key)
    new_project_add_top3_info = get_add_star_top3_new_repo(
        previous_repo_list_path, current_repo_list_path, CONFIG['REPO_DATA_DIR'], end_key=current_key)

    datasource = {
        'meta': {'period_start': previous_key, 'period_end': current_key,
                 'series_source': 'monthly_repository_snapshots'},
        'projectInfo': project_info,
        'projectAddTop5Info': project_add_top5_info,
        'newProjectAddTop3Info': new_project_add_top3_info,
        'top10KnowledgeSharingOrganizationInfo': top10_knowledge_sharing_organization_info
    }
    # 写入合并后的数据源文件
    ensure_dir_and_write_file(
        CONFIG['ANALYZED_DATASOURCE_FILE_NAME'],
        json.dumps(datasource, indent=2, ensure_ascii=False)
    )


def select_period(keys):
    keys = sorted(set(keys), key=lambda key: tuple(map(int, key.split('-'))))
    if not keys:
        raise ValueError('No organization snapshots available')
    return keys[max(0, len(keys) - 4)], keys[-1]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--analyze-only', action='store_true',
                        help='Rebuild the derived charts from existing monthly snapshots; no network')
    args = parser.parse_args()
    key_list = json.loads(read_file(CONFIG['FETCH_TIME_KEY_FILE_NAME']) or '[]')
    if not args.analyze_only:
        now = datetime.now()
        current_key = f'{now.year}-{now.month}'
        fetch_organization_data(current_key)
        if current_key not in key_list:
            key_list.append(current_key)
        key_list.sort(key=lambda key: tuple(map(int, key.split('-'))))
        # Publish a period only after its source snapshots were collected.
        ensure_dir_and_write_file(CONFIG['FETCH_TIME_KEY_FILE_NAME'],
                                  json.dumps(key_list, indent=2, ensure_ascii=False))
    previous_key, current_key = select_period(key_list)
    analyze_organization_data(previous_key, current_key)
