import json
import os
from datetime import datetime
from pathlib import Path
from fetch_organization_from_star_history import fetch_organization_from_star_history
from fetch_organization_repo_detail import fetch_organization_repo_detail
from analyze_organization import get_top10_knowledge_sharing_organization_info
from analyze_repo import get_add_star_top3_new_repo, get_add_star_top5_repo, get_repo_add_star_more_than_1000, get_repo_star_more_than_1000
from utils import ensure_dir_and_write_file


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
    'ALL_ORGANIZATION_FILE_NAME': "all_organization.json",
    'TOP_10_KNOWLEDGE_SHARING_ORGANIZATION_FILE_NAME': "top_10_knowledge_sharing_organization.json",
    'REPO_DATA_LIST_FILE_NAME': "repo_list.json",
    'ANALYZED_DATASOURCE_FILE_NAME': Path(__file__).parent.parent.parent / 'docs' / 'public' / 'data' / 'datawhalechina' / 'organization_datasource.json',
}


def fetch_organization_data(key):
    # 确保数据目录存在
    CONFIG['DATA_DIR'].mkdir(parents=True, exist_ok=True)
    CONFIG['REPO_DATA_DIR'].mkdir(parents=True, exist_ok=True)
    CONFIG['ORGANIZATION_DATA_DIR'].mkdir(parents=True, exist_ok=True)

    # 加载环境变量
    github_token = os.getenv('GITHUB_TOKEN')

    # 1. 从starHistory网站中获取开源组织列表
    star_history_res = fetch_organization_from_star_history(
        10, CONFIG['TOP_10_KNOWLEDGE_SHARING_ORGANIZATION']
    )
    all_organization_path = CONFIG['ORGANIZATION_DATA_DIR'] / \
        key / CONFIG['ALL_ORGANIZATION_FILE_NAME']
    top_10_knowledge_sharing_organization_path = CONFIG['ORGANIZATION_DATA_DIR'] / \
        key / CONFIG['TOP_10_KNOWLEDGE_SHARING_ORGANIZATION_FILE_NAME']
    ensure_dir_and_write_file(all_organization_path, json.dumps(
        star_history_res["organization_list"], indent=2, ensure_ascii=False))
    ensure_dir_and_write_file(top_10_knowledge_sharing_organization_path, json.dumps(
        star_history_res["top_10_knowledge_sharing_organization"], indent=2, ensure_ascii=False))

    # 2. 获取Datawhale的仓库列表和仓库详情
    repo_detail_res = fetch_organization_repo_detail(
        CONFIG['DATAWHALE_ORGANIZATION_NAME'], github_token)
    repo_data_list_file_path = CONFIG['ORGANIZATION_DATA_DIR'] / \
        key / CONFIG['REPO_DATA_LIST_FILE_NAME']
    ensure_dir_and_write_file(repo_data_list_file_path, json.dumps(
        repo_detail_res["repo_list"], indent=2, ensure_ascii=False))

    # 写入每个仓库的详情
    for repo_detail in repo_detail_res["repo_detail_list"]:
        repo_detail_path = CONFIG['REPO_DATA_DIR'] / \
            f"{repo_detail['repo_name']}.json"
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
        current_repo_list_path, CONFIG['REPO_DATA_DIR'])
    project_add_info = get_repo_add_star_more_than_1000(
        previous_repo_list_path, current_repo_list_path, CONFIG['REPO_DATA_DIR'])
    project_add_top5_info = get_add_star_top5_repo(
        previous_repo_list_path, current_repo_list_path, CONFIG['REPO_DATA_DIR'])
    new_project_add_top3_info = get_add_star_top3_new_repo(
        previous_repo_list_path, current_repo_list_path, CONFIG['REPO_DATA_DIR'])

    datasource = {
        'projectInfo': project_info,
        'projectAddInfo': project_add_info,
        'projectAddTop5Info': project_add_top5_info,
        'newProjectAddTop3Info': new_project_add_top3_info,
        'top10KnowledgeSharingOrganizationInfo': top10_knowledge_sharing_organization_info
    }
    # 写入合并后的数据源文件
    ensure_dir_and_write_file(
        CONFIG['ANALYZED_DATASOURCE_FILE_NAME'],
        json.dumps(datasource, indent=2, ensure_ascii=False)
    )


if __name__ == "__main__":
    year = datetime.now().year
    month = datetime.now().month
    current_key = f"{year}-{month}"
    previous_key = f"{year}-{month - 3}"
    # fetch_organization_data(current_key)
    analyze_organization_data(previous_key, current_key)
