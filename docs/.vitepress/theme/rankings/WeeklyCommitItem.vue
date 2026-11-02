<template>
  <div
    ref="itemRef"
    class="weekly-commit-item leaderboard-item-base"
    :class="[ `rank-${rank}`, { 'is-expanded': props.showDetails } ]"
    :style="{ animationDelay: `${animationDelay}ms` }"
    @click="onItemClick"
  >
    <!-- 排名徽章 -->
    <div class="rank-badge">
      <span v-if="rank <= 3" class="medal">{{ getMedal(rank) }}</span>
      <span v-else class="rank-number">{{ rank }}</span>
    </div>

    <!-- 成员头像 -->
    <div class="avatar-section">
      <img
        :src="getAvatarUrl(member.avatar)"
        :alt="displayName"
        class="avatar"
        @error="handleImageError"
      />
      <div class="fire-indicator">🔥</div>
    </div>

    <!-- 成员信息 -->
    <div class="member-info">
      <div class="name-section">
        <h4 class="member-name">{{ displayName }}</h4>
        <div class="member-meta">
          <span v-if="member.location" class="location">📍 {{ member.location }}</span>
          <span v-if="member.company" class="company">🏢 {{ member.company }}</span>
        </div>
      </div>
      <div class="domains-section" v-if="member.domain">
        <div class="domains">
          <span v-for="domain in getDomains(member.domain)" :key="domain" class="domain-tag">{{ domain }}</span>
        </div>
      </div>



    </div>

    <!-- 每日commit分布图 -->
    <div class="daily-chart-section">
      <div class="chart-title">每日分布</div>
      <div class="daily-chart">
        <div
          v-for="d in weeklyDailySeries"
          :key="d.date"
          :class="d.hasData ? 'day-bar' : 'day-dash'"
          :style="d.hasData ? { height: `${getBarHeight(d.count)}%` } : {}"
          :title="d.hasData ? `${d.date}: ${d.count} commits` : `${d.date}: 无数据`"
        >
          <div v-if="d.hasData" class="bar-fill"></div>
        </div>
      </div>
    </div>

    <!-- 分数和趋势 -->
    <div class="score-section">
      <div class="score-value">{{ member.score }}</div>
      <div class="score-label">{{ weeklyScoreLabel }}</div>

      <!-- 详细数据 -->
      <div class="detailed-stats">
        <div class="stat-item" v-if="member.followers" title="GitHub 粉丝量（Followers）">
          <span class="stat-icon">👥</span>
          <span class="stat-value">{{ member.followers }}</span>
        </div>
        <div class="stat-item" v-if="member.total_stars">
          <span class="stat-icon">⭐</span>
          <span class="stat-value">{{ member.total_stars }}</span>
        </div>
        <div class="stat-item" v-if="member.public_repos">
          <span class="stat-icon">📁</span>
          <span class="stat-value">{{ member.public_repos }}</span>
        </div>
      </div>

      <div class="trend-indicator" :class="getTrendClass()">
        {{ getTrendIcon() }}
      </div>
    </div>

    <!-- 详细信息悬浮框 -->
    <div
      ref="popupRef"
      class="details-popup"
      :class="`popup-${popupPosition}`"
      v-if="props.showDetails"
    >

      <div class="popup-header">
        <h5>{{ displayName }} 的本周战绩</h5>
        <button @click="emit('toggle-details', props.member.user_key)" class="close-btn">×</button>
      </div>

      <div class="popup-content">
        <!-- 统计概览和主要仓库 - 左右并排布局 -->
        <div class="top-sections">
          <div class="detail-section stats-section">
            <h6>📊 统计概览</h6>
            <ul>
              <li>总commit数：{{ member.total_commits }}</li>
              <li>参与仓库：{{ member.repo_count }} 个</li>
              <li>活跃天数：{{ member.active_days }} 天</li>
              <li>平均每日：{{ member.avg_commits_per_day?.toFixed(1) }} commits</li>
            </ul>
          </div>

          <div class="detail-section repos-section" v-if="member.repos?.length">
            <h6>📁 主要仓库</h6>
            <div class="repo-tags">
              <a
                v-for="repo in member.repos.slice(0, 5)"
                :key="repo"
                :href="`https://github.com/datawhalechina/${repo}`"
                target="_blank"
                rel="noopener noreferrer"
                class="repo-tag repo-link-tag"
                :title="`访问仓库: ${repo}`"
              >
                {{ repo }}
                <svg class="external-link-icon" viewBox="0 0 24 24" width="10" height="10">
                  <path fill="currentColor" d="M14,3V5H17.59L7.76,14.83L9.17,16.24L19,6.41V10H21V3M19,19H5V5H12V3H5C3.89,3 3,3.9 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V12H19V19Z"/>
                </svg>
              </a>
            </div>
          </div>
        </div>

        <div class="detail-section" v-if="member.commit_messages?.length">
          <h6>💬 最近提交</h6>
          <div class="commit-messages">
            <div
              v-for="commit in member.commit_messages.slice(0, 3)"
              :key="commit.url"
              class="commit-message"
            >
              <a
                :href="commit.url"
                target="_blank"
                rel="noopener noreferrer"
                class="commit-link"
                :title="`查看提交详情: ${commit.message}`"
              >
                <div class="commit-text">{{ commit.message }}</div>
                <div class="commit-meta">
                  <span class="repo-link">{{ commit.repo }}</span> • {{ commit.date }}
                  <svg class="external-link-icon" viewBox="0 0 24 24" width="12" height="12">
                    <path fill="currentColor" d="M14,3V5H17.59L7.76,14.83L9.17,16.24L19,6.41V10H21V3M19,19H5V5H12V3H5C3.89,3 3,3.9 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V12H19V19Z"/>
                  </svg>
                </div>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- GitHub 链接 -->
    <div class="actions-section">

      <a
        v-if="member.github_username"
        :href="`https://github.com/${member.github_username}`"
        target="_blank"
        rel="noopener noreferrer"
        class="github-link"
        title="访问GitHub"
      >
        <svg class="github-icon" viewBox="0 0 24 24" width="16" height="16">
          <path fill="currentColor" d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
        </svg>
      </a>
    </div>

    <!-- 点击区域 -->
    <div class="click-overlay" aria-hidden="true"></div>
  </div>


</template>

<script setup>
import { ref, computed, nextTick, watch } from 'vue'

// Props

// 研究领域拆分（与 LeaderboardItem.vue 一致）
const getDomains = (domainString) => {
  if (!domainString) return []
  return domainString.split(';').map(d => d.trim()).filter(Boolean)
}

const props = defineProps({
  member: {
    type: Object,
    required: true
  },
  rank: {
    type: Number,
    required: true
  },
  animationDelay: {
    type: Number,
    default: 0
  },
  showDetails: {
    type: Boolean,
    default: false
  }
})

// Emits

// 整卡点击（排除 GitHub 按钮与弹窗区域）
const onItemClick = (e) => {
  if (e.target.closest && (e.target.closest('.github-link') || e.target.closest('.details-popup'))) return
  emit('toggle-details', props.member.user_key)
}

const emit = defineEmits(['toggle-details'])

// 弹窗定位相关
const popupRef = ref(null)
const itemRef = ref(null)
const popupPosition = ref('bottom') // 'bottom' 或 'top'

// 智能计算弹窗位置
const calculatePopupPosition = async () => {
  if (!props.showDetails) return

  await nextTick()

  if (!itemRef.value) return

  // 找到榜单容器
  const leaderboardContainer = itemRef.value.closest('.leaderboard-content') ||
                               itemRef.value.closest('.commits-list') ||
                               itemRef.value.closest('.weekly-commits-card')

  if (!leaderboardContainer) {
    popupPosition.value = 'bottom'
    return
  }

  // 找到所有成员项
  const allItems = leaderboardContainer.querySelectorAll('.weekly-commit-item')
  const currentIndex = Array.from(allItems).indexOf(itemRef.value)
  const totalItems = allItems.length

  // 如果是最后两个成员，直接向上弹出
  if (currentIndex >= totalItems - 2) {
    popupPosition.value = 'top'
    return
  }

  // 对于其他成员，基于空间计算
  const itemRect = itemRef.value.getBoundingClientRect()
  const containerRect = leaderboardContainer.getBoundingClientRect()
  const popupHeight = 320 // 调整后的弹窗高度（因为布局优化后高度减少）
  const margin = 20 // 安全边距

  // 计算在容器内的可用空间
  const spaceBelow = containerRect.bottom - itemRect.bottom
  const spaceAbove = itemRect.top - containerRect.top

  // 如果下方空间不足，且上方空间充足，则向上显示
  if (spaceBelow < popupHeight + margin && spaceAbove > popupHeight + margin) {
    popupPosition.value = 'top'
  } else {
    popupPosition.value = 'bottom'
  }
}

// 监听弹窗显示状态变化
watch(() => props.showDetails, (newVal) => {
  if (newVal) {
    calculatePopupPosition()
  }
})

// 计算属性
const displayName = computed(() => {
  // 优先使用name字段，为空时使用id字段
  const name = props.member.name
  if (name && name !== 'null' && name !== 'undefined' && name !== 'None' && name.trim() !== '') {
    return name
  }

  // 如果name为空，使用id字段
  if (props.member.id) {
    return props.member.id
  }

  // 最后回退到display_name
  return props.member.display_name || props.member.user_key || '未知用户'
})

// 统一 7 天时间轴（优先以数据中的最大日期为止，回溯 6 天）
const formatDate = (d) => {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

const weeklyDates = computed(() => {
  const keys = props.member.daily_commits ? Object.keys(props.member.daily_commits) : []
  let end = new Date()
  if (keys.length) {
    const parsed = keys.map(k => new Date(k)).filter(d => !isNaN(d))
    if (parsed.length) end = parsed.sort((a, b) => a - b)[parsed.length - 1]
  }
  const arr = []
  for (let i = 6; i >= 0; i--) {
    const d = new Date(end)
    d.setDate(d.getDate() - i)
    arr.push(formatDate(d))
  }
  return arr
})

// 将无记录的日期标为占位（day-dash）
const weeklyDailySeries = computed(() => {
  const dc = props.member.daily_commits || {}
  return weeklyDates.value.map(date => {
    const hasData = Object.prototype.hasOwnProperty.call(dc, date)
    const count = hasData ? (dc[date] || 0) : 0
    return { date, count, hasData }
  })
})



const weeklyScoreLabel = computed(() => {
  const parts = []
  const commits = props.member.total_commits
  const repos = props.member.repo_count
  const days = props.member.active_days
  if (typeof commits === 'number') parts.push(`${commits} 次`)
  if (typeof repos === 'number') parts.push(`${repos} 仓库`)
  if (typeof days === 'number') parts.push(`${days} 天`)
  return parts.join(' • ')
})

// 方法
const getMedal = (rank) => {


  const medals = { 1: '🥇', 2: '🥈', 3: '🥉' }
  return medals[rank] || rank
}

const getAvatarUrl = (avatar) => {
  const basePath = import.meta.env.BASE_URL || '/'
  const defaultAvatar = `${basePath}default-avatar.svg`.replace(/\/+/g, '/')

  if (!avatar) return defaultAvatar

  // 优先处理本地缓存的头像文件
  if (avatar.startsWith('avatars/')) {
    return `${basePath}${avatar}`.replace(/\/+/g, '/')
  }

  if (avatar.startsWith('http')) {
    return avatar
  }
  return `${basePath}${avatar}`.replace(/\/+/g, '/')
}

const handleImageError = (event) => {
  const basePath = import.meta.env.BASE_URL || '/'
  event.target.src = `${basePath}default-avatar.svg`.replace(/\/+/g, '/')
}

const getBarHeight = (count) => {
  const withData = weeklyDailySeries.value.filter(d => d.hasData).map(d => d.count)
  const maxCount = withData.length ? Math.max(...withData) : 0
  return maxCount > 0 ? (count / maxCount) * 100 : 0
}

const getTrendClass = () => {
  // 基于活跃天数和平均commit数判断趋势
  const avgCommits = props.member.avg_commits_per_day || 0
  const activeDays = props.member.active_days || 0

  if (avgCommits >= 3 && activeDays >= 5) return 'up'
  if (avgCommits >= 2 && activeDays >= 3) return 'stable'
  return 'down'
}

const getTrendIcon = () => {
  const trendClass = getTrendClass()
  const icons = { up: '📈', stable: '➡️', down: '📉' }
  return icons[trendClass] || '➡️'
}
</script>

<style scoped>
/* 卷王榜特有样式 - 基础样式由 leaderboard-item-base 提供 */
.weekly-commit-item {
  border-left: 3px solid #ff6b6b;
  animation: slideInLeft 0.6s ease-out;
}

.weekly-commit-item:hover {
  border-left-color: #e53e3e;
}

/* 排名样式 - 由基础样式类 leaderboard-base.css 提供 */

/* 排名徽章样式 - 基础布局由 leaderboard-base.css 提供 */
.rank-badge {
  width: 40px;
  height: 40px;
  /* display, align-items, justify-content, margin-right, flex-shrink 由基础样式类提供 */
}

.medal {
  font-size: 24px;
}

.rank-number {
  background: var(--vp-c-bg-soft);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #ff6b6b;
  color: #ff6b6b;
  font-weight: 700;
  font-size: 14px;
}

/* 头像区域样式 - 基础布局由 leaderboard-base.css 提供 */

.avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #ff6b6b;
  transition: transform 0.3s ease;
}

.weekly-commit-item:hover .avatar {
  transform: scale(1.1);
}

.fire-indicator {
  position: absolute;
  bottom: -2px;
  right: -2px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--vp-c-bg);
  border: 1px solid #ff6b6b;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  animation: fireFlicker 2s ease-in-out infinite alternate;
}

@keyframes fireFlicker {
  0% { transform: scale(1); }
  100% { transform: scale(1.2); }
}

/* 成员信息样式 - 由基础样式类 leaderboard-base.css 提供 */

.member-name {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--vp-c-text-1);
}

.member-meta {
  margin-bottom: 8px;
}

.github-username {
  font-size: 12px;
  color: var(--vp-c-text-2);
}

/* 提交统计样式 - 基础布局由 leaderboard-base.css 提供 */
.commit-stats {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: nowrap; /* 避免换行导致成员卡高度拉伸 */
  overflow: hidden;
}

.commit-stats .stat-item {
  font-size: 12px;
  color: var(--vp-c-text-2);
  margin: 0;
}

.commit-stats .stat-value {
  white-space: nowrap;
}

/* 无数据日的短横线占位 */
.day-dash {
  width: 8px;
  height: 2px;
  background: var(--vp-c-bg-soft);
  border-radius: 2px;
  align-self: flex-end;
  opacity: 0.7;
}



.stat-icon {
  font-size: 10px;
}

.daily-chart-section {
  margin-right: 12px;
  flex-shrink: 0;
}

.chart-title {
  font-size: 10px;
  color: var(--vp-c-text-2);
  text-align: center;
  margin-bottom: 4px;
}

.daily-chart {
  display: flex;
  gap: 2px;
  height: 30px;
  align-items: flex-end;
}

.day-bar {
  width: 8px;
  height: 100%;
  background: rgba(255, 107, 107, 0.1);
  border-radius: 2px;
  position: relative;
  cursor: pointer;
}

.bar-fill {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, #ff6b6b, #ff8e8e);
  border-radius: 2px;
  height: 100%;
}

/* 分数区域样式 - 基础布局由 leaderboard-base.css 提供 */

/* 分数样式 - 由基础样式类 leaderboard-base.css 提供 */
.score-value {
  /* font-size, font-weight, color 由基础样式类提供 */
  line-height: 1; /* 保留特殊行高 */
}

.score-label {
  /* font-size, color 由基础样式类提供 */
  margin-top: 2px; /* 保留特殊间距 */
}

.trend-indicator {
  position: absolute;
  top: -5px;
  right: -5px;
  font-size: 12px;
}

/* 操作区域样式 - 基础布局由 leaderboard-base.css 提供 */

.github-link {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-2);
  text-decoration: none;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  position: relative;
  z-index: 3;
}

.github-link:hover {
  background: #ff6b6b;
  color: white;
  transform: scale(1.1);
}

.click-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
  pointer-events: none;
}

.github-icon {
  width: 16px;
  height: 16px;
}

/* 详细信息弹窗 */
.details-popup {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  padding: 18px;
  width: 600px;
  max-width: 95vw;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  max-height: 320px;
  overflow-y: auto;
}

/* 弹窗向下显示（默认） */
.details-popup.popup-bottom {
  top: 100%;
  margin-top: 8px;
  animation: popupSlideInBottom 0.3s ease-out;
}

/* 弹窗向上显示 */
.details-popup.popup-top {
  bottom: 100%;
  margin-bottom: 8px;
  animation: popupSlideInTop 0.3s ease-out;
}

/* 向下滑入动画 */
@keyframes popupSlideInBottom {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

/* 向上滑入动画 */
@keyframes popupSlideInTop {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--vp-c-divider);
}

.popup-header h5 {
  margin: 0;
  font-size: 14px;
  color: var(--vp-c-text-1);
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: var(--vp-c-text-2);
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 顶部区域左右并排布局 */
.top-sections {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

.stats-section {
  flex: 1;
  min-width: 0;
}

.repos-section {
  flex: 1;
  min-width: 0;
}

.detail-section {
  margin-bottom: 12px;
}

/* 当只有统计概览时，占满整个宽度 */
.top-sections .stats-section:only-child {
  flex: 1;
}

.detail-section h6 {
  margin: 0 0 6px 0;
  font-size: 12px;
  color: var(--vp-c-text-1);
  font-weight: 600;
}

.detail-section ul {
  margin: 0;
  padding-left: 16px;
  font-size: 12px;
  color: var(--vp-c-text-2);
  line-height: 1.3;
}

.detail-section ul li {
  margin-bottom: 2px;
}

.repo-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.repo-tag {
  background: rgba(255, 107, 107, 0.1);
  color: #ff6b6b;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 10px;
  font-weight: 500;
}

/* 仓库链接样式 */
.repo-link-tag {
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 3px;
  transition: all 0.2s ease;
}

.repo-link-tag:hover {
  background: rgba(255, 107, 107, 0.2);
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(255, 107, 107, 0.2);
}

.commit-messages {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.commit-message {
  padding: 6px;
  background: var(--vp-c-bg-soft);
  border-radius: 4px;
}

/* Commit链接样式 */
.commit-link {
  text-decoration: none;
  color: inherit;
  display: block;
  transition: all 0.2s ease;
  border-radius: 4px;
}

.commit-link:hover {
  background: var(--vp-c-bg-alt);
  transform: translateX(2px);
}

.commit-text {
  font-size: 11px;
  color: var(--vp-c-text-1);
  margin-bottom: 2px;
  line-height: 1.3;
}

.commit-meta {
  font-size: 10px;
  color: var(--vp-c-text-2);
  display: flex;
  align-items: center;
  gap: 4px;
}

.repo-link {
  color: #ff6b6b;
  font-weight: 500;
}

/* 外部链接图标 */
.external-link-icon {
  opacity: 0.6;
  transition: opacity 0.2s ease;
}

.commit-link:hover .external-link-icon,
.repo-link-tag:hover .external-link-icon {
  opacity: 1;
}

/* 动画 */
@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .weekly-commit-item {
    flex-wrap: wrap;
    padding: 16px 0;
  }

  .member-info {
    order: 1;
    flex: 1 1 100%;
    margin: 8px 0;
  }

  .daily-chart-section {
    order: 2;
    margin: 8px 0;
  }

  .score-section {
    order: 3;
    margin: 8px 0;
  }

  .actions-section {
    order: 4;
  }

  .commit-stats {
    flex-direction: column;
    gap: 4px;
  }

  .details-popup {
    width: 280px;
    max-width: calc(100vw - 40px);
  }

  /* 移动端弹窗内容布局调整 */
  .top-sections {
    flex-direction: column;
    gap: 8px;
  }

  .stats-section,
  .repos-section {
    flex: none;
  }
}
</style>
