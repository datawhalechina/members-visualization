/**
 * 数据源管理
 * 负责从静态文件加载和缓存数据
 */

class DataSource {
  constructor() {
    this.cache = {
      members: null,
      commits: null,
      projects: null,
      organizations: null,
      organizationMembers: null,
      quarterlyContributors: null
    }
    this.loading = {}
  }

  /**
   * 获取基础路径
   */
  getBasePath() {
    // In Vercel Serverless Function, use a fixed URL or environment variable
    if (process.env.DATA_SOURCE_URL) {
      return process.env.DATA_SOURCE_URL;
    }
    // Default to the GitHub Pages URL
    return 'https://datawhalechina.github.io/members-visualization/';
  }

  /**
   * 构建完整路径
   */
  buildPath(relativePath) {
    const basePath = this.getBasePath()
    return `${basePath}${relativePath}`.replace(/\/+/g, '/')
  }

  /**
   * 通用数据加载方法
   */
  async loadData(cacheKey, path) {
    // 如果已缓存，直接返回
    if (this.cache[cacheKey]) {
      return this.cache[cacheKey]
    }

    // 如果正在加载，等待加载完成
    if (this.loading[cacheKey]) {
      return this.loading[cacheKey]
    }

    // 开始加载
    this.loading[cacheKey] = (async () => {
      try {
        const fullPath = this.buildPath(path)
        const response = await fetch(fullPath)
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data = await response.json()
        this.cache[cacheKey] = data
        delete this.loading[cacheKey]
        return data
      } catch (error) {
        delete this.loading[cacheKey]
        console.error(`Failed to load ${cacheKey}:`, error)
        throw error
      }
    })()

    return this.loading[cacheKey]
  }

  /**
   * 解析 CSV 格式的成员数据
   */
  parseMemberData(rawData) {
    if (!Array.isArray(rawData)) {
      return []
    }

    return rawData.map(item => {
      const parsed = { ...item }
      
      // 清理字符串字段
      Object.keys(parsed).forEach(key => {
        if (typeof parsed[key] === 'string') {
          parsed[key] = parsed[key].trim().replace(/^"|"$/g, '')
        }
      })

      // 解析数组字段
      if (parsed.domain) {
        if (typeof parsed.domain === 'string') {
          parsed.domain = parsed.domain
            .split(';')
            .map(d => d.trim())
            .filter(d => d && d !== 'null' && d !== 'undefined')
        } else if (!Array.isArray(parsed.domain)) {
          parsed.domain = []
        }
      } else {
        parsed.domain = []
      }

      if (parsed.repositories) {
        if (typeof parsed.repositories === 'string') {
          parsed.repositories = parsed.repositories
            .split(';')
            .map(r => r.trim())
            .filter(r => r && r !== 'null' && r !== 'undefined')
        } else if (!Array.isArray(parsed.repositories)) {
          parsed.repositories = []
        }
      } else {
        parsed.repositories = []
      }

      // 转换数字字段
      const numericFields = [
        'followers',
        'following',
        'org_repos_count',
        'org_total_stars',
        'org_total_contributions'
      ]
      
      numericFields.forEach(field => {
        if (parsed[field] !== undefined && parsed[field] !== null) {
          const num = parseInt(parsed[field], 10)
          parsed[field] = isNaN(num) ? 0 : num
        } else {
          parsed[field] = 0
        }
      })

      return parsed
    })
  }

  /**
   * 加载成员数据
   */
  async loadMembers() {
    const rawData = await this.loadData('members', 'data/members.json')
    return this.parseMemberData(rawData)
  }

  /**
   * 加载提交统计数据
   */
  async loadCommits() {
    return await this.loadData('commits', 'data/commits_weekly.json')
  }
  /**
   * 加载季度贡献者数据
   */
  async loadQuarterlyContributors() {
    return this.loadData('quarterlyContributors', 'data/quarterly_contributors.json')
  }

  /**
   * 加载项目数据
   */
  async loadProjects() {
    const data = await this.loadData('projects', 'data/datawhalechina/organization_datasource.json')
    return data?.projectInfo || []
  }

  /**
   * 加载组织数据
   */
  async loadOrganizations() {
    const data = await this.loadData('organizations', 'data/datawhalechina/organization_datasource.json')
    return data?.top10KnowledgeSharingOrganizationInfo || []
  }

  /**
   * 加载组织成员列表
   */
  async loadOrganizationMembers() {
    try {
      const data = await this.loadData('organizationMembers', 'data/datawhale_member.json')
      
      // 提取用户名集合
      const usernames = new Set()
      if (Array.isArray(data)) {
        data.forEach(item => {
          if (item.id && item.id.trim()) {
            usernames.add(item.id.trim())
          }
        })
      }
      
      return usernames
    } catch (error) {
      console.warn('Failed to load organization members, returning empty set:', error)
      return new Set()
    }
  }

  /**
   * 清除缓存
   */
  clearCache(cacheKey = null) {
    if (cacheKey) {
      this.cache[cacheKey] = null
    } else {
      Object.keys(this.cache).forEach(key => {
        this.cache[key] = null
      })
    }
  }

  /**
   * 预加载所有数据
   */
  async preloadAll() {
    try {
      await Promise.all([
        this.loadMembers(),
        this.loadCommits(),
        this.loadProjects(),
        this.loadOrganizations(),
        this.loadOrganizationMembers()
      ])
      console.log('All data preloaded successfully')
    } catch (error) {
      console.error('Failed to preload data:', error)
    }
  }
}

// 导出单例实例
export const dataSource = new DataSource()
