<template>
  <div class="night-owl-card leaderboard-card-base" :class="`theme-night`">
    <!-- 卡片头部 -->
    <div class="card-header card-header-base">
      <div class="title-section title-section-base">
        <span class="icon icon-base animated-moon">🌙</span>
        <div>
          <h3 class="title title-base">夜猫榜</h3>
          <p class="description description-base">深夜时段（22:00-06:00）代码提交活跃度排行</p>
        </div>
      </div>
      <div class="stats-badge">
        <span class="count">{{ validMembers.length }}</span>
        <span class="label">夜猫子</span>
      </div>
    </div>

    <!-- 更新信息 -->
    <div class="update-info-section">
      <div class="time-info">
        <span class="time-label">🌃 最近7天深夜活动数据</span>
        <span class="update-time">{{ lastUpdateTime }}</span>
      </div>
    </div>

    <!-- 榜单内容 -->
    <div class="leaderboard-content">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>正在加载夜猫数据...</p>
      </div>
      
      <div v-else-if="error" class="error-state">
        <p>❌ {{ error }}</p>
        <button @click="loadCommitsData" class="retry-btn">重试</button>
      </div>
      
      <div v-else-if="validMembers.length === 0" class="empty-state">
        <div class="empty-icon">😴</div>
        <p v-if="showOnlyOrgMembers">组织成员本周暂无深夜提交活动</p>
        <p v-else>本周暂无深夜提交活动</p>
        <p class="empty-hint" v-if="showOnlyOrgMembers">组织成员们早睡早起身体好！</p>
        <p class="empty-hint" v-else>早睡早起身体好！</p>
      </div>
      
      <div v-else class="commits-list">
        <NightOwlItem
          v-for="(member, index) in displayMembers"
          :key="member.user_key"
          :member="member"
          :rank="index + 1"
          :animation-delay="index * 100"
          :show-details="activeDetailsUser === member.user_key"
          @toggle-details="handleToggleDetails"
        />
      </div>
    </div>

    <!-- 卡片底部 -->
    <div class="card-footer" v-if="validMembers.length > 0">
      <div class="ranking-info">
        <span>夜猫王：{{ validMembers[0]?.display_name }}</span>
        <span>总深夜commit数：{{ totalNightOwlCommits }}</span>
      </div>
      
      <button 
        v-if="validMembers.length > 5"
        @click="toggleExpanded" 
        class="expand-btn"
      >
        {{ isExpanded ? '收起' : '查看更多' }}
        <span class="arrow" :class="{ expanded: isExpanded }">▼</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import NightOwlItem from './NightOwlItem.vue'
import { isOrganizationMember } from '../utils/index.js'

// Props
const props = defineProps({
  membersData: {
    type: Array,
    default: () => []
  },
  selectedDomain: {
    type: String,
    default: ''
  },
  topCount: {
    type: Number,
    default: 20
  },
  showOnlyOrgMembers: {
    type: Boolean,
    default: false
  },
  organizationMembers: {
    type: Set,
    default: () => new Set()
  }
})

// 响应式数据
const loading = ref(false)
const error = ref(null)
const commitsData = ref(null)
const activeDetailsUser = ref(null)
const isExpanded = ref(false)

// 计算属性
const validMembers = computed(() => {
  if (!commitsData.value?.user_commits) return []

  const members = []
  let debugCount = 0

  for (const [userKey, stats] of Object.entries(commitsData.value.user_commits)) {
    // 过滤条件：至少1个深夜commit
    if (stats.night_owl_commits >= 1) {
      // 从membersData中查找对应的成员信息 - 内连接第一步：必须在主数据中存在
      const memberInfo = props.membersData.find(m => m.id === userKey)

      // 内连接第二步：如果启用组织成员筛选，必须同时满足以下条件：
      // 1. 在主数据中存在 (memberInfo)
      // 2. 在组织成员名单中存在
      // 3. 有实际的深夜commit活动数据
      if (props.showOnlyOrgMembers) {
        const hasMemberInfo = !!memberInfo
        const isOrgMember = isOrganizationMember(userKey, props.organizationMembers)

        // 调试：打印前3个用户的筛选结果
        if (debugCount < 3) {
          console.log(`🌙 深夜猫头鹰榜 - 检查用户 ${userKey}:`, {
            hasMemberInfo,
            isOrgMember,
            hasAvatar: memberInfo?.avatar,
            passed: hasMemberInfo && isOrgMember
          })
          debugCount++
        }

        if (!memberInfo || !isOrgMember) {
          continue // 跳过不满足内连接条件的成员
        }
      }

      const member = {
        user_key: userKey,
        // 添加原始字段供组件内部使用
        id: memberInfo?.id || userKey,
        name: memberInfo?.name || null,
        display_name: extractDisplayName(userKey, memberInfo),
        github_username: extractGithubUsername(userKey),
        // 头像
        avatar: memberInfo?.avatar || null,
        // 基础资料（与人气王一致）
        location: memberInfo?.location || null,
        company: memberInfo?.company || null,
        domain: memberInfo?.domain || '',
        // 人气与仓库统计（字段兼容多种命名）
        followers: (memberInfo?.followers ?? memberInfo?.followers_count ?? 0),
        total_stars: (memberInfo?.total_stars ?? memberInfo?.stars ?? 0),
        public_repos: (memberInfo?.public_repos ?? memberInfo?.repo_count ?? 0),
        // 业务统计
        ...stats,
        // 计算夜猫分数
        night_owl_score: calculateNightOwlScore(stats)
      }

      // 根据研究方向筛选
      if (props.selectedDomain) {
        if (memberInfo && memberInfo.domain && memberInfo.domain.includes(props.selectedDomain)) {
          members.push(member)
        }
      } else {
        members.push(member)
      }
    }
  }

  // 按夜猫分数排序
  return members.sort((a, b) => b.night_owl_score - a.night_owl_score)
})

const displayMembers = computed(() => {
  const count = isExpanded.value ? props.topCount : Math.min(5, props.topCount)
  return validMembers.value.slice(0, count)
})

const totalNightOwlCommits = computed(() => {
  return validMembers.value.reduce((sum, member) => sum + member.night_owl_commits, 0)
})

const lastUpdateTime = computed(() => {
  if (!commitsData.value?.update_time) return '未知'
  
  try {
    const date = new Date(commitsData.value.update_time)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (e) {
    return '未知'
  }
})

// 工具函数
const extractDisplayName = (userKey, memberInfo) => {
  // 优先使用memberInfo中的name字段
  if (memberInfo?.name && memberInfo.name !== 'null' && memberInfo.name !== 'undefined' && memberInfo.name !== 'None' && memberInfo.name.trim() !== '') {
    return memberInfo.name
  }

  // 如果name为空，使用memberInfo中的id字段
  if (memberInfo?.id) {
    return memberInfo.id
  }

  // 最后回退到从userKey提取
  if (userKey.includes('@')) {
    return userKey.split('@')[0]
  }
  return userKey
}

const extractGithubUsername = (userKey) => {
  if (userKey.includes('@')) {
    return userKey.split('@')[0]
  }
  return userKey
}

const calculateNightOwlScore = (stats) => {
  let score = 0
  
  // 基础分：每个深夜commit = 2分（比普通commit更有价值）
  score += stats.night_owl_commits * 2
  
  // 深夜比例奖励
  const nightOwlPercentage = stats.night_owl_percentage || 0
  if (nightOwlPercentage >= 50) {
    score += 10 // 超过50%深夜提交
  } else if (nightOwlPercentage >= 30) {
    score += 5  // 超过30%深夜提交
  } else if (nightOwlPercentage >= 20) {
    score += 2  // 超过20%深夜提交
  }
  
  // 连续性奖励：深夜活跃天数
  const activeDays = stats.active_days || 0
  if (activeDays >= 5) {
    score += 8 // 连续5天以上有深夜提交
  } else if (activeDays >= 3) {
    score += 4 // 连续3天以上有深夜提交
  }
  
  // 多仓库深夜工作奖励
  const repoCount = stats.repo_count || 0
  if (repoCount >= 3) {
    score += 3
  } else if (repoCount >= 2) {
    score += 1
  }
  
  return Math.round(score)
}

// 处理详情弹窗切换
const handleToggleDetails = (userKey) => {
  if (activeDetailsUser.value === userKey) {
    activeDetailsUser.value = null // 关闭当前弹窗
  } else {
    activeDetailsUser.value = userKey // 打开新弹窗，自动关闭其他
  }
}

const loadCommitsData = async () => {
  try {
    loading.value = true
    error.value = null
    
    const basePath = import.meta.env.BASE_URL || '/'
    const commitsPath = `${basePath}data/commits_weekly.json`.replace(/\/+/g, '/')
    
    const response = await fetch(commitsPath)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    commitsData.value = await response.json()
    
  } catch (err) {
    error.value = err.message
    console.error('加载commit数据失败:', err)
  } finally {
    loading.value = false
  }
}

const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}

// 生命周期
onMounted(() => {
  loadCommitsData()
})
</script>

<style scoped>
/* 夜猫榜特有样式 - 基础样式由 leaderboard-card-base 提供 */
.night-owl-card {
  /* 移除顶部彩色边框，与其他榜单保持一致 */
  margin-top: 24px;
}

/* 夜猫榜特有悬停效果 - 基础悬停由 leaderboard-card-base 提供 */
.night-owl-card:hover {
  box-shadow: 0 8px 25px rgba(99, 102, 241, 0.2) !important;
}

/* 夜猫榜特有头部样式 - 基础样式由 card-header-base 提供 */
.card-header {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, var(--vp-c-bg-soft) 100%) !important;
}

.title-section {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.icon {
  font-size: 24px;
  line-height: 1;
}

.animated-moon {
  animation: moonGlow 3s ease-in-out infinite alternate;
}

@keyframes moonGlow {
  0% { 
    transform: scale(1);
    filter: brightness(1);
  }
  100% { 
    transform: scale(1.1);
    filter: brightness(1.3);
  }
}

.title {
  margin: 0 0 4px 0;
  font-size: 20px;
  font-weight: 700;
  color: var(--vp-c-text-1);
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.description {
  margin: 0;
  font-size: 13px;
  color: var(--vp-c-text-2);
  line-height: 1.4;
}

.stats-badge {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  text-align: center;
  min-width: 60px;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
}

.stats-badge .count {
  display: block;
  font-size: 18px;
  font-weight: 700;
  line-height: 1;
}

.stats-badge .label {
  display: block;
  font-size: 11px;
  opacity: 0.9;
  margin-top: 2px;
}

.update-info-section {
  padding: 12px 20px;
  background: var(--vp-c-bg-soft);
  border-bottom: 1px solid var(--vp-c-divider);
}

.time-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: var(--vp-c-text-2);
}

.time-label {
  font-weight: 500;
}

.update-time {
  opacity: 0.8;
}

.leaderboard-content {
  padding: 16px 20px;
  min-height: 200px;
}

.loading-state, .error-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--vp-c-divider);
  border-top: 3px solid #6366f1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.6;
}

.empty-hint {
  font-size: 12px;
  color: var(--vp-c-text-2);
  margin-top: 8px;
}

.commits-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 0;
}

.card-footer {
  padding: 16px 20px;
  background: var(--vp-c-bg-soft);
  border-top: 1px solid var(--vp-c-divider);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ranking-info {
  display: flex;
  gap: 24px;
  font-size: 13px;
  color: var(--vp-c-text-2);
}

.ranking-info span {
  font-weight: 500;
}

.expand-btn {
  background: none;
  border: 1px solid var(--vp-c-divider);
  color: var(--vp-c-text-1);
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 4px;
}

.expand-btn:hover {
  background: var(--vp-c-bg-elv);
  border-color: #6366f1;
}

.arrow {
  transition: transform 0.2s ease;
  font-size: 10px;
}

.arrow.expanded {
  transform: rotate(180deg);
}

.retry-btn {
  background: #6366f1;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  margin-top: 12px;
  transition: background 0.2s ease;
}

.retry-btn:hover {
  background: #5855eb;
}
</style>
