# GraphQL API 文档

本项目提供了一套纯前端实现的 GraphQL API，用于查询和处理 Datawhale 组织的成员、项目和统计数据。

## 特性

- ✅ **标准 GraphQL 实现** - 使用官方 GraphQL.js 库，完全符合 GraphQL 规范
- ✅ **纯前端运行** - 无需后端服务器，直接在浏览器中运行
- ✅ **类型安全** - 完整的 GraphQL Schema 定义和类型检查
- ✅ **数据缓存** - 自动缓存数据，提高查询性能
- ✅ **便捷 API** - 提供简洁的 JavaScript 函数接口
- ✅ **灵活查询** - 支持标准 GraphQL 查询语法、过滤、排序、分页等功能

## 快速开始

### 1. 导入 API

```javascript
import { 
  getMembers, 
  getStats, 
  getDomainStats,
  getLeaderboards 
} from './.vitepress/graphql'
```

### 2. 查询数据

```javascript
// 获取统计信息
const stats = await getStats()
console.log(stats)
// { totalMembers: 500, totalDomains: 20, avgDomainsPerMember: 2.5, ... }

// 查询成员列表
const members = await getMembers(
  { domain: 'NLP', minFollowers: 100 },  // 过滤条件
  { limit: 10, sortBy: 'FOLLOWERS', sortOrder: 'DESC' }  // 选项
)

// 查询研究方向统计
const domainStats = await getDomainStats(10)

// 查询排行榜
const leaderboards = await getLeaderboards({}, 20)
```

## API 参考

### 成员查询

#### `getMembers(filter, options)`

查询成员列表，支持过滤、排序和分页。

**参数:**
- `filter` (Object, 可选)
  - `domain` (String) - 按研究方向筛选
  - `minFollowers` (Number) - 最小 followers 数
  - `maxFollowers` (Number) - 最大 followers 数
  - `isOrgMember` (Boolean) - 是否为组织成员
  
- `options` (Object, 可选)
  - `sortBy` (String) - 排序字段: `'FOLLOWERS'`, `'FOLLOWING'`, `'ORG_REPOS_COUNT'`, `'ORG_TOTAL_STARS'`, `'NAME'`
  - `sortOrder` (String) - 排序方向: `'ASC'`, `'DESC'`
  - `limit` (Number) - 限制返回数量
  - `offset` (Number) - 跳过前 N 条记录

**返回:** `Promise<Member[]>`

**示例:**
```javascript
// 查询 NLP 方向的成员，按 followers 降序排列，取前 20 个
const nlpMembers = await getMembers(
  { domain: 'NLP' },
  { sortBy: 'FOLLOWERS', sortOrder: 'DESC', limit: 20 }
)

// 查询 followers 超过 1000 的成员
const popularMembers = await getMembers(
  { minFollowers: 1000 },
  { sortBy: 'FOLLOWERS', sortOrder: 'DESC' }
)

// 查询组织成员
const orgMembers = await getMembers(
  { isOrgMember: true },
  { limit: 50 }
)
```

#### `getMember(id)`

查询单个成员信息。

**参数:**
- `id` (String) - 成员 ID (GitHub 用户名)

**返回:** `Promise<Member | null>`

**示例:**
```javascript
const member = await getMember('johndoe')
console.log(member.name, member.followers, member.domain)
```

#### `membersByDomain(domain)`

查询指定研究方向的所有成员。

**参数:**
- `domain` (String) - 研究方向名称

**返回:** `Promise<Member[]>`

**示例:**
```javascript
const cvMembers = await membersByDomain('CV')
```

### 统计查询

#### `getStats()`

获取整体统计信息。

**返回:** `Promise<StatsOverview>`

**返回数据结构:**
```javascript
{
  totalMembers: 500,           // 总成员数
  totalDomains: 20,            // 研究方向总数
  avgDomainsPerMember: 2.5,    // 平均每人研究方向数
  mostPopularDomain: 'NLP'     // 最热门研究方向
}
```

#### `getDomainStats(limit)`

获取研究方向统计信息。

**参数:**
- `limit` (Number, 可选) - 限制返回数量

**返回:** `Promise<DomainStat[]>`

**返回数据结构:**
```javascript
[
  {
    domain: 'NLP',
    count: 150,
    percentage: 30.0,
    members: [...]  // 该方向的所有成员
  },
  ...
]
```

### 排行榜查询

#### `getLeaderboards(filter, topCount)`

获取所有排行榜。

**参数:**
- `filter` (Object, 可选) - 成员过滤条件（同 getMembers）
- `topCount` (Number, 可选, 默认: 20) - 每个榜单显示的人数

**返回:** `Promise<Leaderboard[]>`

**排行榜类型:**
- `popularity` - 人气王榜
- `productive` - 多产榜
- `social` - 社交达人榜
- `rising` - 新星榜
- `comprehensive` - 综合实力榜

**示例:**
```javascript
// 获取所有排行榜，每个榜单显示前 10 名
const leaderboards = await getLeaderboards({}, 10)

// 仅显示组织成员的排行榜
const orgLeaderboards = await getLeaderboards(
  { isOrgMember: true },
  20
)
```

#### `getLeaderboard(id, filter, topCount)`

获取单个排行榜。

**参数:**
- `id` (String) - 排行榜 ID
- `filter` (Object, 可选) - 成员过滤条件
- `topCount` (Number, 可选, 默认: 20) - 显示人数

**返回:** `Promise<Leaderboard>`

**示例:**
```javascript
// 获取人气王榜前 50 名
const popularityBoard = await getLeaderboard('popularity', {}, 50)

// 获取 NLP 方向的综合实力榜
const nlpComprehensive = await getLeaderboard(
  'comprehensive',
  { domain: 'NLP' },
  20
)
```

### 项目查询

#### `getProjects()`

获取所有项目信息。

**返回:** `Promise<ProjectInfo[]>`

#### `getTopProjects(limit)`

获取 Star 数最多的项目。

**参数:**
- `limit` (Number, 可选, 默认: 10) - 返回数量

**返回:** `Promise<ProjectInfo[]>`

**示例:**
```javascript
// 获取 Star 数前 5 的项目
const topProjects = await getTopProjects(5)
```

### 组织查询

#### `getOrganizations()`

获取同类组织信息。

**返回:** `Promise<OrganizationInfo[]>`

### 提交统计查询

#### `getCommitStats(username)`

获取提交统计信息。

**参数:**
- `username` (String, 可选) - 用户名，不传则返回所有用户

**返回:** `Promise<CommitStats[]>`

#### `getWeeklyTopCommitters(limit)`

获取周提交排行榜。

**参数:**
- `limit` (Number, 可选, 默认: 10) - 返回数量

**返回:** `Promise<CommitStats[]>`

#### `getNightOwls(limit)`

获取夜猫子排行榜（夜间提交最多）。

**参数:**
- `limit` (Number, 可选, 默认: 10) - 返回数量

**返回:** `Promise<CommitStats[]>`

## 使用原始 GraphQL 查询

如果你更喜欢使用 GraphQL 查询语法，可以使用 `query` 函数：

```javascript
import { query } from './.vitepress/graphql'

const result = await query(`
  query {
    members(filter: { domain: "NLP" }, limit: 10)
  }
`)

console.log(result.data.members)
```

## 数据类型

### Member

```typescript
{
  id: string              // GitHub 用户名
  name: string            // 姓名
  github: string          // GitHub 链接
  avatar: string          // 头像 URL
  domain: string[]        // 研究方向列表
  repositories: string[]  // 仓库列表
  followers: number       // Followers 数
  following: number       // Following 数
  org_repos_count: number // 参与的组织仓库数
  org_total_stars: number // 组织仓库总 Stars
  org_total_contributions: number // 组织总贡献数
}
```

### DomainStat

```typescript
{
  domain: string          // 研究方向名称
  count: number           // 成员数量
  percentage: number      // 占比百分比
  members: Member[]       // 该方向的所有成员
}
```

### RankedMember

```typescript
{
  rank: number            // 排名
  member: Member          // 成员信息
  score: number           // 得分
  scoreDisplay: string    // 得分显示文本
}
```

## 高级用法

### 预加载数据

在应用启动时预加载所有数据，提高后续查询速度：

```javascript
import { graphqlClient } from './.vitepress/graphql'

// 在应用初始化时调用
await graphqlClient.preload()
```

### 清除缓存

如果需要重新加载数据：

```javascript
import { graphqlClient } from './.vitepress/graphql'

graphqlClient.clearCache()
```

### 在 Vue 组件中使用

```vue
<script setup>
import { ref, onMounted } from 'vue'
import { getMembers, getStats } from './.vitepress/graphql'

const members = ref([])
const stats = ref(null)

onMounted(async () => {
  stats.value = await getStats()
  members.value = await getMembers(
    { domain: 'NLP' },
    { limit: 20, sortBy: 'FOLLOWERS', sortOrder: 'DESC' }
  )
})
</script>

<template>
  <div>
    <h2>统计信息</h2>
    <p>总成员数: {{ stats?.totalMembers }}</p>
    
    <h2>NLP 方向成员</h2>
    <div v-for="member in members" :key="member.id">
      {{ member.name }} - {{ member.followers }} followers
    </div>
  </div>
</template>
```

## 交互式演示

<script setup>
import GraphQLDemo from './.vitepress/theme/graphql-demo/GraphQLDemo.vue'
</script>

<GraphQLDemo />

## 性能优化建议

1. **使用过滤和限制** - 避免一次性加载所有数据
2. **预加载数据** - 在应用启动时预加载常用数据
3. **合理使用缓存** - 数据会自动缓存，避免重复请求
4. **按需查询** - 只查询需要的字段和数据

## 常见问题

### Q: 数据从哪里来？

A: 数据来自 `docs/public/data/` 目录下的 JSON 文件，这些文件由 GitHub Actions 自动更新。

### Q: 如何更新数据？

A: 数据会通过 GitHub Actions 自动更新。如果需要手动刷新缓存，可以调用 `graphqlClient.clearCache()`。

### Q: 支持实时数据吗？

A: 目前是静态数据，每日自动更新。未来可以扩展支持实时数据源。

### Q: 可以在服务端使用吗？

A: 可以，但需要确保 `fetch` API 可用（Node.js 18+ 或使用 polyfill）。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个 API！

---

*最后更新: {{ new Date().toLocaleDateString('zh-CN') }}*
