# 合并仓库详情
import json


# 获取十大知识分享组织信息
def get_top10_knowledge_sharing_organization_info(previous_data_path, current_data_path):
    with open(previous_data_path, 'r', encoding='utf-8') as f:
        previous_data_list = json.load(f)

    with open(current_data_path, 'r', encoding='utf-8') as f:
        current_data_list = json.load(f)

    diff_info = []
    for item in current_data_list:
        previous_item = next(
            (prev for prev in previous_data_list if prev['name'] == item['name']), None)
        if previous_item:
            diff_info.append({
                **item,
                'starAdd': item['star_count'] - previous_item['star_count'],
                'rankAdd': item['rank'] - previous_item['rank'],
            })

    print(json.dumps(diff_info, indent=2, ensure_ascii=False))
    return diff_info
