/**
 * GraphQL Resolvers
 * 实现所有查询的解析逻辑
 */

import { dataSource } from './dataSource.js'

/**
 * 过滤成员数据
 */
function filterMembers(members, filter = {}) {
  let filtered = [...members]

  if (filter.domain) {
    filtered = filtered.filter(m => 
      m.domain && m.domain.includes(filter.domain)
    )
  }

  if (filter.minFollowers !== undefined) {
    filtered = filtered.filter(m => 
      (m.followers || 0) >= filter.minFollowers
    )
  }

  if (filter.maxFollowers !== undefined) {
    filtered = filtered.filter(m => 
      (m.followers || 0) <= filter.maxFollowers
    )
  }

  if (filter.isOrgMember !== undefined) {
    const orgMembers = dataSource.cache.organizationMembers
    if (orgMembers) {
      filtered = filtered.filter(m => {
        const isOrgMember = orgMembers.has(m.id)
        return filter.isOrgMember ? isOrgMember : !isOrgMember
      })
    }
  }

  return filtered
}

/**
 * 排序成员数据
 */
function sortMembers(members, sortBy = 'NAME', sortOrder = 'ASC') {
  const sorted = [...members]
  
  const compareFn = (a, b) => {
    let aVal, bVal
    
    switch (sortBy) {
      case 'FOLLOWERS':
        aVal = a.followers || 0
        bVal = b.followers || 0
        break
      case 'FOLLOWING':
        aVal = a.following || 0
        bVal = b.following || 0
        break
      case 'ORG_REPOS_COUNT':
        aVal = a.org_repos_count || 0
        bVal = b.org_repos_count || 0
        break
      case 'ORG_TOTAL_STARS':
        aVal = a.org_total_stars || 0
        bVal = b.org_total_stars || 0
        break
      case 'NAME':
      default:
        aVal = a.name || a.id || ''
        bVal = b.name || b.id || ''
        return sortOrder === 'ASC' 
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal)
    }
    
    return sortOrder === 'ASC' ? aVal - bVal : bVal - aVal
  }
  
  return sorted.sort(compareFn)
}

/**
 * 计算排行榜
 */
function calculateLeaderboard(members, type, topCount = 20) {
  let scored = []
  
  switch (type) {
    case 'popularity':
      scored = members.map(m => ({
        member: m,
        score: (m.followers || 0) * 0.6 + (m.org_total_stars || 0) * 0.4,
        scoreDisplay: `${m.followers || 0} followers + ${m.org_total_stars || 0} 组织stars`
      }))
      break
      
    case 'productive':
      scored = members.map(m => ({
        member: m,
        score: m.org_repos_count || 0,
        scoreDisplay: `参与 ${m.org_repos_count || 0} 个组织仓库`
      }))
      break
      
    case 'social':
      scored = members.map(m => ({
        member: m,
        score: m.following || 0,
        scoreDisplay: `关注 ${m.following || 0} 人`
      }))
      break
      
    case 'rising':
      scored = members.map(m => {
        const orgRepos = Math.max(m.org_repos_count || 1, 1)
        const activity = (m.followers || 0) + (m.org_total_stars || 0)
        const score = activity / orgRepos * (orgRepos < 5 ? 1.5 : 1)
        
        return {
          member: m,
          score,
          scoreDisplay: `活跃度 ${Math.round(score)}`
        }
      })
      break
      
    case 'comprehensive':
      scored = members.map(m => {
        const score = 
          (m.org_total_stars || 0) * 0.3 +
          (m.followers || 0) * 0.25 +
          (m.org_repos_count || 0) * 0.2 +
          (m.following || 0) * 0.15 +
          (m.org_total_contributions || 0) * 0.1
        
        return {
          member: m,
          score,
          scoreDisplay: `综合分 ${Math.round(score)}`
        }
      })
      break
      
    default:
      return []
  }
  
  return scored
    .filter(item => item.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, topCount)
    .map((item, index) => ({
      rank: index + 1,
      ...item
    }))
}

/**
 * GraphQL Resolvers
 */
export const resolvers = {
  Query: {
    // 成员查询
    async members(_, { filter, sortBy, sortOrder, limit, offset }) {
      const members = await dataSource.loadMembers()
      let result = filterMembers(members, filter)
      
      if (sortBy) {
        result = sortMembers(result, sortBy, sortOrder)
      }
      
      if (offset) {
        result = result.slice(offset)
      }
      
      if (limit) {
        result = result.slice(0, limit)
      }
      
      return result
    },
    
    async member(_, { id }) {
      const members = await dataSource.loadMembers()
      return members.find(m => m.id === id) || null
    },
    
    async membersByDomain(_, { domain }) {
      const members = await dataSource.loadMembers()
      return members.filter(m => 
        m.domain && m.domain.includes(domain)
      )
    },
    
    // 统计查询
    async stats() {
      const members = await dataSource.loadMembers()
      
      const domainCount = {}
      members.forEach(m => {
        m.domain.forEach(d => {
          if (d) {
            domainCount[d] = (domainCount[d] || 0) + 1
          }
        })
      })
      
      const totalDomains = Object.keys(domainCount).length
      const avgDomainsPerMember = members.length > 0
        ? members.reduce((sum, m) => sum + m.domain.length, 0) / members.length
        : 0
      
      const mostPopularDomain = Object.entries(domainCount)
        .sort((a, b) => b[1] - a[1])[0]?.[0] || null
      
      return {
        totalMembers: members.length,
        totalDomains,
        avgDomainsPerMember: parseFloat(avgDomainsPerMember.toFixed(2)),
        mostPopularDomain
      }
    },
    
    async domainStats(_, { limit }) {
      const members = await dataSource.loadMembers()
      
      const domainCount = {}
      const domainMembers = {}
      
      members.forEach(m => {
        m.domain.forEach(d => {
          if (d) {
            domainCount[d] = (domainCount[d] || 0) + 1
            if (!domainMembers[d]) {
              domainMembers[d] = []
            }
            domainMembers[d].push(m)
          }
        })
      })
      
      let stats = Object.entries(domainCount)
        .map(([domain, count]) => ({
          domain,
          count,
          percentage: parseFloat(((count / members.length) * 100).toFixed(2)),
          members: domainMembers[domain]
        }))
        .sort((a, b) => b.count - a.count)
      
      if (limit) {
        stats = stats.slice(0, limit)
      }
      
      return stats
    },
    
    // 排行榜查询
    async leaderboards(_, { filter, topCount = 20 }) {
      const members = await dataSource.loadMembers()
      await dataSource.loadOrganizationMembers() // 确保组织成员数据已加载
      
      const filtered = filterMembers(members, filter)
      
      const leaderboardTypes = [
        { id: 'popularity', title: '人气王榜', description: '综合个人 Followers 和组织仓库 Stars 的影响力排行' },
        { id: 'productive', title: '多产榜', description: '基于参与组织仓库数量的贡献广度排行' },
        { id: 'social', title: '社交达人榜', description: '基于 Following 数量的社交活跃度排行' },
        { id: 'rising', title: '新星榜', description: '基于组织贡献活跃度的潜力新星排行' },
        { id: 'comprehensive', title: '综合实力榜', description: '基于组织贡献的多维度综合评分排行' }
      ]
      
      return leaderboardTypes.map(type => ({
        ...type,
        members: calculateLeaderboard(filtered, type.id, topCount)
      }))
    },
    
    async leaderboard(_, { id, filter, topCount = 20 }) {
      const members = await dataSource.loadMembers()
      await dataSource.loadOrganizationMembers()
      
      const filtered = filterMembers(members, filter)
      
      const leaderboardInfo = {
        popularity: { title: '人气王榜', description: '综合个人 Followers 和组织仓库 Stars 的影响力排行' },
        productive: { title: '多产榜', description: '基于参与组织仓库数量的贡献广度排行' },
        social: { title: '社交达人榜', description: '基于 Following 数量的社交活跃度排行' },
        rising: { title: '新星榜', description: '基于组织贡献活跃度的潜力新星排行' },
        comprehensive: { title: '综合实力榜', description: '基于组织贡献的多维度综合评分排行' }
      }
      
      const info = leaderboardInfo[id]
      if (!info) return null
      
      return {
        id,
        ...info,
        members: calculateLeaderboard(filtered, id, topCount)
      }
    },
    
    // 项目查询
    async projects() {
      return await dataSource.loadProjects()
    },
    
    async topProjects(_, { limit = 10 }) {
      const projects = await dataSource.loadProjects()
      return projects
        .sort((a, b) => (b.stars || 0) - (a.stars || 0))
        .slice(0, limit)
    },
    
    // 组织查询
    async organizations() {
      return await dataSource.loadOrganizations()
    },
    
    // 提交统计查询
    async commitStats(_, { username }) {
      const commits = await dataSource.loadCommits()
      
      if (!commits || !commits.weekly_commits) {
        return []
      }
      
      const stats = Object.entries(commits.weekly_commits).map(([user, data]) => ({
        username: user,
        totalCommits: data.total || 0,
        weeklyCommits: data.commits || [],
        nightCommits: data.night_commits || 0
      }))
      
      if (username) {
        return stats.filter(s => s.username === username)
      }
      
      return stats
    },
    
    async weeklyTopCommitters(_, { limit = 10 }) {
      const commits = await dataSource.loadCommits()
      
      if (!commits || !commits.weekly_commits) {
        return []
      }
      
      return Object.entries(commits.weekly_commits)
        .map(([user, data]) => ({
          username: user,
          totalCommits: data.total || 0,
          weeklyCommits: data.commits || [],
          nightCommits: data.night_commits || 0
        }))
        .sort((a, b) => b.totalCommits - a.totalCommits)
        .slice(0, limit)
    },
    
    async nightOwls(_, { limit = 10 }) {
      const commits = await dataSource.loadCommits()
      
      if (!commits || !commits.weekly_commits) {
        return []
      }
      
      return Object.entries(commits.weekly_commits)
        .map(([user, data]) => ({
          username: user,
          totalCommits: data.total || 0,
          weeklyCommits: data.commits || [],
          nightCommits: data.night_commits || 0
        }))
        .filter(s => s.nightCommits > 0)
        .sort((a, b) => b.nightCommits - a.nightCommits)
        .slice(0, limit)
    }
  },
  
  Mutation: {
    async refreshData() {
      dataSource.clearCache()
      await dataSource.preloadAll()
      return true
    }
  }
}
