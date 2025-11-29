/**
 * 工具函数
 */

/**
 * 解析CSV文件内容
 * @param {string} csvContent - CSV文件内容
 * @returns {Array} 解析后的数据数组
 */
export function parseCSV(csvContent) {
  // 移除 BOM（Byte Order Mark）如果存在
  let content = csvContent
  if (content.charCodeAt(0) === 0xFEFF) {
    content = content.slice(1)
  }

  const lines = content.trim().split('\n')
  if (lines.length < 2) return []

  // 解析表头，移除 BOM 和引号
  const headers = lines[0].split(',').map(h => h.trim().replace(/^["']|["']$/g, '').replace(/^\uFEFF/, ''))

  // 解析数据行
  const data = []
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim()
    if (!line) continue // 跳过空行

    // 简单的CSV解析（处理带引号的字段）
    const values = []
    let currentValue = ''
    let inQuotes = false

    for (let j = 0; j < line.length; j++) {
      const char = line[j]

      if (char === '"') {
        inQuotes = !inQuotes
      } else if (char === ',' && !inQuotes) {
        values.push(currentValue.trim())
        currentValue = ''
      } else {
        currentValue += char
      }
    }
    values.push(currentValue.trim()) // 添加最后一个值

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

  csvData.forEach((row, index) => {
    // 假设CSV中的'id'字段就是GitHub用户名
    if (row.id && row.id.trim()) {
      const username = row.id.trim()
      usernames.add(username)
      // 只打印前5个用户名作为示例
      if (index < 5) {
        console.log(`  - Extracted username: ${username}`)
      }
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
      // 如果JSON文件不存在，尝试加载CSV文件
      console.warn(`JSON file not found, trying CSV file instead`)
      const csvPath = jsonPath.replace('.json', '.csv')
      return await loadOrganizationMembers(csvPath)
    }

    const jsonData = await response.json()
    const usernames = extractGithubUsernames(jsonData)

    console.log(`Loaded ${usernames.size} organization members from JSON`)
    return usernames
  } catch (error) {
    console.error('Error loading organization members from JSON:', error)
    // 尝试降级到CSV文件
    try {
      const csvPath = jsonPath.replace('.json', '.csv')
      console.log(`Falling back to CSV file: ${csvPath}`)
      return await loadOrganizationMembers(csvPath)
    } catch (csvError) {
      console.error('Error loading organization members from CSV:', csvError)
      return new Set() // 返回空集合，不影响正常功能
    }
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
