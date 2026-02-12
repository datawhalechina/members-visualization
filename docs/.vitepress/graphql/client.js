/**
 * GraphQL 客户端
 * 使用 fetch 调用后端 API /api/graphql
 */

// 移除本地 graphql 依赖
// import { graphql } from 'graphql'
// import { schema } from './schema.js'
// import { dataSource } from './dataSource.js'

const API_ENDPOINT = '/api/graphql'

/**
 * GraphQL 客户端类
 */
class GraphQLClient {
  constructor() {
    // 允许自定义 endpoint，默认为 /api/graphql
    this.endpoint = API_ENDPOINT
  }

  /**
   * 执行 GraphQL 查询
   * @param {string} source - GraphQL 查询字符串
   * @param {object} variableValues - 查询变量
   * @param {object} contextValue - 上下文值 (不再使用)
   * @returns {Promise<object>} 查询结果
   */
  async query(source, variableValues = {}, contextValue = {}) {
    try {
      // 检查是否在浏览器环境
      if (typeof fetch === 'undefined') {
        console.warn('fetch is not defined. You might be running in a build environment without access to the live API.')
        return { data: {} }
      }

      const response = await fetch(this.endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          query: source,
          variables: variableValues
        })
      })

      if (!response.ok) {
        throw new Error(`Example API Error: ${response.status} ${response.statusText}`)
      }
      
      const result = await response.json()
      return result
    } catch (error) {
      console.error('GraphQL Query Error:', error)
      return {
        errors: [{
          message: error.message,
          stack: error.stack
        }]
      }
    }
  }

  /**
   * 执行 GraphQL Mutation
   * @param {string} source - GraphQL mutation 字符串
   * @param {object} variableValues - 变量
   * @returns {Promise<object>} 执行结果
   */
  async mutate(source, variableValues = {}) {
    return this.query(source, variableValues)
  }

  /**
   * 便捷方法：查询成员
   */
  async getMembers(filter = {}, options = {}) {
    const query = `
      query GetMembers($filter: MemberFilter, $sortBy: MemberSortField, $sortOrder: SortOrder, $limit: Int, $offset: Int) {
        members(filter: $filter, sortBy: $sortBy, sortOrder: $sortOrder, limit: $limit, offset: $offset) {
          id
          name
          github
          avatar
          domain
          repositories
          followers
          following
          org_repos_count
          org_total_stars
          org_total_contributions
        }
      }
    `
    
    const result = await this.query(query, { filter, ...options })
    return result.data?.members || []
  }

  /**
   * 便捷方法：查询单个成员
   */
  async getMember(id) {
    const query = `
      query GetMember($id: ID!) {
        member(id: $id) {
          id
          name
          github
          avatar
          domain
          repositories
          followers
          following
          org_repos_count
          org_total_stars
          org_total_contributions
        }
      }
    `
    
    const result = await this.query(query, { id })
    return result.data?.member || null
  }

  /**
   * 便捷方法：查询统计信息
   */
  async getStats() {
    const query = `
      query GetStats {
        stats {
          totalMembers
          totalDomains
          avgDomainsPerMember
          mostPopularDomain
        }
      }
    `
    
    const result = await this.query(query)
    return result.data?.stats || null
  }

  /**
   * 便捷方法：查询研究方向统计
   */
  async getDomainStats(limit) {
    const query = `
      query GetDomainStats($limit: Int) {
        domainStats(limit: $limit) {
          domain
          count
          percentage
          members {
            id
            name
            avatar
          }
        }
      }
    `
    
    const result = await this.query(query, { limit })
    return result.data?.domainStats || []
  }

  /**
   * 便捷方法：查询排行榜
   */
  async getLeaderboards(filter = {}, topCount = 20) {
    const query = `
      query GetLeaderboards($filter: MemberFilter, $topCount: Int) {
        leaderboards(filter: $filter, topCount: $topCount) {
          id
          title
          description
          members {
            rank
            score
            scoreDisplay
            member {
              id
              name
              avatar
              github
              followers
              following
              org_repos_count
              org_total_stars
            }
          }
        }
      }
    `
    
    const result = await this.query(query, { filter, topCount })
    return result.data?.leaderboards || []
  }

  /**
   * 便捷方法：查询单个排行榜
   */
  async getLeaderboard(id, filter = {}, topCount = 20) {
    const query = `
      query GetLeaderboard($id: String!, $filter: MemberFilter, $topCount: Int) {
        leaderboard(id: $id, filter: $filter, topCount: $topCount) {
          id
          title
          description
          members {
            rank
            score
            scoreDisplay
            member {
              id
              name
              avatar
              github
              followers
              following
              org_repos_count
              org_total_stars
            }
          }
        }
      }
    `
    
    const result = await this.query(query, { id, filter, topCount })
    return result.data?.leaderboard || null
  }

  /**
   * 便捷方法：查询项目
   */
  async getProjects() {
    const query = `
      query GetProjects {
        projects {
          name
          stars
          starHistory {
            date
            stars
          }
        }
      }
    `
    
    const result = await this.query(query)
    return result.data?.projects || []
  }

  /**
   * 便捷方法：查询热门项目
   */
  async getTopProjects(limit = 10) {
    const query = `
      query GetTopProjects($limit: Int) {
        topProjects(limit: $limit) {
          name
          stars
          starHistory {
            date
            stars
          }
        }
      }
    `
    
    const result = await this.query(query, { limit })
    return result.data?.topProjects || []
  }

  /**
   * 便捷方法：查询组织
   */
  async getOrganizations() {
    const query = `
      query GetOrganizations {
        organizations {
          name
          stars
          repos
          members
          change {
            stars
            repos
            members
          }
        }
      }
    `
    
    const result = await this.query(query)
    return result.data?.organizations || []
  }

  /**
   * 便捷方法：查询提交统计
   */
  async getCommitStats(username) {
    const query = `
      query GetCommitStats($username: String) {
        commitStats(username: $username) {
          username
          totalCommits
          weeklyCommits
          nightCommits
        }
      }
    `
    
    const result = await this.query(query, { username })
    return result.data?.commitStats || []
  }

  /**
   * 便捷方法：查询周提交排行
   */
  async getWeeklyTopCommitters(limit = 10) {
    const query = `
      query GetWeeklyTopCommitters($limit: Int) {
        weeklyTopCommitters(limit: $limit) {
          username
          totalCommits
          weeklyCommits
          nightCommits
        }
      }
    `
    
    const result = await this.query(query, { limit })
    return result.data?.weeklyTopCommitters || []
  }

  /**
   * 便捷方法：查询夜猫子
   */
  async getNightOwls(limit = 10) {
    const query = `
      query GetNightOwls($limit: Int) {
        nightOwls(limit: $limit) {
          username
          totalCommits
          weeklyCommits
          nightCommits
        }
      }
    `
    
    const result = await this.query(query, { limit })
    return result.data?.nightOwls || []
  }

  /**
   * 预加载所有数据
   */
  async preload() {
    // 换成 API 模式后，无需预加载
    return true
  }

  /**
   * 清除缓存
   */
  clearCache() {
    // 换成 API 模式后，无需清除本地缓存
    return true
  }
}

// 导出单例实例
export const graphqlClient = new GraphQLClient()

// 导出便捷的查询函数
export const query = (source, variables) => 
  graphqlClient.query(source, variables)

export const mutate = (source, variables) =>
  graphqlClient.mutate(source, variables)

export const getMembers = (filter, options) => 
  graphqlClient.getMembers(filter, options)

export const getMember = (id) => 
  graphqlClient.getMember(id)

export const getStats = () => 
  graphqlClient.getStats()

export const getDomainStats = (limit) => 
  graphqlClient.getDomainStats(limit)

export const getLeaderboards = (filter, topCount) => 
  graphqlClient.getLeaderboards(filter, topCount)

export const getLeaderboard = (id, filter, topCount) => 
  graphqlClient.getLeaderboard(id, filter, topCount)

export const getProjects = () => 
  graphqlClient.getProjects()

export const getTopProjects = (limit) => 
  graphqlClient.getTopProjects(limit)

export const getOrganizations = () => 
  graphqlClient.getOrganizations()

export const getCommitStats = (username) => 
  graphqlClient.getCommitStats(username)

export const getWeeklyTopCommitters = (limit) => 
  graphqlClient.getWeeklyTopCommitters(limit)

export const getNightOwls = (limit) => 
  graphqlClient.getNightOwls(limit)
