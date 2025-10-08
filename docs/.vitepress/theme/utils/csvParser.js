/**
 * CSV解析工具函数
 * 用于解析组织成员CSV文件
 */

/**
 * 解析CSV文件内容
 * @param {string} csvContent - CSV文件内容
 * @returns {Array} 解析后的数据数组
 */
export function parseCSV(csvContent) {
  const lines = csvContent.trim().split('\n')
  if (lines.length < 2) return []

  // 解析表头
  const headers = lines[0].split(',').map(h => h.trim())

  // 解析数据行
  const data = []
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim()
    if (!line) continue // 跳过空行

    const values = line.split(',').map(v => v.trim())
    const row = {}

    headers.forEach((header, index) => {
      row[header] = values[index] || ''
    })

    data.push(row)
  }

  return data
}

/**
 * 从CSV数据中提取GitHub用户名列表
 * @param {Array} csvData - 解析后的CSV数据
 * @returns {Set} GitHub用户名集合
 */
export function extractGithubUsernames(csvData) {
  const usernames = new Set()

  csvData.forEach(row => {
    // 假设CSV中的'id'字段就是GitHub用户名
    if (row.id && row.id.trim()) {
      usernames.add(row.id.trim())
    }
  })

  return usernames
}



/**
 * 异步加载并解析组织成员CSV文件
 * @param {string} csvPath - CSV文件路径
 * @returns {Promise<Set>} GitHub用户名集合
 */
export async function loadOrganizationMembers(csvPath = '/data/datawhale_member.csv') {
  try {
    console.log(`Loading organization members from: ${csvPath}`)

    const response = await fetch(csvPath)
    if (!response.ok) {
      throw new Error(`Failed to fetch CSV: ${response.status}`)
    }

    const csvContent = await response.text()
    const csvData = parseCSV(csvContent)
    const usernames = extractGithubUsernames(csvData)

    console.log(`Loaded ${usernames.size} organization members from CSV`)
    return usernames
  } catch (error) {
    console.error('Error loading organization members:', error)
    return new Set() // 返回空集合，不影响正常功能
  }
}


/**
 * 异步加载并解析组织成员JSON文件
 * @param {string} jsonPath - JSON文件路径
 * @returns {Promise<Set>} GitHub用户名集合
 */
export async function loadJSONOrganizationMembers(jsonPath = '/data/datawhale_member.json') {
  try {
    console.log(`Loading organization members from: ${jsonPath}`)

    const response = await fetch(jsonPath)
    if (!response.ok) {
      throw new Error(`Failed to fetch json: ${response.status}`)
    }

    const jsonData = await response.json()
    const usernames = extractGithubUsernames(jsonData)

    console.log(`Loaded ${usernames.size} organization members from JSON`)
    return usernames
  } catch (error) {
    console.error('Error loading organization members:', error)
    return new Set() // 返回空集合，不影响正常功能
  }
}

/**
 * 检查用户是否为组织成员
 * @param {string} username - GitHub用户名
 * @param {Set} organizationMembers - 组织成员用户名集合
 * @returns {boolean} 是否为组织成员
 */
export function isOrganizationMember(username, organizationMembers) {
  if (!username || !organizationMembers) return false
  return organizationMembers.has(username)
}
