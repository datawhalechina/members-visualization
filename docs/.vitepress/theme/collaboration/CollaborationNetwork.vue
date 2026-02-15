<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

const members = ref([])
const loading = ref(true)
const error = ref(null)
const isDark = ref(false)
const chartRef = ref(null)
const minRepos = ref(3)
const selectedDomain = ref('')
let chart = null
let resizeHandler = null
let themeObserver = null

// 所有研究方向
const allDomains = computed(() => {
  const domains = new Set()
  members.value.forEach(m => {
    if (Array.isArray(m.domain)) {
      m.domain.forEach(d => domains.add(d))
    }
  })
  return Array.from(domains).sort()
})

// 构建协作图数据
const graphData = computed(() => {
  // 1. 过滤成员
  const filtered = members.value.filter(m => {
    const repos = Array.isArray(m.repositories) ? m.repositories : []
    if (repos.length < minRepos.value) return false
    if (selectedDomain.value && Array.isArray(m.domain)) {
      if (!m.domain.includes(selectedDomain.value)) return false
    }
    return true
  })

  // 2. 构建 repo -> members 倒排索引
  const repoToMembers = {}
  filtered.forEach(m => {
    m.repositories.forEach(repo => {
      if (!repoToMembers[repo]) repoToMembers[repo] = []
      repoToMembers[repo].push(m)
    })
  })

  // 3. 构建边（两两配对）
  const edgeMap = new Map()
  for (const [repo, memberList] of Object.entries(repoToMembers)) {
    for (let i = 0; i < memberList.length; i++) {
      for (let j = i + 1; j < memberList.length; j++) {
        const a = memberList[i].id
        const b = memberList[j].id
        const key = a < b ? `${a}|${b}` : `${b}|${a}`
        if (!edgeMap.has(key)) {
          edgeMap.set(key, { source: a < b ? a : b, target: a < b ? b : a, count: 0, repos: [] })
        }
        const edge = edgeMap.get(key)
        edge.count++
        edge.repos.push(repo)
      }
    }
  }

  // 4. 计算度数
  const degreeMap = {}
  edgeMap.forEach(edge => {
    degreeMap[edge.source] = (degreeMap[edge.source] || 0) + 1
    degreeMap[edge.target] = (degreeMap[edge.target] || 0) + 1
  })

  // 5. 生成节点
  const nodes = filtered.map(m => {
    const displayName = (m.name && m.name.trim() && m.name !== 'null' && m.name !== 'None') ? m.name : m.id
    const repoCount = m.repositories.length
    const primaryDomain = (Array.isArray(m.domain) && m.domain.length > 0) ? m.domain[0] : '其他'
    const degree = degreeMap[m.id] || 0
    return {
      id: m.id,
      name: displayName,
      symbolSize: Math.max(12, Math.min(55, Math.log2(repoCount + 1) * 12)),
      category: primaryDomain,
      value: repoCount,
      degree,
      repositories: m.repositories,
      domains: m.domain || [],
      label: { show: degree >= 3 }
    }
  })

  // 6. 生成边
  const edges = Array.from(edgeMap.values()).map(e => ({
    source: e.source,
    target: e.target,
    value: e.count,
    sharedRepos: e.repos,
    lineStyle: {
      width: Math.max(1, Math.min(8, e.count * 1.5)),
      opacity: Math.min(0.8, 0.15 + e.count * 0.1)
    }
  }))

  // 7. 分类
  const domainSet = new Set(nodes.map(n => n.category))
  const categories = Array.from(domainSet).sort().map(d => ({ name: d }))

  return { nodes, edges, categories }
})

const domainColors = [
  '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de',
  '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc', '#13c2c2'
]

const checkDarkMode = () => {
  isDark.value = document.documentElement.classList.contains('dark')
}

const createChartOption = () => {
  const { nodes, edges, categories } = graphData.value
  const textColor = isDark.value ? '#eee' : '#333'
  const subTextColor = isDark.value ? '#aaa' : '#666'

  return {
    backgroundColor: 'transparent',
    title: {
      text: '仓库协作网络图',
      subtext: `${nodes.length} 位成员 · ${edges.length} 条协作关系\n节点大小 = 参与仓库数 · 连线粗细 = 共同仓库数`,
      left: 'center',
      top: '2%',
      textStyle: { fontSize: 18, fontWeight: 'bold', color: textColor },
      subtextStyle: { fontSize: 12, color: subTextColor, lineHeight: 20 }
    },
    tooltip: {
      trigger: 'item',
      confine: true,
      formatter: (params) => {
        if (params.dataType === 'node') {
          const d = params.data
          const repoList = d.repositories.slice(0, 6).join(', ')
          const more = d.repositories.length > 6 ? ` 等${d.repositories.length}个` : ''
          return `<strong>${d.name}</strong> (${d.id})<br/>` +
            `参与仓库: ${d.value} 个<br/>` +
            `协作者: ${d.degree} 人<br/>` +
            `研究方向: ${d.domains.join(', ') || '未知'}<br/>` +
            `仓库: ${repoList}${more}`
        }
        if (params.dataType === 'edge') {
          const d = params.data
          return `<strong>${d.source}</strong> ↔ <strong>${d.target}</strong><br/>` +
            `共同仓库: ${d.value} 个<br/>` +
            d.sharedRepos.join(', ')
        }
      }
    },
    legend: {
      data: categories.map(c => c.name),
      right: '3%',
      top: '10%',
      orient: 'vertical',
      type: 'scroll',
      pageIconColor: textColor,
      textStyle: { color: textColor, fontSize: 11 }
    },
    series: [{
      type: 'graph',
      layout: 'circular',
      data: nodes,
      links: edges,
      categories: categories.map((c, i) => ({
        name: c.name,
        itemStyle: { color: domainColors[i % domainColors.length] }
      })),
      roam: true,
      draggable: true,
      scaleLimit: { min: 0.5, max: 3 },
      circular: {
        rotateLabel: true
      },
      label: {
        position: 'right',
        formatter: '{b}',
        fontSize: 10,
        color: textColor
      },
      lineStyle: {
        color: 'source',
        curveness: 0.2,
        opacity: 0.3
      },
      emphasis: {
        focus: 'adjacency',
        lineStyle: { width: 6, opacity: 0.9 },
        label: { show: true, fontSize: 13, fontWeight: 'bold' }
      },
      left: '5%',
      right: '12%',
      top: '8%',
      bottom: '5%'
    }]
  }
}

const initChart = () => {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value, isDark.value ? 'dark' : 'light')
  chart.setOption(createChartOption())
}

const refreshChart = () => {
  if (chart && chartRef.value) {
    chart.dispose()
    chart = echarts.init(chartRef.value, isDark.value ? 'dark' : 'light')
    chart.setOption(createChartOption())
  }
}

// 筛选变化时更新图表
watch(graphData, () => {
  if (chart) {
    chart.setOption(createChartOption(), true)
  }
})

onMounted(async () => {
  try {
    checkDarkMode()

    // 监听主题变化
    if (typeof window !== 'undefined') {
      themeObserver = new MutationObserver(() => {
        const newIsDark = document.documentElement.classList.contains('dark')
        if (newIsDark !== isDark.value) {
          isDark.value = newIsDark
          setTimeout(refreshChart, 100)
        }
      })
      themeObserver.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['class']
      })

      resizeHandler = () => chart?.resize()
      window.addEventListener('resize', resizeHandler)
    }

    await nextTick()

    // 加载数据
    const basePath = import.meta.env.BASE_URL || '/'
    const jsonPath = `${basePath}data/members.json`.replace(/\/+/g, '/')
    const res = await fetch(jsonPath)
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`)

    const responseJSON = await res.json()
    members.value = responseJSON.map(item => {
      Object.keys(item).forEach(key => {
        let value = item[key] || ''
        if (typeof value === 'string') {
          value = value.trim().replace(/^"|"$/g, '')
        }
        if (['domain', 'repositories'].includes(key)) {
          value = value ? value.split(';').map(d => d.trim()).filter(d => d) : []
        }
        item[key] = value
      })
      return item
    })

    loading.value = false
    await nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))
    initChart()
  } catch (err) {
    console.error('加载数据失败:', err)
    error.value = err.message
    loading.value = false
  }
})

onUnmounted(() => {
  chart?.dispose()
  if (resizeHandler) window.removeEventListener('resize', resizeHandler)
  themeObserver?.disconnect()
})
</script>

<template>
  <div class="collaboration-network">
    <div v-if="loading" class="status-box loading"><p>正在加载数据...</p></div>
    <div v-else-if="error" class="status-box error"><p>加载失败: {{ error }}</p></div>
    <div v-else>
      <!-- 统计卡片 -->
      <div class="stats-row">
        <div class="stat-card">
          <div class="stat-number">{{ graphData.nodes.length }}</div>
          <div class="stat-label">协作成员</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ graphData.edges.length }}</div>
          <div class="stat-label">协作关系</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ graphData.categories.length }}</div>
          <div class="stat-label">研究方向</div>
        </div>
      </div>

      <!-- 筛选控件 -->
      <div class="filter-controls">
        <div class="filter-item">
          <label class="filter-label">最少参与仓库数: <strong>{{ minRepos }}</strong></label>
          <input type="range" v-model.number="minRepos" min="1" max="10" step="1" class="range-slider" />
          <div class="range-ticks">
            <span>1</span><span>5</span><span>10</span>
          </div>
        </div>
        <div class="filter-item">
          <label class="filter-label">研究方向</label>
          <select v-model="selectedDomain" class="domain-select">
            <option value="">全部</option>
            <option v-for="d in allDomains" :key="d" :value="d">{{ d }}</option>
          </select>
        </div>
      </div>

      <!-- 图表 -->
      <div class="chart-container">
        <div ref="chartRef" class="chart"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.collaboration-network {
  width: 100%;
  padding: 20px 0;
}

.status-box {
  text-align: center;
  padding: 60px 20px;
  border-radius: 12px;
  margin: 20px 0;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-border);
}

.status-box.loading {
  border-color: var(--vp-c-brand-1);
  color: var(--vp-c-brand-1);
}

.status-box.error {
  border-color: var(--vp-c-danger-1);
  color: var(--vp-c-danger-1);
}

.stats-row {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  flex: 1;
  text-align: center;
  padding: 20px 16px;
  border-radius: 12px;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-border);
}

.stat-number {
  font-size: 28px;
  font-weight: 700;
  color: var(--vp-c-brand-1);
}

.stat-label {
  font-size: 13px;
  color: var(--vp-c-text-2);
  margin-top: 4px;
}

.filter-controls {
  display: flex;
  gap: 24px;
  margin-bottom: 24px;
  padding: 20px;
  background: var(--vp-c-bg-soft);
  border-radius: 12px;
  border: 1px solid var(--vp-c-border);
  align-items: flex-start;
  flex-wrap: wrap;
}

.filter-item {
  flex: 1;
  min-width: 200px;
}

.filter-label {
  display: block;
  font-size: 14px;
  color: var(--vp-c-text-1);
  margin-bottom: 8px;
}

.range-slider {
  width: 100%;
  cursor: pointer;
  accent-color: var(--vp-c-brand-1);
}

.range-ticks {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--vp-c-text-3);
  margin-top: 2px;
}

.domain-select {
  width: 100%;
  padding: 10px 14px;
  border: 2px solid var(--vp-c-border);
  border-radius: 8px;
  font-size: 14px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  cursor: pointer;
  transition: border-color 0.3s ease;
}

.domain-select:focus {
  outline: none;
  border-color: var(--vp-c-brand-1);
}

.chart-container {
  border: 1px solid var(--vp-c-border);
  border-radius: 12px;
  padding: 16px;
  background: var(--vp-c-bg);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  overflow: visible;
  min-height: 1140px;
}

.chart {
  width: 100%;
  height: 1100px;
  min-height: 900px;
}

@media (max-width: 768px) {
  .stats-row {
    flex-direction: column;
    gap: 12px;
  }

  .filter-controls {
    flex-direction: column;
    gap: 16px;
  }

  .filter-item {
    min-width: auto;
  }

  .chart {
    height: 500px;
    min-height: 400px;
  }
}
</style>
