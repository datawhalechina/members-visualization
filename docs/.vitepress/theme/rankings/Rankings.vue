<template>
  <div class="rankings-container">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>正在加载榜单数据...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-state">
      <p>❌ 加载失败: {{ error }}</p>
      <button @click="loadData" class="retry-btn">重试</button>
    </div>

    <!-- 榜单内容 -->
    <div v-else class="rankings-content">
      <!-- 筛选器 -->
      <div class="filters-section">
        <div class="filter-group">
          <label>研究方向筛选：</label>
          <select v-model="selectedDomain" @change="applyFilters">
            <option value="">全部方向</option>
            <option v-for="domain in allDomains" :key="domain" :value="domain">
              {{ domain }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label>显示数量：</label>
          <select v-model="topCount" @change="applyFilters">
            <option :value="10">Top 10</option>
            <option :value="20">Top 20</option>
            <option :value="50">Top 50</option>
          </select>
        </div>

        <div class="filter-group checkbox-group">
          <label class="checkbox-label">
            <input type="checkbox" v-model="showOnlyOrgMembers" @change="applyFilters" class="checkbox-input" />
            <span class="checkbox-text">仅显示组织成员</span>
          </label>
        </div>

        <button v-if="selectedDomain || showOnlyOrgMembers" @click="clearFilters" class="clear-filters-btn">
          清除筛选
        </button>
      </div>

      <!-- 一周卷王榜（特殊位置） -->
      <div class="weekly-commits-section">
        <WeeklyCommitsCard :members-data="members" :selected-domain="selectedDomain" :top-count="topCount"
          :show-only-org-members="showOnlyOrgMembers" :organization-members="organizationMembers" />
      </div>

      <!-- 夜猫榜（特殊位置） -->
      <div class="night-owl-section">
        <NightOwlCard :members-data="members" :selected-domain="selectedDomain" :top-count="topCount"
          :show-only-org-members="showOnlyOrgMembers" :organization-members="organizationMembers" />
      </div>

      <!-- 榜单网格 -->
      <div class="leaderboards-grid">
        <LeaderboardCard v-for="leaderboard in leaderboards" :key="leaderboard.id" :title="leaderboard.title"
          :description="leaderboard.description" :icon="leaderboard.icon" :members="leaderboard.data"
          :color-scheme="leaderboard.colorScheme" :show-trend="leaderboard.showTrend" />
      </div>

      <!-- 数据更新时间和说明 -->
      <div class="update-info">
        <p>📅 数据最后更新时间：{{ lastUpdateTime }}</p>
        <p>🔄 下次更新时间：{{ nextUpdateTime }}</p>
      </div>


    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import LeaderboardCard from './LeaderboardCard.vue'
import WeeklyCommitsCard from './WeeklyCommitsCard.vue'
import NightOwlCard from './NightOwlCard.vue'
import { loadJSONOrganizationMembers, isOrganizationMember } from '../utils/index.js'
import { withBase } from 'vitepress'

// 响应式数据
const loading = ref(true)
const error = ref(null)
const members = ref([])
const commitsData = ref(null)
const selectedDomain = ref('')
const topCount = ref(20)
const showOnlyOrgMembers = ref(false)
const organizationMembers = ref(new Set())

// 计算属性
const allDomains = computed(() => {
  const domains = new Set()
  members.value.forEach(member => {
    if (member.domain) {
      member.domain.split(';').forEach(d => domains.add(d.trim()))
    }
  })
  return Array.from(domains).sort()
})

const filteredMembers = computed(() => {
  let filtered = members.value

  // 研究方向筛选
  if (selectedDomain.value) {
    filtered = filtered.filter(member =>
      member.domain && member.domain.includes(selectedDomain.value)
    )
  }

  // 组织成员筛选 - 使用内连接（INNER JOIN）逻辑
  if (showOnlyOrgMembers.value) {
    console.log(`🔍 组织成员筛选已启用`)
    console.log(`📋 组织成员名单大小: ${organizationMembers.value.size}`)
    console.log(`📊 筛选前成员总数: ${filtered.length}`)

    filtered = filtered.filter(member => {
      const isOrgMember = isOrganizationMember(member.id, organizationMembers.value)
      const hasAvatar = !!member.avatar
      const hasId = !!member.id
      const hasDomain = !!member.domain

      // 调试：打印前3个成员的筛选结果
      if (filtered.indexOf(member) < 3) {
        console.log(`  检查成员 ${member.id}:`, {
          isOrgMember,
          hasAvatar,
          hasId,
          hasDomain,
          passed: isOrgMember && hasAvatar && hasId && hasDomain
        })
      }

      // 双向存在性检查：
      // 1. 成员必须存在于组织成员名单中
      // 2. 成员必须在主数据中有完整信息
      return isOrgMember && hasAvatar && hasId && hasDomain
    })

    console.log(`✅ 筛选后成员总数: ${filtered.length}`)
  }

  return filtered
})

// 榜单配置
const leaderboards = computed(() => [
  {
    id: 'popularity',
    title: '人气王榜',
    description: '综合个人 Followers 和组织仓库 Stars 的影响力排行',
    icon: '👑',
    colorScheme: 'fire',
    showTrend: false,
    data: calculatePopularityRanking()
  },
  {
    id: 'productive',
    title: '多产榜',
    description: '基于参与组织仓库数量的贡献广度排行',
    icon: '🏆',
    colorScheme: 'blue',
    showTrend: false,
    data: calculateProductiveRanking()
  },
  {
    id: 'social',
    title: '社交达人榜',
    description: '基于 Following 数量的社交活跃度排行',
    icon: '💬',
    colorScheme: 'green',
    showTrend: false,
    data: calculateSocialRanking()
  },
  {
    id: 'rising',
    title: '新星榜',
    description: '基于组织贡献活跃度的潜力新星排行',
    icon: '🌠',
    colorScheme: 'purple',
    showTrend: false,
    data: calculateRisingStarRanking()
  },
  {
    id: 'comprehensive',
    title: '综合实力榜',
    description: '基于组织贡献的多维度综合评分排行',
    icon: '🌟',
    colorScheme: 'gold',
    showTrend: false,
    data: calculateComprehensiveRanking()
  }
])

// 时间信息
const lastUpdateTime = computed(() => {
  if (commitsData.value?.update_time) {
    return new Date(commitsData.value.update_time).toLocaleString('zh-CN')
  }
  return new Date().toLocaleString('zh-CN')
})

const nextUpdateTime = computed(() => {
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  tomorrow.setHours(6, 0, 0, 0) // 每天早上6点更新
  return tomorrow.toLocaleString('zh-CN')
})

// 排名计算函数
function calculatePopularityRanking() {
  // 使用组织贡献数据：followers（个人社交影响力）+ org_total_stars（组织仓库影响力）
  return filteredMembers.value
    .map(member => ({
      ...member,
      score: (member.followers || 0) * 0.6 + (member.org_total_stars || 0) * 0.4,
      scoreDisplay: `${member.followers || 0} followers + ${member.org_total_stars || 0} 组织stars`
    }))
    .filter(member => member.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, topCount.value)
    .map((member, index) => ({ ...member, rank: index + 1 }))
}

function calculateProductiveRanking() {
  // 使用组织贡献数据：参与的组织仓库数量
  return filteredMembers.value
    .map(member => ({
      ...member,
      score: member.org_repos_count || 0,
      scoreDisplay: `参与 ${member.org_repos_count || 0} 个组织仓库`
    }))
    .filter(member => member.score >= 1)
    .sort((a, b) => b.score - a.score)
    .slice(0, topCount.value)
    .map((member, index) => ({ ...member, rank: index + 1 }))
}

function calculateSocialRanking() {
  // 社交达人榜保持使用个人 following 数据（这是个人社交属性）
  return filteredMembers.value
    .map(member => ({
      ...member,
      score: member.following || 0,
      scoreDisplay: `关注 ${member.following || 0} 人`
    }))
    .filter(member => member.score >= 10)
    .sort((a, b) => b.score - a.score)
    .slice(0, topCount.value)
    .map((member, index) => ({ ...member, rank: index + 1 }))
}

function calculateRisingStarRanking() {
  // 使用组织贡献数据：基于组织仓库参与度和影响力的新星评分
  return filteredMembers.value
    .map(member => {
      const orgRepos = Math.max(member.org_repos_count || 1, 1)
      const activity = (member.followers || 0) + (member.org_total_stars || 0)
      const score = activity / orgRepos * (orgRepos < 5 ? 1.5 : 1) // 新人加成（参与少于5个组织仓库）

      return {
        ...member,
        score,
        scoreDisplay: `活跃度 ${Math.round(score)}`
      }
    })
    .filter(member => member.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, topCount.value)
    .map((member, index) => ({ ...member, rank: index + 1 }))
}

function calculateComprehensiveRanking() {
  // 使用组织贡献数据进行综合评分
  return filteredMembers.value
    .map(member => {
      const orgStars = (member.org_total_stars || 0) * 0.3  // 组织仓库stars影响力
      const followers = (member.followers || 0) * 0.25      // 个人社交影响力
      const orgRepos = (member.org_repos_count || 0) * 0.2  // 组织仓库参与度
      const following = (member.following || 0) * 0.15      // 社交活跃度
      const contributions = (member.org_total_contributions || 0) * 0.1  // 代码贡献量

      const score = orgStars + followers + orgRepos + following + contributions

      return {
        ...member,
        score,
        scoreDisplay: `综合分 ${Math.round(score)}`
      }
    })
    .filter(member => member.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, topCount.value)
    .map((member, index) => ({ ...member, rank: index + 1 }))
}

// 方法
const loadData = async () => {
  try {
    loading.value = true
    error.value = null

    const basePath = import.meta.env.BASE_URL || '/'
    const jsonPath = `${basePath}data/members.json`.replace(/\/+/g, '/')
    const commitsPath = `${basePath}data/commits_weekly.json`.replace(/\/+/g, '/')

    // 并行加载成员数据和commits数据
    const [membersResponse, commitsResponse] = await Promise.all([
      fetch(jsonPath),
      fetch(commitsPath)
    ])

    if (!membersResponse.ok) {
      throw new Error(`HTTP error! status: ${membersResponse.status}`)
    }

    const membersJSON = await membersResponse.json()
    members.value = membersJSON.map((item => {
      Object.keys(item).forEach((key) => {
        let value = item[key] || ''
        if (typeof value === 'string') {
          value = value.trim().replace(/^"|"$/g, '')
        }
        item[key] = value
      })
      return item
    }))

    // 加载commits数据（用于获取更新时间）
    if (commitsResponse.ok) {
      commitsData.value = await commitsResponse.json()
    }

    // 加载组织成员数据
    const orgMembersJSONPath = withBase('/data/datawhale_member.json')
    organizationMembers.value = await loadJSONOrganizationMembers(orgMembersJSONPath)

  } catch (err) {
    error.value = err.message
    console.error('加载数据失败:', err)
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  // 筛选逻辑已通过计算属性实现
}

const clearFilters = () => {
  selectedDomain.value = ''
  showOnlyOrgMembers.value = false
}

// 生命周期
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.rankings-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.loading-state,
.error-state {
  text-align: center;
  padding: 60px 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

.filters-section {
  background: var(--vp-c-bg-soft);
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 30px;
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  align-items: center;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-group label {
  font-weight: 500;
  color: var(--vp-c-text-1);
}

.filter-group select {
  padding: 8px 12px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  font-size: 14px;
}

/* 复选框样式 */
.checkbox-group {
  display: flex;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-weight: 500;
  color: var(--vp-c-text-1);
}

.checkbox-input {
  width: 16px;
  height: 16px;
  accent-color: var(--vp-c-brand-1);
  cursor: pointer;
}

.checkbox-text {
  user-select: none;
}

.clear-filters-btn,
.retry-btn {
  padding: 8px 16px;
  background: var(--vp-c-brand-1);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.clear-filters-btn:hover,
.retry-btn:hover {
  background: var(--vp-c-brand-2);
}

.weekly-commits-section {
  margin-bottom: 40px;
}

.night-owl-section {
  margin-bottom: 40px;
}

.leaderboards-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 30px;
  margin-bottom: 40px;
}

.update-info {
  text-align: center;
  padding: 20px;
  background: var(--vp-c-bg-soft);
  border-radius: 8px;
  color: var(--vp-c-text-2);
  font-size: 14px;
}

.update-info p {
  margin: 5px 0;
}



@media (max-width: 768px) {
  .rankings-container {
    padding: 15px;
  }

  .leaderboards-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .filters-section {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-group {
    justify-content: space-between;
  }
}
</style>
