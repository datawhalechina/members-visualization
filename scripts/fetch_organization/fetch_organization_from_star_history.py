import requests
from bs4 import BeautifulSoup


def get_organization_list(page):
    output = []
    try:
        response = requests.get(
            f"https://gitstar-ranking.com/organizations?page={page}")
        soup = BeautifulSoup(response.text, 'html.parser')

        # 获取两个列的组织数据
        columns = soup.select('div.container > div.row > div')
        for column in columns[:2]:  # 只取前两列
            organizations = column.select('a')
            for org in organizations:
                name_element = org.select_one(
                    'span.name > span.hidden-xs.hidden-sm')
                star_count_element = org.select_one(
                    'span.stargazers_count.pull-right')

                if name_element and star_count_element:
                    name = name_element.get_text(strip=True)
                    star_count = star_count_element.get_text(
                        strip=True).replace(',', '')

                    output.append({
                        'name': name,
                        'star_count': int(star_count)
                    })
    except Exception as e:
        print(f"fetch repo error: {e}")
        return []

    return output


def fetch_organization_from_star_history(page_count, top_knowledge_sharing_organization_name_list):
    organization_list = []
    for i in range(1, page_count + 1):
        result = get_organization_list(i)
        organization_list.extend(result)
        print(f"fetch organization from star history page {i} success")

    # 按star_count排序并添加排名
    organization_list.sort(key=lambda x: x['star_count'], reverse=True)
    for index, item in enumerate(organization_list):
        item['rank'] = index + 1

    # 筛选知识分享类组织
    top_10_knowledge_sharing_organization = [
        item for item in organization_list
        if item['name'] in top_knowledge_sharing_organization_name_list
    ]

    print("organization_list", organization_list)
    print("top_10_knowledge_sharing_organization",
          top_10_knowledge_sharing_organization)

    return {
        'organization_list': organization_list,
        'top_10_knowledge_sharing_organization': top_10_knowledge_sharing_organization
    }
