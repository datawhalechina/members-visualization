/**
 * GraphQL API 入口文件
 * 导出所有公共接口
 */

// export { schema, typeDefs } from './schema.js'
// export { resolvers } from './resolvers.js'
// export { dataSource } from './dataSource.js'
export {
  graphqlClient,
  query,
  mutate,
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
  getNightOwls
} from './client.js'

/**
 * 使用示例：
 * 
 * // 1. 使用便捷方法
 * import { getMembers, getStats } from './.vitepress/graphql'
 * 
 * const members = await getMembers({ domain: 'NLP' }, { limit: 10 })
 * const stats = await getStats()
 * 
 * // 2. 使用标准 GraphQL 查询字符串
 * import { query } from './.vitepress/graphql'
 * 
 * const result = await query(`
 *   query GetMembers($domain: String) {
 *     members(filter: { domain: $domain }, limit: 10) {
 *       id
 *       name
 *       followers
 *     }
 *   }
 * `, { domain: 'NLP' })
 * 
 * console.log(result.data.members)
 * 
 * // 3. 使用客户端实例
 * import { graphqlClient } from './.vitepress/graphql'
 * 
 * await graphqlClient.preload() // 预加载数据
 * const members = await graphqlClient.getMembers()
 * 
 * // 4. 直接使用 GraphQL Schema（高级用法）
 * import { schema } from './.vitepress/graphql'
 * import { graphql } from 'graphql'
 * 
 * const result = await graphql({
 *   schema,
 *   source: '{ stats { totalMembers } }'
 * })
 */
