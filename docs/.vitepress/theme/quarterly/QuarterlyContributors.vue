<template>
  <div class="quarterly-contributors-container">
    <!-- 季度选择器 - 始终显示 -->
    <div class="quarter-selector">
      <label>选择季度：</label>
      <select v-model="selectedYear" @change="loadData">
        <option v-for="year in availableYears" :key="year" :value="year">
          {{ year }}年
        </option>
      </select>
      <select v-model="selectedQuarter" @change="loadData">
        <option v-for="q in [1, 2, 3, 4]" :key="q" :value="q">
          第{{ q }}季度
        </option>
      </select>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>正在加载季度贡献者数据...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-state">
      <p>❌ 加载失败: {{ error }}</p>
      <button @click="loadData" class="retry-btn">重试</button>
    </div>

    <!-- 暂无数据状态 -->
    <div v-else-if="!data" class="empty-state">
      <div class="empty-icon">📭</div>
      <p class="empty-title">暂无数据</p>
      <p class="empty-desc">{{ selectedYear }}年第{{ selectedQuarter }}季度的数据尚未生成</p>
      <p class="empty-hint">请选择其他季度查看</p>
    </div>

    <!-- 内容区域 -->
    <div v-else class="content">
      <!-- 统计概览 -->
      <div class="stats-overview" v-if="data">
        <div class="stat-card">
          <div class="stat-icon">👥</div>
          <div class="stat-content">
            <div class="stat-value">{{ data.meta.total_contributors }}</div>
            <div class="stat-label">总贡献者</div>
            <div class="stat-desc">{{ selectedYear }}年Q{{ selectedQuarter }}</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🏆</div>
          <div class="stat-content">
            <div class="stat-value">{{ data.meta.outstanding_count }}</div>
            <div class="stat-label">卓越贡献者</div>
            <div class="stat-desc">≥{{ data.meta.thresholds.outstanding }}次有效commit</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">⭐</div>
          <div class="stat-content">
            <div class="stat-value">{{ data.meta.excellent_count }}</div>
            <div class="stat-label">优秀贡献者</div>
            <div class="stat-desc">≥{{ data.meta.thresholds.excellent }}次有效commit</div>
          </div>
        </div>
      </div>

      <!-- 卓越贡献者榜单 -->
      <div class="contributors-section" v-if="data && data.contributors.outstanding.length > 0">
        <h2 class="section-title">
          <span class="title-icon">🏆</span>
          卓越贡献者
          <span class="count-badge">{{ data.contributors.outstanding.length }}</span>
        </h2>
        <div class="contributors-grid">
          <ContributorCard
            v-for="contributor in data.contributors.outstanding"
            :key="contributor.username"
            :contributor="contributor"
            level="outstanding"
          />
        </div>
      </div>

      <!-- 优秀贡献者榜单 -->
      <div class="contributors-section" v-if="data && data.contributors.excellent.length > 0">
        <h2 class="section-title">
          <span class="title-icon">⭐</span>
          优秀贡献者
          <span class="count-badge">{{ data.contributors.excellent.length }}</span>
        </h2>
        <div class="contributors-grid">
          <ContributorCard
            v-for="contributor in data.contributors.excellent"
            :key="contributor.username"
            :contributor="contributor"
            level="excellent"
          />
        </div>
      </div>

      <!-- 数据更新时间 -->
      <div class="update-info" v-if="data">
        <p>📅 数据生成时间：{{ formatDate(data.meta.generated_at) }}</p>
        <p>💡 有效commit定义：至少包含一个文件新增行数 ≥ {{ data.meta.thresholds.valid_commit_threshold }} 行</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import ContributorCard from './ContributorCard.vue'

// 响应式数据
const loading = ref(true)
const error = ref(null)
const data = ref(null)
const selectedYear = ref(new Date().getFullYear())
const selectedQuarter = ref(Math.floor((new Date().getMonth() + 3) / 3))

// 可用年份（从2024年到当前年份）
const availableYears = computed(() => {
  const currentYear = new Date().getFullYear()
  const years = []
  for (let year = 2024; year <= currentYear; year++) {
    years.push(year)
  }
  return years.reverse()
})

// 格式化日期
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

// 加载数据
const loadData = async () => {
  try {
    loading.value = true
    error.value = null
    data.value = null

    const basePath = import.meta.env.BASE_URL || '/'
    const filename = `quarterly_contributors_${selectedYear.value}_Q${selectedQuarter.value}.json`
    const jsonPath = `${basePath}data/datawhalechina/${filename}`.replace(/\/+/g, '/')

    const response = await fetch(jsonPath)

    // 检查响应状态
    if (!response.ok) {
      data.value = null
      return
    }

    // 检查content-type是否为JSON
    const contentType = response.headers.get('content-type')
    if (!contentType || !contentType.includes('application/json')) {
      // 服务器返回了HTML页面（如404页面），视为数据不存在
      data.value = null
      return
    }

    data.value = await response.json()
  } catch (err) {
    // JSON解析错误也视为数据不存在
    if (err instanceof SyntaxError) {
      data.value = null
    } else {
      error.value = err.message
      console.error('加载季度贡献者数据失败:', err)
    }
  } finally {
    loading.value = false
  }
}

// 生命周期
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.quarterly-contributors-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.empty-title {
  font-size: 20px;
  font-weight: bold;
  color: var(--vp-c-text-1);
  margin: 10px 0;
}

.empty-desc {
  font-size: 16px;
  color: var(--vp-c-text-2);
  margin: 8px 0;
}

.empty-hint {
  font-size: 14px;
  color: var(--vp-c-text-3);
  margin: 8px 0;
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
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

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

.retry-btn:hover {
  background: var(--vp-c-brand-2);
}

.quarter-selector {
  background: var(--vp-c-bg-soft);
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 30px;
  display: flex;
  align-items: center;
  gap: 15px;
}

.quarter-selector label {
  font-weight: 500;
  color: var(--vp-c-text-1);
}

.quarter-selector select {
  padding: 8px 12px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  font-size: 14px;
  cursor: pointer;
}

.stats-overview {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-bottom: 40px;
}

.stat-card {
  background: var(--vp-c-bg-soft);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  font-size: 36px;
  line-height: 1;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: var(--vp-c-brand-1);
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--vp-c-text-1);
  margin-top: 2px;
}

.stat-desc {
  font-size: 11px;
  color: var(--vp-c-text-2);
  margin-top: 2px;
}

.contributors-section {
  margin-bottom: 50px;
}

.section-title {
  font-size: 24px;
  font-weight: bold;
  color: var(--vp-c-text-1);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.title-icon {
  font-size: 28px;
}

.count-badge {
  background: var(--vp-c-brand-1);
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: normal;
}

.contributors-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.update-info {
  text-align: center;
  padding: 20px;
  background: var(--vp-c-bg-soft);
  border-radius: 8px;
  color: var(--vp-c-text-2);
  font-size: 14px;
  margin-top: 40px;
}

.update-info p {
  margin: 5px 0;
}

@media (max-width: 768px) {
  .quarterly-contributors-container {
    padding: 15px;
  }

  .quarter-selector {
    flex-direction: column;
    align-items: stretch;
  }

  .stats-overview {
    grid-template-columns: 1fr;
  }

  .contributors-grid {
    grid-template-columns: 1fr;
  }
}
</style>
