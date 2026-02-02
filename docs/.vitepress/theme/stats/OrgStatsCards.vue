<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

// 日期范围选项
const periodOptions = [
  { label: '7天', value: 'past_7_days' },
  { label: '28天', value: 'past_28_days' },
  { label: '90天', value: 'past_90_days' },
  { label: '12个月', value: 'past_12_months' }
]

// 当前选中的日期范围（默认选中90天）
const selectedPeriod = ref('past_90_days')

// 暗黑模式状态
const isDark = ref(false)

// 监听 VitePress 主题变化
const checkDarkMode = () => {
  if (typeof window !== 'undefined') {
    isDark.value = document.documentElement.classList.contains('dark')
  }
}

let observer = null

onMounted(() => {
  checkDarkMode()
  if (typeof window !== 'undefined' && typeof MutationObserver !== 'undefined') {
    observer = new MutationObserver(() => checkDarkMode())
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class']
    })
  }
})

onUnmounted(() => {
  if (observer) observer.disconnect()
})

// 计算当前颜色方案
const colorScheme = computed(() => isDark.value ? 'dark' : 'light')

// 卡片分组配置
const cardGroups = computed(() => [
  {
    id: 'popularity',
    title: '⭐ 受欢迎程度',
    description: '通过 Stars 了解社区关注度和潜在合作机会',
    cards: [
      {
        id: 'stars-total',
        title: 'Stars 增长趋势',
        type: 'compose-org-activity-growth-total',
        params: { activity: 'stars' },
        imageSize: 'full'
      },
      {
        id: 'stars-top-repos',
        title: 'Star 数最高仓库',
        type: 'compose-org-stars-top-repos',
        imageSize: 'half'
      },
      {
        id: 'active-repos',
        title: '活跃仓库',
        type: 'compose-org-activity-active-ranking',
        params: { activity: 'repos' },
        imageSize: 'half'
      }
    ]
  },
  {
    id: 'participants',
    title: '👥 参与者分析',
    description: '分析参与者活跃度、参与深度和地理分布',
    cards: [
      {
        id: 'participants-growth-active',
        title: '活跃参与者趋势',
        type: 'compose-org-participants-growth',
        params: { activity: 'active' },
        imageSize: 'full'
      },
      {
        id: 'participants-growth-new',
        title: '新增参与者趋势',
        type: 'compose-org-participants-growth',
        params: { activity: 'new' },
        imageSize: 'full'
      },
      {
        id: 'participants-ranking-active',
        title: '活跃参与者排名',
        type: 'compose-org-activity-active-ranking',
        params: { activity: 'participants' },
        imageSize: 'full'
      },
      {
        id: 'participants-ranking-new',
        title: '新增参与者排名',
        type: 'compose-org-activity-new-ranking',
        params: { activity: 'participants' },
        imageSize: 'full'
      }
    ]
  },
  {
    id: 'engagement',
    title: '🤝 参与度分析',
    description: '了解最活跃的贡献者和代码提交时间分布',
    cards: [
      {
        id: 'engagement-scatter',
        title: '最活跃贡献者',
        type: 'compose-org-engagement-scatter',
        imageSize: 'full'
      },
      {
        id: 'commits-time-distribution',
        title: '代码提交时间分布',
        type: 'analyze-org-commits-time-distribution',
        params: { zone: '8' },
        imageSize: 'full'
      }
    ]
  },
  {
    id: 'productivity',
    title: '📈 生产力分析',
    description: '分析 PR、Code Review、Issue 处理效率',
    cards: [
      {
        id: 'overview-stars',
        title: 'Stars 概览',
        type: 'compose-org-overview-stars',
        imageSize: 'auto'
      },
      {
        id: 'active-contributors',
        title: '活跃贡献者',
        type: 'compose-org-active-contributors',
        params: { activity: 'active' },
        imageSize: 'auto'
      },
      {
        id: 'pull-requests',
        title: 'Pull Requests',
        type: 'compose-org-overview-stats',
        params: { activity: 'pull-requests' },
        imageSize: '2x2'
      },
      {
        id: 'reviews',
        title: 'Code Reviews',
        type: 'compose-org-overview-stats',
        params: { activity: 'reviews' },
        imageSize: '2x2'
      },
      {
        id: 'issues',
        title: 'Issues',
        type: 'compose-org-overview-stats',
        params: { activity: 'issues' },
        imageSize: '2x2'
      }
    ]
  }
])

// 生成卡片链接
const getCardUrl = (card) => {
  const baseUrl = `https://next.ossinsight.io/widgets/official/${card.type}`
  const params = new URLSearchParams({
    owner_id: '46047812',
    period: selectedPeriod.value,
    ...card.params
  })
  return `${baseUrl}?${params.toString()}`
}

// 生成卡片图片链接
const getCardImageUrl = (card) => {
  const baseUrl = `https://next.ossinsight.io/widgets/official/${card.type}/thumbnail.png`
  const params = new URLSearchParams({
    owner_id: '46047812',
    period: selectedPeriod.value,
    image_size: card.imageSize,
    color_scheme: colorScheme.value,
    ...card.params
  })
  return `${baseUrl}?${params.toString()}`
}
</script>

<template>
  <div class="org-stats-cards">
    <!-- 日期范围选择器 -->
    <div class="period-selector">
      <span class="selector-label">📅 时间范围：</span>
      <div class="period-buttons">
        <button
          v-for="option in periodOptions"
          :key="option.value"
          class="period-btn"
          :class="{ active: selectedPeriod === option.value }"
          @click="selectedPeriod = option.value"
        >
          {{ option.label }}
        </button>
      </div>
    </div>

    <!-- 分组卡片 -->
    <div class="card-groups">
      <div
        v-for="group in cardGroups"
        :key="group.id"
        class="card-group"
      >
        <div class="group-header">
          <h3 class="group-title">{{ group.title }}</h3>
          <p class="group-description">{{ group.description }}</p>
        </div>
        <div class="cards-grid">
          <div
            v-for="card in group.cards"
            :key="card.id"
            class="card-wrapper"
            :class="`size-${card.imageSize}`"
          >
            <a
              :href="getCardUrl(card)"
              target="_blank"
              rel="noopener noreferrer"
              class="stats-card-link"
              :title="card.title"
            >
              <img
                :src="getCardImageUrl(card)"
                :alt="`${card.title} - ${selectedPeriod}`"
                class="stats-card-img"
                loading="lazy"
              />
            </a>
          </div>
        </div>
      </div>
    </div>

    <!-- 提示信息 -->
    <div class="card-hint">
      <span class="hint-icon">💡</span>
      <span class="hint-text">点击卡片查看详细数据 | 所有卡片时间范围同步</span>
    </div>
  </div>
</template>

<style scoped>
.org-stats-cards {
  width: 100%;
  padding: 20px 0;
}

/* 日期范围选择器 */
.period-selector {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 32px;
  padding: 16px 20px;
  background: var(--vp-c-bg-soft);
  border-radius: 12px;
  border: 1px solid var(--vp-c-divider);
  position: sticky;
  top: 80px;
  z-index: 10;
  backdrop-filter: blur(8px);
}

.selector-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--vp-c-text-1);
  white-space: nowrap;
}

.period-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.period-btn {
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-2);
  cursor: pointer;
  transition: all 0.2s ease;
}

.period-btn:hover {
  border-color: var(--vp-c-brand);
  color: var(--vp-c-brand);
  transform: translateY(-1px);
}

.period-btn.active {
  background: var(--vp-c-brand);
  border-color: var(--vp-c-brand);
  color: white;
}

/* 分组容器 */
.card-groups {
  display: flex;
  flex-direction: column;
  gap: 48px;
}

.card-group {
  border-radius: 16px;
  padding: 24px;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
}

.group-header {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--vp-c-divider);
}

.group-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--vp-c-text-1);
  margin: 0 0 8px 0;
}

.group-description {
  font-size: 14px;
  color: var(--vp-c-text-2);
  margin: 0;
  line-height: 1.5;
}

/* 卡片网格布局 */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 16px;
}

.card-wrapper {
  border-radius: 12px;
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  background: var(--vp-c-bg);
}

.card-wrapper:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

/* 不同尺寸卡片的网格占比 */
.size-full { grid-column: span 12; }
.size-half { grid-column: span 6; }
.size-auto { grid-column: span 6; }
.size-2x6 { grid-column: span 12; }
.size-4x7 { grid-column: span 7; }
.size-4x5 { grid-column: span 5; }
.size-4x3 { grid-column: span 6; }
.size-5x5 { grid-column: span 7; }
.size-3x6 { grid-column: span 5; }
.size-2x3 { grid-column: span 4; }
.size-2x2 { grid-column: span 4; }

.stats-card-link {
  display: block;
  width: 100%;
  height: 100%;
}

.stats-card-img {
  display: block;
  width: 100%;
  height: auto;
  transition: opacity 0.3s ease;
}

/* 提示信息 */
.card-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-top: 32px;
  padding: 12px;
  font-size: 13px;
  color: var(--vp-c-text-2);
  background: var(--vp-c-bg-soft);
  border-radius: 8px;
  border: 1px dashed var(--vp-c-divider);
}

.hint-icon {
  font-size: 14px;
}

.hint-text {
  opacity: 0.8;
}

/* 响应式设计 - 平板 */
@media (max-width: 960px) {
  .cards-grid {
    grid-template-columns: repeat(6, 1fr);
  }

  .size-full,
  .size-2x6,
  .size-4x7,
  .size-4x5,
  .size-5x5,
  .size-3x6 { grid-column: span 6; }

  .size-half,
  .size-auto,
  .size-4x3,
  .size-2x3,
  .size-2x2 { grid-column: span 3; }
}

/* 响应式设计 - 移动端 */
@media (max-width: 640px) {
  .period-selector {
    flex-direction: column;
    align-items: flex-start;
    position: relative;
    top: 0;
  }

  .period-buttons {
    width: 100%;
  }

  .period-btn {
    flex: 1;
    min-width: 60px;
    text-align: center;
  }

  .card-group {
    padding: 16px;
  }

  .group-title {
    font-size: 18px;
  }

  .cards-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .size-full,
  .size-half,
  .size-auto,
  .size-2x6,
  .size-4x7,
  .size-4x5,
  .size-4x3,
  .size-5x5,
  .size-3x6,
  .size-2x3,
  .size-2x2 {
    grid-column: span 1;
  }
}

/* 暗黑模式适配 */
.dark .card-wrapper {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.dark .card-wrapper:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
}
</style>
