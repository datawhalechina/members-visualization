<template>
  <div
    ref="itemRef"
    class="night-owl-item leaderboard-item-base"
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
        :alt="member.display_name"
        class="avatar"
        @error="handleImageError"
      />
      <div class="moon-indicator">🌙</div>
    </div>

    <!-- 成员信息 -->
    <div class="member-info">
      <h4 class="member-name">{{ member.display_name }}</h4>
      <div class="member-stats">
        <span class="stat-item">
          <span class="stat-value">{{ member.night_owl_commits }}</span>
          <span class="stat-label">深夜commit</span>
        </span>
        <span class="stat-divider">•</span>
        <span class="stat-item">
          <span class="stat-value">{{ member.night_owl_percentage }}%</span>
          <span class="stat-label">深夜比例</span>
        </span>
      </div>
    </div>

    <!-- 深夜时段分布图 -->
    <div class="night-chart-section">
      <div class="chart-title">深夜分布</div>
      <div class="night-chart">
        <div
          v-for="hour in nightHours"
          :key="hour"
          class="hour-bar"
          :style="{ height: `${getNightBarHeight(hour)}%` }"
          :title="`${hour}:00 - ${member.beijing_hourly_distribution[hour] || 0} commits`"
        >
          <div class="bar-fill night-bar-fill"></div>
        </div>
      </div>
    </div>

    <!-- 分数和趋势 -->
    <div class="score-section">
      <div class="score-value night-score">{{ member.night_owl_score }}</div>
      <div class="score-label">夜猫分</div>

      <div class="trend-indicator night-trend" :class="getNightTrendClass()">
        {{ getNightTrendIcon() }}
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
          <path fill="currentColor" d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.30.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
        </svg>
      </a>
    </div>

    <!-- 详细信息悬浮框 -->
    <div
      ref="popupRef"
      class="details-popup night-popup"
      :class="`popup-${popupPosition}`"
      v-if="props.showDetails"
    >
      <div class="popup-header">
        <h5>{{ member.display_name }} 的深夜战绩</h5>
        <button @click="emit('toggle-details', props.member.user_key)" class="close-btn">×</button>
      </div>

      <div class="popup-content">
        <!-- 统计概览和深夜分析 - 左右并排布局 -->
        <div class="top-sections">
          <div class="detail-section stats-section">
            <h6>🌙 深夜统计</h6>
            <ul>
              <li>深夜commit：{{ member.night_owl_commits }} 个</li>
              <li>深夜比例：{{ member.night_owl_percentage }}%</li>
              <li>夜猫分数：{{ member.night_owl_score }} 分</li>
              <li>活跃天数：{{ member.active_days }} 天</li>
            </ul>
          </div>

          <div class="detail-section analysis-section">
            <h6>📊 时段分析</h6>
            <div class="night-hours-detail">
              <div v-for="hour in nightHours" :key="hour" class="hour-detail">
                <span class="hour-label">{{ hour }}:00</span>
                <span class="hour-count">{{ member.beijing_hourly_distribution[hour] || 0 }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="detail-section" v-if="nightOwlCommits.length">
          <h6>🌃 深夜提交记录</h6>
          <div class="commit-messages">
            <div
              v-for="commit in nightOwlCommits.slice(0, 3)"
              :key="commit.url"
              class="commit-message night-commit"
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
                  <span class="repo-link">{{ commit.repo }}</span> •
                  <span class="night-time">{{ formatNightTime(commit.beijing_hour) }}</span> •
                  {{ commit.date }}
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

    <!-- 点击区域（已移除点击事件，避免干扰 Debug hover） -->
    <div class="click-overlay" aria-hidden="true"></div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, watch } from 'vue'

// Props
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
const emit = defineEmits(['toggle-details'])

// 整卡点击：忽略 GitHub 链接与弹窗内部的点击
const onItemClick = (e) => {
  if (e.target.closest && (e.target.closest('.github-link') || e.target.closest('.details-popup'))) {
    return
  }
  emit('toggle-details', props.member.user_key)
}

// 弹窗定位相关
const popupRef = ref(null)
const itemRef = ref(null)
const popupPosition = ref('bottom') // 'bottom' 或 'top'

// 深夜时段（22:00-06:00）
const nightHours = [22, 23, 0, 1, 2, 3, 4, 5]

// 计算属性
const nightOwlCommits = computed(() => {
  return (props.member.commit_messages || []).filter(commit => commit.is_night_owl)
})

// 工具函数
const getMedal = (rank) => {
  const medals = { 1: '🥇', 2: '🥈', 3: '🥉' }
  return medals[rank] || rank
}

const getAvatarUrl = (avatar) => {
  if (!avatar) return '/default-avatar.png'

  const basePath = import.meta.env.BASE_URL || '/'
  if (avatar.startsWith('http')) return avatar

  return `${basePath}${avatar}`.replace(/\/+/g, '/')
}

const handleImageError = (event) => {
  event.target.src = '/default-avatar.png'
}

const getNightBarHeight = (hour) => {
  const count = props.member.beijing_hourly_distribution[hour] || 0
  const maxCount = Math.max(...nightHours.map(h => props.member.beijing_hourly_distribution[h] || 0))
  return maxCount > 0 ? (count / maxCount) * 100 : 0
}

const getNightTrendClass = () => {
  const percentage = props.member.night_owl_percentage || 0
  if (percentage >= 50) return 'trend-hot'
  if (percentage >= 30) return 'trend-warm'
  return 'trend-cool'
}

const getNightTrendIcon = () => {
  const percentage = props.member.night_owl_percentage || 0
  if (percentage >= 50) return '🔥'
  if (percentage >= 30) return '⭐'
  return '💤'
}

const formatNightTime = (hour) => {
  return `${hour.toString().padStart(2, '0')}:00`
}

// 弹窗定位逻辑
const updatePopupPosition = async () => {
  if (!props.showDetails || !itemRef.value) return

  await nextTick()

  try {
    const leaderboardContainer = itemRef.value.closest('.commits-list')
    if (!leaderboardContainer) {
      popupPosition.value = 'bottom'
      return
    }

    // 找到所有成员项
    const allItems = leaderboardContainer.querySelectorAll('.night-owl-item')
    const currentIndex = Array.from(allItems).indexOf(itemRef.value)
    const totalItems = allItems.length

    // 如果是最后两个成员，直接向上弹出
    if (currentIndex >= totalItems - 2) {
      popupPosition.value = 'top'
      return
    }

    // 基于容器内可用空间判断（与 Weekly 保持一致）
    const rect = itemRef.value.getBoundingClientRect()
    const containerRect = leaderboardContainer.getBoundingClientRect()
    const popupHeight = 320
    const margin = 20

    const spaceBelow = containerRect.bottom - rect.bottom
    const spaceAbove = rect.top - containerRect.top

    if (spaceBelow < popupHeight + margin && spaceAbove > popupHeight + margin) {
      popupPosition.value = 'top'
    } else {
      popupPosition.value = 'bottom'
    }

  } catch (error) {
    console.warn('弹窗定位计算失败:', error)
    popupPosition.value = 'bottom'
  }
}

// 监听弹窗显示状态
watch(() => props.showDetails, (newVal) => {
  if (newVal) {
    updatePopupPosition()
  }
}, { immediate: true })
</script>

<style scoped>
/* 夜猫榜特有样式 - 基础样式由 leaderboard-item-base 提供 */
.night-owl-item {
  border-left: 3px solid #6366f1;
  animation: slideInUp 0.6s ease-out forwards;
  opacity: 0;
  transform: translateY(20px);
}

@keyframes slideInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}


/* 可视化问题修复：确保文本颜色正确；调试模式不被遮挡 */
.member-info, .score-section {
  position: relative;
  z-index: 1;
  color: var(--vp-c-text-1);
}

/* 默认：overlay 不拦截鼠标事件，避免干扰 Debug hover 检测 */
.click-overlay {
  pointer-events: none;
  z-index: 0;
}

/* Debug 关闭时，仍保持整卡点击功能由根容器接管（onItemClick） */

.night-owl-item:hover {
  border-left-color: #5855eb;
  /* 悬停右移动画由基础样式类 leaderboard-item-base:hover 提供 */
}

/* 强化：确保悬停右移由基础样式生效（防止选择器权重或 scoped 干扰） */
.night-owl-item.leaderboard-item-base:hover {
  transform: translateX(4px) !important;
}

/* 前三名排名样式 - 由基础样式类 leaderboard-base.css 提供 */

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
  border: 2px solid #6366f1;
  color: #6366f1;
  font-weight: 700;
  font-size: 14px;
}

/* 头像区域样式 - 基础布局由 leaderboard-base.css 提供 */
.avatar-section {
  /* position, margin-right 由基础样式类提供 */
}

.avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #6366f1;
  transition: transform 0.3s ease;
}

.night-owl-item:hover .avatar {
  transform: scale(1.1);
}

.moon-indicator {
  position: absolute;
  bottom: -2px;
  right: -2px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--vp-c-bg);
  border: 1px solid #6366f1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  animation: moonPulse 2s ease-in-out infinite alternate;
}

@keyframes moonPulse {
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

/* 成员统计样式 - 基础布局由 leaderboard-base.css 提供 */
.member-stats {
  /* display, align-items, gap, font-size, color 由基础样式类提供 */
}

.stat-item {
  /* display, align-items, gap 由基础样式类提供 */
}

.stat-value {
  font-weight: 600;
  color: #6366f1;
}

.stat-divider {
  opacity: 0.5;
}

.night-chart-section {
  margin-right: 16px;
}

.chart-title {
  font-size: 10px;
  color: var(--vp-c-text-2);
  text-align: center;
  margin-bottom: 4px;
}

.night-chart {
  display: flex;
  align-items: end;
  gap: 2px;
  height: 32px;
  width: 64px;
}

.hour-bar {
  flex: 1;
  background: var(--vp-c-bg-soft);
  border-radius: 2px 2px 0 0;
  position: relative;
  min-height: 2px;
}

.night-bar-fill {
  background: linear-gradient(to top, #6366f1, #8b5cf6);
  width: 100%;
  height: 100%;
  border-radius: 2px 2px 0 0;
}

/* 分数区域样式 - 基础布局由 leaderboard-base.css 提供 */
.score-section {
  /* text-align, min-width, margin-right 由基础样式类提供 */
}

.night-score {
  font-size: 20px;
  font-weight: 700;
  color: #6366f1;
  margin-bottom: 2px;
}

.score-label {
  font-size: 10px;
  color: var(--vp-c-text-2);
  margin-bottom: 4px;
}

.night-trend {
  font-size: 16px;
}

/* 操作区域样式 - 基础布局由 leaderboard-base.css 提供 */
.actions-section {
  /* display, gap, flex-shrink, position, z-index 由基础样式类提供 */
}

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
  transition: all 0.3s ease;
  position: relative;
  z-index: 3;
}

.github-link:hover {
  background: #6366f1;
  color: white;
  transform: scale(1.1);
}

.github-icon {
  width: 16px;
  height: 16px;
}

.trend-hot { color: #ef4444; }
.trend-warm { color: #f59e0b; }
.trend-cool { color: #6b7280; }

/* 弹窗样式 */
.details-popup {
  position: absolute;
  left: 0;
  right: 0;
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-height: 320px;
  overflow-y: auto;
}

.night-popup {
  border-color: #6366f1;
  box-shadow: 0 8px 32px rgba(99, 102, 241, 0.2);
}

.popup-bottom {
  top: 100%;
  margin-top: 8px;
  animation: popupSlideInBottom 0.3s ease-out;
}

.popup-top {
  bottom: 100%;
  margin-bottom: 8px;
  animation: popupSlideInTop 0.3s ease-out;
}

/* 向下滑入动画 */
@keyframes popupSlideInBottom {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 向上滑入动画 */
@keyframes popupSlideInTop {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.popup-header {
  padding: 16px;
  border-bottom: 1px solid var(--vp-c-divider);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, var(--vp-c-bg-soft) 100%);
}

.popup-header h5 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--vp-c-text-1);
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  color: var(--vp-c-text-2);
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: var(--vp-c-bg-elv);
  color: var(--vp-c-text-1);
}

.popup-content {
  padding: 16px;
}

.top-sections {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

.stats-section, .analysis-section {
  flex: 1;
  min-width: 0;
}

.detail-section {
  margin-bottom: 16px;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.detail-section h6 {
  margin: 0 0 8px 0;
  font-size: 12px;
  font-weight: 600;
  color: var(--vp-c-text-1);
}

.detail-section ul {
  margin: 0;
  padding: 0;
  list-style: none;
}

.detail-section li {
  font-size: 11px;
  color: var(--vp-c-text-2);
  margin-bottom: 4px;
  padding-left: 12px;
  position: relative;
}

.detail-section li:before {
  content: '•';
  position: absolute;
  left: 0;
  color: #6366f1;
}

.night-hours-detail {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 4px;
}

.hour-detail {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 10px;
  padding: 2px 4px;
  background: var(--vp-c-bg-soft);
  border-radius: 4px;
}

.hour-label {
  color: var(--vp-c-text-2);
}

.hour-count {
  color: #6366f1;
  font-weight: 600;
}

.commit-messages {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.night-commit {
  border-left: 2px solid #6366f1;
}

.commit-message {
  background: var(--vp-c-bg-soft);
  border-radius: 6px;
  overflow: hidden;
  transition: all 0.2s ease;
}

.commit-message:hover {
  background: var(--vp-c-bg-elv);
}

.commit-link {
  display: block;
  padding: 8px;
  text-decoration: none;
  color: inherit;
}

.commit-text {
  font-size: 11px;
  color: var(--vp-c-text-1);
  margin-bottom: 4px;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.commit-meta {
  font-size: 10px;
  color: var(--vp-c-text-2);
  display: flex;
  align-items: center;
  gap: 4px;
}

.repo-link {
  color: #6366f1;
  font-weight: 500;
}

.night-time {
  color: #8b5cf6;
  font-weight: 600;
}

.external-link-icon {
  opacity: 0.6;
  transition: opacity 0.2s ease;
}

.commit-link:hover .external-link-icon {
  opacity: 1;
}

.click-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .night-owl-item {
    flex-wrap: wrap;
    /* padding由基础样式类提供 */
  }

  .member-info {
    order: 1;
    flex: 1 1 100%;
    margin: 8px 0;
  }

  .night-chart-section {
    order: 2;
    margin: 8px 0;
  }

  .score-section {
    order: 3;
    text-align: left;
    margin-right: 0;
  }

  .actions-section {
    order: 4;
  }

  .top-sections {
    flex-direction: column;
    gap: 8px;
  }

  .night-hours-detail {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
