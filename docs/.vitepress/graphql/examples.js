/**
 * GraphQL API 使用示例
 * 展示各种常见的查询场景
 */

import {
  getMembers,
  getMember,
  getStats,
  getDomainStats,
  getLeaderboards,
  getLeaderboard,
  getProjects,
  getTopProjects,
  getOrganizations,
  getCommitStats,
  getWeeklyTopCommitters,
  getNightOwls,
  query,
  graphqlClient
} from './index.js'

/**
 * 示例 1: 基础查询
 */
export async function example1_basicQueries() {
  console.log('=== 示例 1: 基础查询 ===')
  
  // 获取统计信息
  const stats = await getStats()
  console.log('统计信息:', stats)
  
  // 查询所有成员（前 10 个）
  const members = await getMembers({}, { limit: 10 })
  console.log('成员列表:', members.length, '个')
  
  // 查询单个成员
  if (members.length > 0) {
    const member = await getMember(members[0].id)
    console.log('单个成员:', member.name)
  }
}

/**
 * 示例 2: 过滤和排序
 */
export async function example2_filterAndSort() {
  console.log('=== 示例 2: 过滤和排序 ===')
  
  // 查询 NLP 方向的成员
  const nlpMembers = await getMembers(
    { domain: 'NLP' },
    { limit: 5 }
  )
  console.log('NLP 方向成员:', nlpMembers.length, '个')
  
  // 查询 followers 超过 100 的成员，按 followers 降序
  const popularMembers = await getMembers(
    { minFollowers: 100 },
    { sortBy: 'FOLLOWERS', sortOrder: 'DESC', limit: 10 }
  )
  console.log('热门成员 (followers > 100):', popularMembers.length, '个')
  
  // 查询组织成员
  const orgMembers = await getMembers(
    { isOrgMember: true },
    { limit: 20 }
  )
  console.log('组织成员:', orgMembers.length, '个')
}

/**
 * 示例 3: 研究方向统计
 */
export async function example3_domainStats() {
  console.log('=== 示例 3: 研究方向统计 ===')
  
  // 获取前 10 个热门研究方向
  const topDomains = await getDomainStats(10)
  console.log('热门研究方向:')
  topDomains.forEach((stat, index) => {
    console.log(`  ${index + 1}. ${stat.domain}: ${stat.count} 人 (${stat.percentage}%)`)
  })
}

/**
 * 示例 4: 排行榜查询
 */
export async function example4_leaderboards() {
  console.log('=== 示例 4: 排行榜查询 ===')
  
  // 获取所有排行榜
  const allLeaderboards = await getLeaderboards({}, 5)
  console.log('所有排行榜:')
  allLeaderboards.forEach(board => {
    console.log(`  ${board.title}: ${board.members.length} 人`)
  })
  
  // 获取人气王榜前 10 名
  const popularityBoard = await getLeaderboard('popularity', {}, 10)
  console.log('\n人气王榜 Top 10:')
  popularityBoard.members.forEach(item => {
    console.log(`  ${item.rank}. ${item.member.name} - ${item.scoreDisplay}`)
  })
  
  // 获取 NLP 方向的综合实力榜
  const nlpComprehensive = await getLeaderboard(
    'comprehensive',
    { domain: 'NLP' },
    5
  )
  console.log('\nNLP 方向综合实力榜:')
  nlpComprehensive.members.forEach(item => {
    console.log(`  ${item.rank}. ${item.member.name} - ${item.scoreDisplay}`)
  })
}

/**
 * 示例 5: 项目和组织查询
 */
export async function example5_projectsAndOrgs() {
  console.log('=== 示例 5: 项目和组织查询 ===')
  
  // 获取 Star 数最多的 5 个项目
  const topProjects = await getTopProjects(5)
  console.log('热门项目 Top 5:')
  topProjects.forEach((project, index) => {
    console.log(`  ${index + 1}. ${project.name}: ${project.stars} stars`)
  })
  
  // 获取同类组织信息
  const orgs = await getOrganizations()
  console.log('\n同类组织:', orgs.length, '个')
}

/**
 * 示例 6: 提交统计
 */
export async function example6_commitStats() {
  console.log('=== 示例 6: 提交统计 ===')
  
  // 获取周提交排行榜
  const weeklyTop = await getWeeklyTopCommitters(5)
  console.log('周提交排行榜 Top 5:')
  weeklyTop.forEach((stat, index) => {
    console.log(`  ${index + 1}. ${stat.username}: ${stat.totalCommits} commits`)
  })
  
  // 获取夜猫子排行榜
  const nightOwls = await getNightOwls(5)
  console.log('\n夜猫子排行榜 Top 5:')
  nightOwls.forEach((stat, index) => {
    console.log(`  ${index + 1}. ${stat.username}: ${stat.nightCommits} 夜间 commits`)
  })
}

/**
 * 示例 7: 使用原始 GraphQL 查询
 */
export async function example7_rawGraphQL() {
  console.log('=== 示例 7: 原始 GraphQL 查询 ===')
  
  // 使用 GraphQL 查询语法
  const result = await query(`
    query {
      stats
    }
  `)
  
  console.log('GraphQL 查询结果:', result.data.stats)
}

/**
 * 示例 8: 预加载和缓存
 */
export async function example8_preloadAndCache() {
  console.log('=== 示例 8: 预加载和缓存 ===')
  
  // 预加载所有数据
  console.log('开始预加载数据...')
  const startTime = Date.now()
  await graphqlClient.preload()
  const loadTime = Date.now() - startTime
  console.log(`数据预加载完成，耗时: ${loadTime}ms`)
  
  // 使用缓存的数据（速度更快）
  const cacheStartTime = Date.now()
  const members = await getMembers({}, { limit: 100 })
  const cacheTime = Date.now() - cacheStartTime
  console.log(`从缓存查询 ${members.length} 个成员，耗时: ${cacheTime}ms`)
  
  // 清除缓存
  graphqlClient.clearCache()
  console.log('缓存已清除')
}

/**
 * 示例 9: 复杂组合查询
 */
export async function example9_complexQueries() {
  console.log('=== 示例 9: 复杂组合查询 ===')
  
  // 并行查询多个数据
  const [stats, topDomains, popularMembers, leaderboards] = await Promise.all([
    getStats(),
    getDomainStats(5),
    getMembers({ minFollowers: 500 }, { limit: 10, sortBy: 'FOLLOWERS', sortOrder: 'DESC' }),
    getLeaderboards({}, 3)
  ])
  
  console.log('统计信息:', stats)
  console.log('热门研究方向:', topDomains.length, '个')
  console.log('热门成员:', popularMembers.length, '个')
  console.log('排行榜:', leaderboards.length, '个')
}

/**
 * 示例 10: 实际应用场景
 */
export async function example10_realWorldScenario() {
  console.log('=== 示例 10: 实际应用场景 ===')
  
  // 场景：构建一个成员推荐系统
  
  // 1. 获取用户感兴趣的研究方向
  const interestedDomain = 'NLP'
  
  // 2. 查询该方向的活跃成员
  const activeMembers = await getMembers(
    { domain: interestedDomain, minFollowers: 50 },
    { sortBy: 'ORG_TOTAL_STARS', sortOrder: 'DESC', limit: 5 }
  )
  
  console.log(`推荐关注的 ${interestedDomain} 方向成员:`)
  activeMembers.forEach((member, index) => {
    console.log(`  ${index + 1}. ${member.name}`)
    console.log(`     - Followers: ${member.followers}`)
    console.log(`     - 组织 Stars: ${member.org_total_stars}`)
    console.log(`     - 参与仓库: ${member.org_repos_count}`)
  })
  
  // 3. 获取该方向的统计信息
  const allDomainStats = await getDomainStats()
  const domainStat = allDomainStats.find(s => s.domain === interestedDomain)
  
  if (domainStat) {
    console.log(`\n${interestedDomain} 方向统计:`)
    console.log(`  - 总人数: ${domainStat.count}`)
    console.log(`  - 占比: ${domainStat.percentage}%`)
  }
}

/**
 * 运行所有示例
 */
export async function runAllExamples() {
  const examples = [
    example1_basicQueries,
    example2_filterAndSort,
    example3_domainStats,
    example4_leaderboards,
    example5_projectsAndOrgs,
    example6_commitStats,
    example7_rawGraphQL,
    example8_preloadAndCache,
    example9_complexQueries,
    example10_realWorldScenario
  ]
  
  for (const example of examples) {
    try {
      await example()
      console.log('\n')
    } catch (error) {
      console.error(`示例执行失败:`, error)
    }
  }
}

// 如果直接运行此文件
if (typeof window === 'undefined' && import.meta.url === `file://${process.argv[1]}`) {
  runAllExamples().then(() => {
    console.log('所有示例执行完成')
  }).catch(error => {
    console.error('执行失败:', error)
  })
}
