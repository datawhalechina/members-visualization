<template>
  <div class="leaderboard-card leaderboard-card-base" :class="`theme-${colorScheme}`">
    <!-- 卡片头部 -->
    <div class="card-header card-header-base">
      <div class="title-section title-section-base">
        <span class="icon icon-base">{{ icon }}</span>
        <div>
          <h3 class="title title-base">{{ title }}</h3>
          <p class="description description-base">{{ description }}</p>
        </div>
      </div>
      <div class="stats-badge">
        <span class="count">{{ members.length }}</span>
        <span class="label">人上榜</span>
      </div>
    </div>

    <!-- 榜单内容 -->
    <div class="leaderboard-content">
      <div v-if="members.length === 0" class="empty-state">
        <p>暂无符合条件的成员</p>
      </div>
      
      <div v-else class="members-list">
        <LeaderboardItem
          v-for="(member, index) in displayMembers"
          :key="member.id"
          :member="member"
          :rank="member.rank"
          :color-scheme="colorScheme"
          :show-trend="showTrend"
          :icon="icon"
          :animation-delay="index * 100"
        />
      </div>
    </div>

    <!-- 卡片底部 -->
    <div class="card-footer">
      <div class="ranking-info">
        <span v-if="members.length > 0">
          冠军：{{ members[0]?.name || members[0]?.id }}
        </span>
        <span v-if="members.length > 1">
          最高分：{{ Math.round(members[0]?.score || 0) }}
        </span>
      </div>
      
      <button
        v-if="members.length > 5"
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
import { ref, computed } from 'vue'
import LeaderboardItem from './LeaderboardItem.vue'

// Props
const props = defineProps({
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    default: '🏆'
  },
  members: {
    type: Array,
    default: () => []
  },
  colorScheme: {
    type: String,
    default: 'blue',
    validator: value => ['fire', 'blue', 'green', 'purple', 'gold'].includes(value)
  },
  showTrend: {
    type: Boolean,
    default: false
  }
})

// 响应式数据
const isExpanded = ref(false)

// 计算属性
const displayMembers = computed(() => {
  return isExpanded.value ? props.members : props.members.slice(0, 5)
})

// 方法
const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}
</script>

<style scoped>
/* 通用榜单特有样式 - 基础样式由 leaderboard-card-base 提供 */
.leaderboard-card {
  /* 基础样式由 leaderboard-card-base 提供 */
}

/* 通用榜单悬停效果 - 基础悬停由 leaderboard-card-base 提供 */
.leaderboard-card:hover {
  /* 使用基础样式类的悬停效果 */
}

/* 主题色彩 - 移除上边框，只保留左侧强调线通过LeaderboardItem实现 */

/* 通用榜单头部样式 - 基础样式由 card-header-base 提供 */
.card-header {
  /* 使用默认背景，主题色通过主题特定样式覆盖 */
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
  background: var(--vp-c-brand-1);
  color: white;
  padding: 8px 12px;
  border-radius: 20px;
  text-align: center;
  min-width: 60px;
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

.leaderboard-content {
  padding: 16px 20px;
  /* 统一顶部间距，避免与头部重叠 */
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--vp-c-text-2);
}

.members-list {
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
  border-color: var(--vp-c-brand-1);
}

.arrow {
  transition: transform 0.3s ease;
  font-size: 10px;
}

.arrow.expanded {
  transform: rotate(180deg);
}

/* 滚动条样式 */
.leaderboard-content::-webkit-scrollbar {
  width: 6px;
}

.leaderboard-content::-webkit-scrollbar-track {
  background: var(--vp-c-bg-soft);
}

.leaderboard-content::-webkit-scrollbar-thumb {
  background: var(--vp-c-divider);
  border-radius: 3px;
}

.leaderboard-content::-webkit-scrollbar-thumb:hover {
  background: var(--vp-c-text-3);
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
  
  .card-footer {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
  }
  
  .ranking-info {
    text-align: center;
  }
}

/* 动画效果 */
@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.leaderboard-card {
  animation: slideInUp 0.6s ease-out;
}

/* 主题特定的渐变背景 */
.theme-fire .card-header {
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, var(--vp-c-bg-soft) 100%);
}

.theme-blue .card-header {
  background: linear-gradient(135deg, rgba(78, 205, 196, 0.1) 0%, var(--vp-c-bg-soft) 100%);
}

.theme-green .card-header {
  background: linear-gradient(135deg, rgba(149, 225, 211, 0.1) 0%, var(--vp-c-bg-soft) 100%);
}

.theme-purple .card-header {
  background: linear-gradient(135deg, rgba(168, 230, 207, 0.1) 0%, var(--vp-c-bg-soft) 100%);
}

.theme-gold .card-header {
  background: linear-gradient(135deg, rgba(255, 217, 61, 0.1) 0%, var(--vp-c-bg-soft) 100%);
}
</style>
