/**
 * 徽章定义与计算模块
 * 纯函数，无 Vue 依赖，可在任意组件中导入
 */

export const BADGE_DEFINITIONS = [
  {
    id: 'starCollector',
    name: 'Star 收割机',
    icon: '🌟',
    description: '组织仓库获得大量 Stars',
    field: 'org_total_stars',
    tiers: [
      { level: 'gold', label: '金牌', threshold: 100000 },
      { level: 'silver', label: '银牌', threshold: 50000 },
      { level: 'bronze', label: '铜牌', threshold: 10000 },
    ],
    compute: (m) => Number(m.org_total_stars) || 0,
    format: (v) => v >= 10000 ? `${(v / 10000).toFixed(1)}w` : String(v),
  },
  {
    id: 'prolificContributor',
    name: '高产贡献者',
    icon: '🔥',
    description: '组织仓库贡献次数突出',
    field: 'org_total_contributions',
    tiers: [
      { level: 'gold', label: '金牌', threshold: 500 },
      { level: 'silver', label: '银牌', threshold: 200 },
      { level: 'bronze', label: '铜牌', threshold: 50 },
    ],
    compute: (m) => Number(m.org_total_contributions) || 0,
    format: (v) => String(v),
  },
  {
    id: 'multiProject',
    name: '多面手',
    icon: '📦',
    description: '参与多个组织仓库',
    field: 'org_repos_count',
    tiers: [
      { level: 'gold', label: '金牌', threshold: 10 },
      { level: 'silver', label: '银牌', threshold: 5 },
      { level: 'bronze', label: '铜牌', threshold: 3 },
    ],
    compute: (m) => Number(m.org_repos_count) || 0,
    format: (v) => `${v} 个仓库`,
  },
  {
    id: 'communityInfluencer',
    name: '社区影响力',
    icon: '👥',
    description: '拥有大量 GitHub 关注者',
    field: 'followers',
    tiers: [
      { level: 'gold', label: '金牌', threshold: 500 },
      { level: 'silver', label: '银牌', threshold: 200 },
      { level: 'bronze', label: '铜牌', threshold: 50 },
    ],
    compute: (m) => Number(m.followers) || 0,
    format: (v) => String(v),
  },
  {
    id: 'domainExpert',
    name: '领域专家',
    icon: '🎯',
    description: '涉猎多个研究方向',
    field: 'domain',
    tiers: [
      { level: 'gold', label: '金牌', threshold: 8 },
      { level: 'silver', label: '银牌', threshold: 5 },
      { level: 'bronze', label: '铜牌', threshold: 3 },
    ],
    compute: (m) => {
      if (Array.isArray(m.domain)) return m.domain.length
      if (typeof m.domain === 'string' && m.domain) return m.domain.split(';').filter(d => d.trim()).length
      return 0
    },
    format: (v) => `${v} 个方向`,
  },
  {
    id: 'nightOwl',
    name: '夜猫子',
    icon: '🦉',
    description: '深夜代码提交比例高',
    field: 'night_owl_percentage',
    tiers: [
      { level: 'gold', label: '金牌', threshold: 70 },
      { level: 'silver', label: '银牌', threshold: 50 },
      { level: 'bronze', label: '铜牌', threshold: 30 },
    ],
    compute: (m) => Number(m.night_owl_percentage) || 0,
    format: (v) => `${v.toFixed(0)}%`,
  },
]

/**
 * 计算单个成员的所有徽章
 * @returns {{ id, icon, name, tier, tierLabel, value, formatted }[]}
 */
export function computeMemberBadges(member) {
  const badges = []
  for (const def of BADGE_DEFINITIONS) {
    const value = def.compute(member)
    for (const tier of def.tiers) {
      if (value >= tier.threshold) {
        badges.push({
          id: def.id,
          icon: def.icon,
          name: def.name,
          tier: tier.level,
          tierLabel: tier.label,
          value,
          formatted: def.format(value),
        })
        break
      }
    }
  }
  // 全能选手：在 4+ 个不同类别获得徽章
  const categories = new Set(badges.map(b => b.id))
  if (categories.size >= 4) {
    const level = categories.size >= 6 ? 'gold' : categories.size >= 5 ? 'silver' : 'bronze'
    const label = level === 'gold' ? '金牌' : level === 'silver' ? '银牌' : '铜牌'
    badges.push({
      id: 'allRounder',
      icon: '🏆',
      name: '全能选手',
      tier: level,
      tierLabel: label,
      value: categories.size,
      formatted: `${categories.size} 个类别`,
    })
  }
  return badges
}

/** 全能选手的定义信息（用于展示） */
export const ALL_ROUNDER_DEF = {
  id: 'allRounder',
  name: '全能选手',
  icon: '🏆',
  description: '在多个类别获得徽章的全面型选手',
  tiers: [
    { level: 'gold', label: '金牌', threshold: 6 },
    { level: 'silver', label: '银牌', threshold: 5 },
    { level: 'bronze', label: '铜牌', threshold: 4 },
  ],
  format: (v) => `${v} 个类别`,
}

/** 等级颜色映射 */
export const TIER_COLORS = {
  gold: '#ffd700',
  silver: '#c0c0c0',
  bronze: '#cd7f32',
}
