<template>
  <div class="weekly-commits-card leaderboard-card-base" :class="`theme-fire`">
    <!-- 卡片头部 -->
    <div class="card-header card-header-base">
      <div class="title-section title-section-base">
        <span class="icon icon-base animated-fire">🔥</span>
        <div>
          <h3 class="title title-base">一周卷王榜</h3>
          <p class="description description-base">基于最近7天commit活动的超级卷王排行</p>
        </div>
      </div>
      <div class="stats-badge">
        <span class="count">{{ validMembers.length }}</span>
        <span class="label">大卷王</span>
      </div>
    </div>

    <!-- 更新信息 -->
    <div class="update-info-section">
      <div class="time-info">
        <span class="time-label">📅 最近7天活跃数据</span>
        <span class="update-time">{{ lastUpdateTime }}</span>
      </div>
    </div>

    <!-- 榜单内容 -->
    <div class="leaderboard-content">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>正在加载commit数据...</p>
      </div>
      
      <div v-else-if="error" class="error-state">
        <p>❌ {{ error }}</p>
        <button @click="loadCommitsData" class="retry-btn">重试</button>
      </div>
      
      <div v-else-if="validMembers.length === 0" class="empty-state">
        <div class="empty-icon">😴</div>
        <p v-if="showOnlyOrgMembers">组织成员本周暂无commit活动</p>
        <p v-else>本周暂无commit活动</p>
        <p class="empty-hint" v-if="showOnlyOrgMembers">组织成员们快去写代码吧！</p>
        <p class="empty-hint" v-else>快去写代码吧！</p>
      </div>
      
      <div v-else class="commits-list">
        <WeeklyCommitItem
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
        <span>🏆 本周卷王：{{ validMembers[0]?.display_name }}</span>
        <span>📊 总commit数：{{ totalCommits }}</span>
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
import WeeklyCommitItem from './WeeklyCommitItem.vue'
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
const loading = ref(true)
const error = ref(null)
const commitsData = ref(null)
const isExpanded = ref(false)
const activeDetailsUser = ref(null) // 当前显示详情的用户

// 计算属性
const validMembers = computed(() => {
  if (!commitsData.value?.user_commits) return []

  const members = []
  let debugCount = 0

  for (const [userKey, stats] of Object.entries(commitsData.value.user_commits)) {
    // 过滤条件：至少1个commit
    if (stats.total_commits >= 1) {
      // 从membersData中查找对应的成员信息 - 内连接第一步：必须在主数据中存在
      const memberInfo = props.membersData.find(m => m.id === userKey)

      // 内连接第二步：如果启用组织成员筛选，必须同时满足以下条件：
      // 1. 在主数据中存在 (memberInfo)
      // 2. 在组织成员名单中存在
      // 3. 有实际的commit活动数据
      if (props.showOnlyOrgMembers) {
        const hasMemberInfo = !!memberInfo
        const isOrgMember = isOrganizationMember(userKey, props.organizationMembers)

        // 调试：打印前3个用户的筛选结果
        if (debugCount < 3) {
          console.log(`🔥 一周卷王榜 - 检查用户 ${userKey}:`, {
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
        // 计算卷王分数
        score: calculateRollKingScore(stats)
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

  // 按分数排序，然后根据topCount限制数量
  const sorted = members.sort((a, b) => b.score - a.score)
  return sorted.slice(0, props.topCount)
})

const displayMembers = computed(() => {
  // 如果展开，显示所有筛选后的成员；否则只显示前5名
  return isExpanded.value ? validMembers.value : validMembers.value.slice(0, 5)
})

const totalCommits = computed(() => {
  return validMembers.value.reduce((sum, member) => sum + member.total_commits, 0)
})

const lastUpdateTime = computed(() => {
  if (!commitsData.value?.update_time) return '未知'
  
  const updateTime = new Date(commitsData.value.update_time)
  return updateTime.toLocaleString('zh-CN')
})

// 方法
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
  if (!userKey.includes('@')) {
    return userKey
  }

  // 如果是邮箱，提取用户名部分
  const emailMatch = userKey.match(/^([^@]+)@/)
  return emailMatch ? emailMatch[1] : userKey
}

const extractGithubUsername = (userKey) => {
  // 如果不包含@，说明就是GitHub用户名
  return userKey.includes('@') ? null : userKey
}

const calculateRollKingScore = (stats) => {
  let score = 0
  
  // 基础分：每个commit = 1分
  score += stats.total_commits
  
  // 连续性奖励：连续多天有commit
  const activeDays = stats.active_days || 0
  if (activeDays >= 7) {
    score += 10 // 连续7天奖励
  } else if (activeDays >= 5) {
    score += 5  // 连续5天奖励
  } else if (activeDays >= 3) {
    score += 2  // 连续3天奖励
  }
  
  // 多仓库奖励：参与多个仓库
  const repoCount = stats.repo_count || 0
  if (repoCount >= 5) {
    score += 5
  } else if (repoCount >= 3) {
    score += 3
  } else if (repoCount >= 2) {
    score += 1
  }
  
  // 平均每日commit奖励
  const avgCommitsPerDay = stats.avg_commits_per_day || 0
  if (avgCommitsPerDay >= 5) {
    score += 8
  } else if (avgCommitsPerDay >= 3) {
    score += 5
  } else if (avgCommitsPerDay >= 2) {
    score += 2
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
/* 卷王榜特有样式 - 基础样式由 leaderboard-card-base 提供 */
.weekly-commits-card {
  /* 移除顶部彩色边框，与其他榜单保持一致 */
  border-top: none;
}

/* 卷王榜特有悬停效果 - 基础悬停由 leaderboard-card-base 提供 */
.weekly-commits-card:hover {
  box-shadow: 0 8px 25px rgba(255, 107, 107, 0.2) !important;
}

/* 卷王榜特有头部样式 - 基础样式由 card-header-base 提供 */
.card-header {
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, var(--vp-c-bg-soft) 100%) !important;
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

.animated-fire {
  animation: fireFlicker 2s ease-in-out infinite alternate;
}

@keyframes fireFlicker {
  0% { transform: scale(1) rotate(-1deg); }
  50% { transform: scale(1.1) rotate(1deg); }
  100% { transform: scale(1) rotate(-1deg); }
}

.title {
  margin: 0 0 4px 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--vp-c-text-1);
}

.description {
  margin: 0;
  font-size: 14px;
  color: var(--vp-c-text-2);
  line-height: 1.4;
}

.stats-badge {
  background: linear-gradient(135deg, #ff6b6b, #ff8e8e);
  color: white;
  padding: 8px 12px;
  border-radius: 20px;
  text-align: center;
  min-width: 60px;
  box-shadow: 0 2px 8px rgba(255, 107, 107, 0.3);
}

.stats-badge .count {
  display: block;
  font-size: 18px;
  font-weight: bold;
  line-height: 1;
}

.stats-badge .label {
  display: block;
  font-size: 12px;
  opacity: 0.9;
}

.update-info-section {
  padding: 15px 20px;
  background: var(--vp-c-bg-soft);
  border-bottom: 1px solid var(--vp-c-divider);
}

.time-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
}

.time-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--vp-c-text-1);
  display: flex;
  align-items: center;
  gap: 6px;
}

.update-time {
  font-size: 12px;
  color: var(--vp-c-text-2);
  opacity: 0.8;
}

.leaderboard-content {
  padding: 16px 20px;
  /* 统一顶部间距，避免与头部重叠 */
}

.loading-state, .error-state, .empty-state {
  text-align: center;
  padding: 40px 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #ff6b6b;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-hint {
  font-size: 14px;
  color: var(--vp-c-text-2);
  margin-top: 8px;
}

.retry-btn {
  padding: 8px 16px;
  background: #ff6b6b;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.retry-btn:hover {
  background: #ff5252;
}

.commits-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.card-footer {
  padding: 15px 20px;
  background: var(--vp-c-bg-soft);
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--vp-c-divider);
}

.ranking-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
  color: var(--vp-c-text-2);
}

.expand-btn {
  background: none;
  border: 1px solid var(--vp-c-divider);
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  color: var(--vp-c-text-1);
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.3s ease;
}

.expand-btn:hover {
  background: var(--vp-c-bg-soft);
  border-color: #ff6b6b;
}

.arrow {
  transition: transform 0.3s ease;
  font-size: 10px;
}

.arrow.expanded {
  transform: rotate(180deg);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .title-section {
    align-items: center;
  }
  
  .stats-badge {
    align-self: flex-end;
    min-width: auto;
  }
  
  .time-info {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }
  
  .card-footer {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
  }
  
  .ranking-info {
    text-align: center;
  }
}
</style>
