<script setup>
import { ref, computed, onMounted } from 'vue'
import { BADGE_DEFINITIONS, ALL_ROUNDER_DEF, TIER_COLORS, computeMemberBadges } from '../utils/badges.js'
import { loadMembers, loadCommitsWeekly } from '../utils/dataLoader.js'

const loading = ref(true)
const error = ref(null)
const members = ref([])
const selectedCategory = ref('')
const expandedTier = ref(null) // 'badgeId-tier'

// 合并 night_owl 数据到 members
function mergeCommitsData(membersArr, commitsData) {
  if (!commitsData?.user_commits) return membersArr
  return membersArr.map(m => ({
    ...m,
    night_owl_percentage: commitsData.user_commits[m.id]?.night_owl_percentage || 0,
  }))
}

// 所有徽章定义（含全能选手）
const allDefs = computed(() => [...BADGE_DEFINITIONS, ALL_ROUNDER_DEF])

// 每个成员的徽章
const memberBadgesMap = computed(() => {
  const map = new Map()
  members.value.forEach(m => map.set(m.id, computeMemberBadges(m)))
  return map
})

// 每个徽章类别的统计：{ badgeId: { gold: [member...], silver: [...], bronze: [...] } }
const badgeStats = computed(() => {
  const stats = {}
  allDefs.value.forEach(d => { stats[d.id] = { gold: [], silver: [], bronze: [] } })
  for (const [memberId, badges] of memberBadgesMap.value) {
    const member = members.value.find(m => m.id === memberId)
    for (const badge of badges) {
      if (stats[badge.id]?.[badge.tier]) {
        stats[badge.id][badge.tier].push({ ...member, badgeValue: badge.formatted })
      }
    }
  }
  return stats
})

// 总统计
const totalStats = computed(() => {
  let totalBadges = 0
  const membersWithBadges = new Set()
  for (const [memberId, badges] of memberBadgesMap.value) {
    totalBadges += badges.length
    if (badges.length > 0) membersWithBadges.add(memberId)
  }
  // 最稀有徽章
  let rarestBadge = null
  let rarestCount = Infinity
  for (const def of allDefs.value) {
    const s = badgeStats.value[def.id]
    const total = (s?.gold?.length || 0) + (s?.silver?.length || 0) + (s?.bronze?.length || 0)
    if (total > 0 && total < rarestCount) {
      rarestCount = total
      rarestBadge = def
    }
  }
  return { totalBadges, membersWithBadges: membersWithBadges.size, rarestBadge, rarestCount }
})

// 筛选后的徽章定义
const filteredDefs = computed(() => {
  if (!selectedCategory.value) return allDefs.value
  return allDefs.value.filter(d => d.id === selectedCategory.value)
})

function toggleTier(badgeId, tier) {
  const key = `${badgeId}-${tier}`
  expandedTier.value = expandedTier.value === key ? null : key
}

function getTierMembers(badgeId, tier) {
  return badgeStats.value[badgeId]?.[tier] || []
}

function getAvatarUrl(member) {
  if (member.avatar && member.avatar.startsWith('avatars/')) {
    const basePath = import.meta.env.BASE_URL || '/'
    return `${basePath}${member.avatar}`.replace(/\/+/g, '/')
  }
  return member.avatar || `https://github.com/${member.id}.png`
}

onMounted(async () => {
  try {
    const [membersData, commitsData] = await Promise.all([loadMembers(), loadCommitsWeekly()])
    members.value = mergeCommitsData(membersData, commitsData)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="badge-gallery">
    <div v-if="loading" class="status-box loading"><p>正在加载数据...</p></div>
    <div v-else-if="error" class="status-box error"><p>加载失败: {{ error }}</p></div>
    <div v-else>
      <!-- 统计卡片 -->
      <div class="stats-row">
        <div class="stat-card">
          <div class="stat-number">{{ totalStats.totalBadges }}</div>
          <div class="stat-label">徽章总数</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ totalStats.membersWithBadges }}</div>
          <div class="stat-label">获徽章成员</div>
        </div>
        <div class="stat-card" v-if="totalStats.rarestBadge">
          <div class="stat-number">{{ totalStats.rarestBadge.icon }}</div>
          <div class="stat-label">最稀有: {{ totalStats.rarestBadge.name }} ({{ totalStats.rarestCount }}人)</div>
        </div>
      </div>

      <!-- 筛选 -->
      <div class="filter-bar">
        <label class="filter-label">筛选类别</label>
        <select v-model="selectedCategory" class="filter-select">
          <option value="">全部徽章</option>
          <option v-for="d in allDefs" :key="d.id" :value="d.id">{{ d.icon }} {{ d.name }}</option>
        </select>
      </div>

      <!-- 徽章卡片网格 -->
      <div class="badge-grid">
        <div v-for="def in filteredDefs" :key="def.id" class="badge-card">
          <div class="badge-icon">{{ def.icon }}</div>
          <div class="badge-name">{{ def.name }}</div>
          <div class="badge-desc">{{ def.description }}</div>
          <div class="tier-list">
            <div
              v-for="tier in (def.tiers || [])"
              :key="tier.level"
              class="tier-row"
              :class="{ expanded: expandedTier === `${def.id}-${tier.level}` }"
              @click="toggleTier(def.id, tier.level)"
            >
              <div class="tier-header">
                <span class="tier-dot" :style="{ background: TIER_COLORS[tier.level] }"></span>
                <span class="tier-label">{{ tier.label }}</span>
                <span class="tier-threshold">≥ {{ tier.threshold }}</span>
                <span class="tier-count">{{ getTierMembers(def.id, tier.level).length }} 人</span>
                <span class="tier-arrow">{{ expandedTier === `${def.id}-${tier.level}` ? '▾' : '▸' }}</span>
              </div>
              <div v-if="expandedTier === `${def.id}-${tier.level}`" class="tier-members" @click.stop>
                <div v-if="getTierMembers(def.id, tier.level).length === 0" class="no-members">暂无成员</div>
                <div v-for="m in getTierMembers(def.id, tier.level).slice(0, 20)" :key="m.id" class="member-row">
                  <img :src="getAvatarUrl(m)" :alt="m.name || m.id" class="member-avatar" loading="lazy" />
                  <a :href="m.github || `https://github.com/${m.id}`" target="_blank" class="member-name">{{ m.name || m.id }}</a>
                  <span class="member-value">{{ m.badgeValue }}</span>
                </div>
                <div v-if="getTierMembers(def.id, tier.level).length > 20" class="more-hint">
                  还有 {{ getTierMembers(def.id, tier.level).length - 20 }} 位成员...
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.badge-gallery { width: 100%; padding: 20px 0; }

.status-box {
  text-align: center; padding: 60px 20px; border-radius: 12px;
  margin: 20px 0; background: var(--vp-c-bg-soft); border: 1px solid var(--vp-c-border);
}
.status-box.loading { border-color: var(--vp-c-brand-1); color: var(--vp-c-brand-1); }
.status-box.error { border-color: var(--vp-c-danger-1); color: var(--vp-c-danger-1); }

.stats-row { display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }
.stat-card {
  flex: 1 1 140px; text-align: center; padding: 20px 16px; border-radius: 12px;
  background: var(--vp-c-bg-soft); border: 1px solid var(--vp-c-border); min-width: 0;
}
.stat-number { font-size: 28px; font-weight: 700; color: var(--vp-c-brand-1); overflow: hidden; text-overflow: ellipsis; }
.stat-label { font-size: 13px; color: var(--vp-c-text-2); margin-top: 4px; overflow: hidden; text-overflow: ellipsis; }

.filter-bar {
  display: flex; align-items: center; gap: 12px; margin-bottom: 24px;
  padding: 16px 20px; background: var(--vp-c-bg-soft); border-radius: 12px;
  border: 1px solid var(--vp-c-border);
}
.filter-label { font-size: 14px; color: var(--vp-c-text-1); white-space: nowrap; }
.filter-select {
  flex: 1; max-width: 300px; padding: 8px 12px; border: 2px solid var(--vp-c-border);
  border-radius: 8px; font-size: 14px; background: var(--vp-c-bg); color: var(--vp-c-text-1);
  cursor: pointer;
}
.filter-select:focus { outline: none; border-color: var(--vp-c-brand-1); }

.badge-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px;
}

.badge-card {
  background: var(--vp-c-bg); border: 1px solid var(--vp-c-border); border-radius: 12px;
  padding: 24px; transition: transform 0.2s, box-shadow 0.2s;
}
.badge-card:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,0.08); }

.badge-icon { font-size: 48px; text-align: center; margin-bottom: 8px; }
.badge-name { font-size: 18px; font-weight: 700; text-align: center; color: var(--vp-c-text-1); }
.badge-desc { font-size: 13px; color: var(--vp-c-text-2); text-align: center; margin: 4px 0 16px; }

.tier-list { display: flex; flex-direction: column; gap: 4px; }
.tier-row { cursor: pointer; border-radius: 8px; transition: background 0.15s; }
.tier-row:hover { background: var(--vp-c-bg-soft); }

.tier-header {
  display: flex; align-items: center; gap: 8px; padding: 8px 10px; font-size: 13px;
}
.tier-dot { width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }
.tier-label { font-weight: 600; color: var(--vp-c-text-1); min-width: 32px; }
.tier-threshold { color: var(--vp-c-text-2); }
.tier-count { margin-left: auto; color: var(--vp-c-brand-1); font-weight: 600; }
.tier-arrow { color: var(--vp-c-text-3); font-size: 11px; }

.tier-members {
  padding: 8px 10px 12px; max-height: 300px; overflow-y: auto;
  border-top: 1px solid var(--vp-c-border);
}
.member-row {
  display: flex; align-items: center; gap: 8px; padding: 6px 0;
  border-bottom: 1px solid var(--vp-c-divider);
}
.member-row:last-child { border-bottom: none; }
.member-avatar { width: 28px; height: 28px; border-radius: 50%; object-fit: cover; }
.member-name {
  font-size: 13px; color: var(--vp-c-brand-1); text-decoration: none; flex: 1;
}
.member-name:hover { text-decoration: underline; }
.member-value { font-size: 12px; color: var(--vp-c-text-2); white-space: nowrap; }
.no-members { font-size: 13px; color: var(--vp-c-text-3); text-align: center; padding: 8px; }
.more-hint { font-size: 12px; color: var(--vp-c-text-3); text-align: center; padding: 8px 0; }

@media (max-width: 768px) {
  .stats-row { flex-direction: column; gap: 12px; }
  .badge-grid { grid-template-columns: 1fr; }
  .filter-bar { flex-direction: column; align-items: stretch; }
  .filter-select { max-width: none; }
}
</style>
