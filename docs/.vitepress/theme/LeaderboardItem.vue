<template>
  <div 
    class="leaderboard-item" 
    :class="[`rank-${rank}`, `theme-${colorScheme}`]"
    :style="{ animationDelay: `${animationDelay}ms` }"
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
        :alt="member.name || member.id"
        class="avatar"
        @error="handleImageError"
      />
      <div v-if="showTrend" class="trend-indicator" :class="getTrendClass()">
        {{ getTrendIcon() }}
      </div>
    </div>

    <!-- 成员信息 -->
    <div class="member-info">
      <div class="name-section">
        <h4 class="member-name">{{ member.name || member.id }}</h4>
        <div class="member-meta">
          <span v-if="member.location" class="location">📍 {{ member.location }}</span>
          <span v-if="member.company" class="company">🏢 {{ member.company }}</span>
        </div>
      </div>
      
      <div class="domains-section" v-if="member.domain">
        <div class="domains">
          <span 
            v-for="domain in getDomains(member.domain)" 
            :key="domain"
            class="domain-tag"
          >
            {{ domain }}
          </span>
        </div>
      </div>
    </div>

    <!-- 分数显示 -->
    <div class="score-section">
      <div class="score-value">{{ Math.round(member.score || 0) }}</div>
      <div class="score-label">{{ member.scoreDisplay || '分数' }}</div>
      
      <!-- 详细数据 -->
      <div class="detailed-stats">
        <div class="stat-item" v-if="member.followers">
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
    </div>

    <!-- GitHub 链接 -->
    <div class="actions-section">
      <a 
        :href="member.github" 
        target="_blank" 
        rel="noopener noreferrer"
        class="github-link"
        :title="`访问 ${member.name || member.id} 的 GitHub`"
      >
        <svg class="github-icon" viewBox="0 0 24 24" width="16" height="16">
          <path fill="currentColor" d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
        </svg>
      </a>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

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
  colorScheme: {
    type: String,
    default: 'blue'
  },
  showTrend: {
    type: Boolean,
    default: false
  },
  animationDelay: {
    type: Number,
    default: 0
  }
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

const getDomains = (domainString) => {
  if (!domainString) return []
  return domainString.split(';').map(d => d.trim()).filter(d => d)
}

const getTrendClass = () => {
  // 模拟趋势数据，实际应该基于历史数据
  const trends = ['up', 'down', 'stable']
  return trends[Math.floor(Math.random() * trends.length)]
}

const getTrendIcon = () => {
  const trendClass = getTrendClass()
  const icons = { up: '📈', down: '📉', stable: '➡️' }
  return icons[trendClass] || '➡️'
}
</script>

<style scoped>
.leaderboard-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--vp-c-divider-light);
  transition: all 0.3s ease;
  animation: slideInLeft 0.6s ease-out;
  position: relative;
}

.leaderboard-item:hover {
  background: var(--vp-c-bg-soft);
  border-radius: 8px;
  padding-left: 8px;
  padding-right: 8px;
}

.leaderboard-item:last-child {
  border-bottom: none;
}

/* 排名样式 */
.rank-1 {
  background: linear-gradient(90deg, rgba(255, 215, 0, 0.1) 0%, transparent 100%);
}

.rank-2 {
  background: linear-gradient(90deg, rgba(192, 192, 192, 0.1) 0%, transparent 100%);
}

.rank-3 {
  background: linear-gradient(90deg, rgba(205, 127, 50, 0.1) 0%, transparent 100%);
}

.rank-badge {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  flex-shrink: 0;
}

.medal {
  font-size: 24px;
}

.rank-number {
  font-size: 18px;
  font-weight: bold;
  color: var(--vp-c-text-1);
  background: var(--vp-c-bg-soft);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid var(--vp-c-divider);
}

.avatar-section {
  position: relative;
  margin-right: 12px;
  flex-shrink: 0;
}

.avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--vp-c-divider);
  transition: transform 0.3s ease;
}

.leaderboard-item:hover .avatar {
  transform: scale(1.1);
}

.trend-indicator {
  position: absolute;
  bottom: -2px;
  right: -2px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
}

.member-info {
  flex: 1;
  min-width: 0;
  margin-right: 12px;
}

.name-section {
  margin-bottom: 4px;
}

.member-name {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--vp-c-text-1);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.member-meta {
  display: flex;
  gap: 12px;
  margin-top: 2px;
}

.location, .company {
  font-size: 12px;
  color: var(--vp-c-text-2);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.domains-section {
  margin-top: 6px;
}

.domains {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.domain-tag {
  background: var(--vp-c-brand-soft);
  color: var(--vp-c-brand-1);
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 500;
  white-space: nowrap;
}

.score-section {
  text-align: right;
  margin-right: 12px;
  flex-shrink: 0;
}

.score-value {
  font-size: 20px;
  font-weight: bold;
  color: var(--vp-c-brand-1);
  line-height: 1;
}

.score-label {
  font-size: 11px;
  color: var(--vp-c-text-2);
  margin-top: 2px;
}

.detailed-stats {
  display: flex;
  gap: 8px;
  margin-top: 4px;
  justify-content: flex-end;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 11px;
  color: var(--vp-c-text-2);
}

.stat-icon {
  font-size: 10px;
}

.actions-section {
  flex-shrink: 0;
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
}

.github-link:hover {
  background: var(--vp-c-brand-1);
  color: white;
  transform: scale(1.1);
}

.github-icon {
  width: 16px;
  height: 16px;
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
  .leaderboard-item {
    flex-wrap: wrap;
    padding: 16px 0;
  }
  
  .member-info {
    order: 1;
    flex: 1 1 100%;
    margin: 8px 0;
  }
  
  .score-section {
    order: 2;
    text-align: left;
    margin-right: 0;
  }
  
  .actions-section {
    order: 3;
  }
  
  .member-meta {
    flex-direction: column;
    gap: 4px;
  }
  
  .detailed-stats {
    justify-content: flex-start;
  }
}

/* 主题特定样式 */
.theme-fire .rank-number {
  border-color: #ff6b6b;
  color: #ff6b6b;
}

.theme-blue .rank-number {
  border-color: #4ecdc4;
  color: #4ecdc4;
}

.theme-green .rank-number {
  border-color: #95e1d3;
  color: #95e1d3;
}

.theme-purple .rank-number {
  border-color: #a8e6cf;
  color: #a8e6cf;
}

.theme-gold .rank-number {
  border-color: #ffd93d;
  color: #ffd93d;
}
</style>
