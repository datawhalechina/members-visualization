/**
 * 共享数据加载工具
 * 消除各组件中重复的 fetch + 解析逻辑
 */

function getBasePath() {
  return (import.meta.env.BASE_URL || '/').replace(/\/+$/, '')
}

/**
 * 加载并解析 members.json
 * 自动处理：trim、去引号、分号分割 domain/repositories
 */
export async function loadMembers() {
  const basePath = getBasePath()
  const jsonPath = `${basePath}/data/members.json`
  const res = await fetch(jsonPath)
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`)
  const raw = await res.json()
  return raw.map(item => {
    const cleaned = { ...item }
    for (const key of Object.keys(cleaned)) {
      let value = cleaned[key] || ''
      if (typeof value === 'string') {
        value = value.trim().replace(/^"|"$/g, '')
      }
      if (['domain', 'repositories'].includes(key)) {
        cleaned[key] = value ? value.split(';').map(d => d.trim()).filter(Boolean) : []
      } else {
        cleaned[key] = value
      }
    }
    return cleaned
  })
}

/**
 * 加载 commits_weekly.json
 */
export async function loadCommitsWeekly() {
  const basePath = getBasePath()
  const jsonPath = `${basePath}/data/commits_weekly.json`
  const res = await fetch(jsonPath)
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`)
  return res.json()
}
