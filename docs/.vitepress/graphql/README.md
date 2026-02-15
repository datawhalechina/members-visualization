# GraphQL API 实现说明

## 架构概览

这是一个纯前端实现的 GraphQL API 系统，无需后端服务器即可提供完整的数据查询功能。

```
graphql/
├── schema.js       # GraphQL Schema 定义
├── dataSource.js   # 数据源管理和缓存
├── resolvers.js    # 查询解析器实现
├── client.js       # 客户端接口
└── index.js        # 统一导出
```

## 核心组件

### 1. Schema (schema.js)

定义了完整的 GraphQL 类型系统：

- **类型定义**: Member, DomainStat, Leaderboard, ProjectInfo 等
- **查询接口**: members, stats, leaderboards, projects 等
- **输入类型**: MemberFilter, 排序枚举等

### 2. DataSource (dataSource.js)

负责数据加载和缓存管理：

- **数据加载**: 从静态 JSON 文件加载数据
- **缓存机制**: 自动缓存已加载的数据
- **数据解析**: 处理 CSV 格式和类型转换
- **预加载**: 支持批量预加载所有数据

**关键方法:**
```javascript
dataSource.loadMembers()           // 加载成员数据
dataSource.loadProjects()          // 加载项目数据
dataSource.loadOrganizations()     // 加载组织数据
dataSource.preloadAll()            // 预加载所有数据
dataSource.clearCache()            // 清除缓存
```

### 3. Resolvers (resolvers.js)

实现所有 GraphQL 查询的业务逻辑：

- **数据过滤**: 按研究方向、followers 等条件筛选
- **数据排序**: 支持多字段排序
- **分页处理**: limit 和 offset 支持
- **排行榜计算**: 5 种不同的排行榜算法
- **统计计算**: 实时计算各种统计指标

**核心算法:**

#### 人气王榜
```javascript
score = followers * 0.6 + org_total_stars * 0.4
```

#### 多产榜
```javascript
score = org_repos_count
```

#### 社交达人榜
```javascript
score = following
```

#### 新星榜
```javascript
activity = followers + org_total_stars
score = activity / orgRepos * (orgRepos < 5 ? 1.5 : 1)
```

#### 综合实力榜
```javascript
score = org_total_stars * 0.3 +
        followers * 0.25 +
        org_repos_count * 0.2 +
        following * 0.15 +
        org_total_contributions * 0.1
```

### 4. Client (client.js)

提供简洁的 JavaScript API：

- **便捷方法**: 封装常用查询为简单函数
- **查询解析**: 支持 GraphQL 查询字符串
- **错误处理**: 统一的错误处理机制

## 数据流程

```
用户调用 API
    ↓
Client 接收请求
    ↓
Resolver 处理查询
    ↓
DataSource 加载数据 (带缓存)
    ↓
Resolver 处理和计算
    ↓
返回结果给用户
```

## 使用示例

### 基础查询

```javascript
import { getMembers, getStats } from './.vitepress/graphql'

// 查询统计信息
const stats = await getStats()

// 查询成员
const members = await getMembers(
  { domain: 'NLP', minFollowers: 100 },
  { limit: 20, sortBy: 'FOLLOWERS', sortOrder: 'DESC' }
)
```

### 高级查询

```javascript
import { graphqlClient } from './.vitepress/graphql'

// 预加载所有数据
await graphqlClient.preload()

// 查询多个排行榜
const leaderboards = await graphqlClient.getLeaderboards(
  { isOrgMember: true },
  50
)

// 查询特定排行榜
const popularityBoard = await graphqlClient.getLeaderboard(
  'popularity',
  { domain: 'NLP' },
  20
)
```

### 在 Vue 组件中使用

```vue
<script setup>
import { ref, onMounted } from 'vue'
import { getMembers, getDomainStats } from './.vitepress/graphql'

const members = ref([])
const domainStats = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    // 并行加载多个数据
    const [membersData, statsData] = await Promise.all([
      getMembers({ domain: 'NLP' }, { limit: 10 }),
      getDomainStats(5)
    ])
    
    members.value = membersData
    domainStats.value = statsData
  } catch (error) {
    console.error('加载失败:', error)
  } finally {
    loading.value = false
  }
})
</script>
```

## 性能优化

### 1. 数据缓存

所有数据在首次加载后会被缓存，后续查询直接使用缓存数据：

```javascript
// 第一次调用会从文件加载
const members1 = await getMembers()

// 第二次调用使用缓存，速度更快
const members2 = await getMembers()
```

### 2. 预加载

在应用启动时预加载所有数据：

```javascript
// 在 main.js 或 app setup 中
import { graphqlClient } from './.vitepress/graphql'

graphqlClient.preload().then(() => {
  console.log('数据预加载完成')
})
```

### 3. 按需查询

使用过滤和限制减少数据处理量：

```javascript
// ❌ 不推荐：加载所有数据
const allMembers = await getMembers()

// ✅ 推荐：只加载需要的数据
const topMembers = await getMembers(
  { minFollowers: 1000 },
  { limit: 20, sortBy: 'FOLLOWERS', sortOrder: 'DESC' }
)
```

## 扩展指南

### 添加新的查询

1. **更新 Schema** (schema.js)
```javascript
type Query {
  # 添加新查询
  membersByLocation(location: String!): [Member!]!
}
```

2. **实现 Resolver** (resolvers.js)
```javascript
export const resolvers = {
  Query: {
    async membersByLocation(_, { location }) {
      const members = await dataSource.loadMembers()
      return members.filter(m => m.location === location)
    }
  }
}
```

3. **添加便捷方法** (client.js)
```javascript
export const getMembersByLocation = (location) =>
  graphqlClient.getMembersByLocation(location)
```

### 添加新的数据源

1. **在 DataSource 中添加加载方法**
```javascript
async loadNewData() {
  return await this.loadData('newData', 'data/new_data.json')
}
```

2. **在 Resolver 中使用**
```javascript
async newQuery() {
  const data = await dataSource.loadNewData()
  return processData(data)
}
```

## 测试

### 单元测试示例

```javascript
import { getMembers, getStats } from './.vitepress/graphql'

describe('GraphQL API', () => {
  test('getStats returns correct structure', async () => {
    const stats = await getStats()
    
    expect(stats).toHaveProperty('totalMembers')
    expect(stats).toHaveProperty('totalDomains')
    expect(stats).toHaveProperty('avgDomainsPerMember')
    expect(typeof stats.totalMembers).toBe('number')
  })
  
  test('getMembers with filter works', async () => {
    const members = await getMembers(
      { domain: 'NLP' },
      { limit: 10 }
    )
    
    expect(members.length).toBeLessThanOrEqual(10)
    members.forEach(m => {
      expect(m.domain).toContain('NLP')
    })
  })
})
```

## 常见问题

### Q: 数据更新频率？

A: 数据通过 GitHub Actions 每日自动更新。可以通过 `clearCache()` 手动刷新。

### Q: 支持实时查询吗？

A: 当前版本使用静态数据。如需实时数据，可以：
1. 修改 DataSource 连接到 API 端点
2. 添加轮询机制定期刷新
3. 使用 WebSocket 推送更新

### Q: 性能如何？

A: 
- 首次加载: ~100-500ms（取决于数据大小）
- 缓存查询: <10ms
- 复杂计算: ~50-100ms

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License
