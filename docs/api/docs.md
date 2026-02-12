# GraphQL API 文档

本项目提供了一套纯前端实现的 GraphQL API，用于查询和处理 Datawhale 组织的成员、项目和统计数据。

## 特性

- ✅ **标准 GraphQL 实现** - 使用官方 GraphQL 规范，支持所有标准查询
- ✅ **Serverless 架构** - 由 Vercel Serverless Function 提供高性能的 GraphQL API 服务
- ✅ **类型安全** - 完整的 GraphQL Schema 定义和类型检查
- ✅ **便捷 API** - 提供简洁的 JavaScript 函数接口，底层封装了 API 调用
- ✅ **灵活查询** - 支持标准 GraphQL 查询语法、过滤、排序、分页等功能

## 快速开始

### Endpoint 信息

- **URL**: `/api/graphql` (相对路径) 或 `https://your-domain.com/api/graphql`
- **Method**: `POST`
- **Content-Type**: `application/json`

### 1. 使用 curl

```bash
curl -X POST /api/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ stats { totalMembers } }"}'
```

### 2. 使用 JavaScript (fetch)

```javascript
const query = `
  query {
    members(limit: 5) {
      name
      followers
    }
  }
`;

fetch('/api/graphql', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query })
})
  .then(res => res.json())
  .then(result => console.log(result.data));
```

### 3. 使用 Python

```python
import requests

url = 'https://your-domain.com/api/graphql'
query = """
query {
  stats {
    totalMembers
    totalDomains
  }
}
"""

response = requests.post(url, json={'query': query})
print(response.json())
```

## GraphQL Query 参考

所有的查询都位于 `Query` 类型下。

### 成员查询 (members)

查询成员列表，支持过滤、排序和分页。

```graphql
query {
  members(
    filter: { domain: "NLP", minFollowers: 100 },
    sortBy: FOLLOWERS,
    sortOrder: DESC,
    limit: 10,
    offset: 0
  ) {
    id
    name
    followers
    domain
  }
}
```

**参数 Arguments:**

- `filter` (MemberFilter): 过滤条件
  - `domain` (String)
  - `minFollowers` (Int)
  - `maxFollowers` (Int)
  - `isOrgMember` (Boolean)
- `sortBy` (MemberSortField): 排序字段
  - 可选值: `FOLLOWERS`, `FOLLOWING`, `ORG_REPOS_COUNT`, `ORG_TOTAL_STARS`, `NAME`
- `sortOrder` (SortOrder): 排序方向
  - 可选值: `ASC`, `DESC`
- `limit` (Int): 返回数量
- `offset` (Int): 偏移量

### 单个成员 (member)

查询单个成员信息。

```graphql
query {
  member(id: "some-github-username") {
    name
    followers
    repositories
  }
}
```

**参数 Arguments:**
- `id` (ID!): GitHub 用户名

### 统计信息 (stats)

获取组织整体统计信息。

```graphql
query {
  stats {
    totalMembers
    totalDomains
    avgDomainsPerMember
    mostPopularDomain
  }
}
```

### 研究方向统计 (domainStats)

获取各研究方向的统计数据。

```graphql
query {
  domainStats(limit: 10) {
    domain
    count
    percentage
  }
}
```

### 排行榜 (leaderboards)

```graphql
query {
  leaderboards(filter: {}, topCount: 10) {
    id
    title
    members {
      rank
      score
      member { name }
    }
  }
}
```

**参数 Arguments:**
- `filter` (MemberFilter): 过滤条件
- `topCount` (Int): 每个榜单的人数

支持的排行榜 ID: `popularity`, `productive`, `social`, `rising`, `comprehensive`。

### 项目与组织

```graphql
query {
  # 获取所有项目
  projects {
    name
    stars
    description
  }

  # 获取 Top 项目
  topProjects(limit: 5) {
    name
    stars
  }

  # 获取同类组织
  organizations {
    name
    description
  }
}
```

### 提交活跃度

```graphql
query {
  # 指定用户的提交统计
  commitStats(username: "username") {
    totalCommits
    weeklyCommits
  }
  
  # 周榜
  weeklyTopCommitters(limit: 10) {
    username
    weeklyCommits
  }
  
  # 夜猫子榜
  nightOwls(limit: 10) {
    username
    nightCommits
  }
}
```

## 数据类型定义

以下是 API 中使用的主要数据类型定义，可供参考。

### Member (Type)

```graphql
type Member {
  id: ID!                # GitHub 用户名
  name: String           # 姓名
  github: String         # GitHub 链接
  avatar: String         # 头像 URL
  domain: [String]       # 研究方向列表
  repositories: [String] # 仓库列表
  followers: Int         # Followers 数
  following: Int         # Following 数
  org_repos_count: Int   # 参与的组织仓库数
  org_total_stars: Int   # 组织仓库总 Stars
  org_total_contributions: Int # 组织总贡献数
}
```

### DomainStat (Type)

```graphql
type DomainStat {
  domain: String         # 研究方向名称
  count: Int             # 成员数量
  percentage: Float      # 占比百分比
  members: [Member]      # 该方向的所有成员
}
```

### RankedMember (Type)

```graphql
type RankedMember {
  rank: Int              # 排名
  member: Member         # 成员信息
  score: Float           # 得分
  scoreDisplay: String   # 得分显示文本
}
```

## 常见问题

### Q: 数据从哪里来？

A: 数据来自 `docs/public/data/` 目录下的 JSON 文件。在 Vercel Serverless 环境中，API 会自动读取这些静态文件。

### Q: 支持实时数据吗？

A: 目前是基于静态数据的 API。数据通过 GitHub Actions 定期更新。

### Q: 跨域 (CORS) 支持吗？

A: 是的，API 设置了 `Access-Control-Allow-Origin: *`，允许从任何域名调用。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个 API！

---

*最后更新: {{ new Date().toLocaleDateString('zh-CN') }}*
