<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import * as echarts from 'echarts'

// 动态导入 echarts-wordcloud
const wordCloudLoaded = ref(false)

// 暗黑模式检测
const isDark = ref(false)

const pieRef = ref(null)
const barRef = ref(null)
const wordCloudRef = ref(null)
const networkRef = ref(null)
const loading = ref(true)
const error = ref(null)
const members = ref([])
const domainCount = ref({})

let pieChart = null
let barChart = null
let wordCloudChart = null
let networkChart = null

// 暗黑模式检测函数
const checkDarkMode = () => {
  if (typeof window !== 'undefined') {
    isDark.value = document.documentElement.classList.contains('dark')
  }
}

// 获取ECharts主题
const getEChartsTheme = () => {
  return isDark.value ? 'dark' : 'light'
}

// 获取主题相关的颜色配置
const getThemeColors = () => {
  if (isDark.value) {
    return {
      textColor: '#ffffff',
      backgroundColor: '#1a1a1a',
      axisLineColor: '#484848',
      splitLineColor: '#484848'
    }
  } else {
    return {
      textColor: '#333333',
      backgroundColor: '#ffffff',
      axisLineColor: '#e0e0e0',
      splitLineColor: '#f0f0f0'
    }
  }
}

// 重新创建图表配置的函数
const createPieChartOption = () => {
  const pieData = Object.entries(domainCount.value)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([k, v]) => ({ name: k, value: v }))

  return {
    title: {
      text: '研究方向分布',
      subtext: '成员研究方向统计',
      left: 'center',
      textStyle: {
        fontSize: 20,
        fontWeight: 'bold',
        color: getThemeColors().textColor
      },
      subtextStyle: {
        fontSize: 14,
        color: isDark.value ? '#cccccc' : '#666666'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: function (params) {
        const percent = params.percent
        const value = params.value
        return `${params.seriesName}<br/>${params.name}: ${value} 人 (${percent}%)`
      }
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'middle',
      itemGap: 12,
      textStyle: {
        fontSize: 12,
        color: getThemeColors().textColor
      }
    },
    series: [{
      name: '研究方向',
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['60%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 20,
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: false
      },
      data: pieData,
      animationType: 'scale',
      animationEasing: 'elasticOut',
      animationDelay: function (idx) {
        return Math.random() * 200
      }
    }]
  }
}

const createBarChartOption = () => {
  const domainEntries = Object.entries(domainCount.value).sort((a, b) => b[1] - a[1]).slice(0, 15)

  return {
    title: {
      text: '研究方向统计',
      subtext: `平均每人涉及 ${stats.value.avgDomainsPerMember} 个方向`,
      left: 'center',
      textStyle: {
        fontSize: 20,
        fontWeight: 'bold',
        color: getThemeColors().textColor
      },
      subtextStyle: {
        fontSize: 14,
        color: isDark.value ? '#cccccc' : '#666666'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
        shadowStyle: {
          color: 'rgba(0, 0, 0, 0.1)'
        }
      },
      formatter: function (params) {
        const data = params[0]
        const total = members.value.length
        const percent = ((data.value / total) * 100).toFixed(1)
        return `${data.name}<br/>成员数量: ${data.value} 人<br/>占比: ${percent}%`
      }
    },
    grid: {
      left: '5%',
      right: '5%',
      bottom: '15%',
      top: '20%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: domainEntries.map(([k, v]) => k),
      axisLabel: {
        rotate: 45,
        interval: 0,
        fontSize: 12,
        color: getThemeColors().textColor
      },
      axisLine: {
        lineStyle: {
          color: getThemeColors().axisLineColor
        }
      }
    },
    yAxis: {
      type: 'value',
      name: '成员数量',
      nameTextStyle: {
        color: getThemeColors().textColor,
        fontSize: 12
      },
      axisLabel: {
        color: getThemeColors().textColor
      },
      axisLine: {
        lineStyle: {
          color: getThemeColors().axisLineColor
        }
      },
      splitLine: {
        lineStyle: {
          color: getThemeColors().splitLineColor
        }
      }
    },
    series: [{
      name: '成员数量',
      type: 'bar',
      barWidth: '60%',
      data: domainEntries.map(([k, v], index) => ({
        value: v,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: `hsl(${(index * 30) % 360}, 70%, 60%)` },
            { offset: 1, color: `hsl(${(index * 30) % 360}, 70%, 40%)` }
          ])
        }
      })),
      animationDelay: function (idx) {
        return idx * 50
      }
    }]
  }
}

const createWordCloudOption = () => {
  // 确保数据存在且有效
  const wordCloudData = Object.entries(domainCount.value)
    .filter(([k, v]) => k && k.trim() && v > 0)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 30) // 减少词云数量，避免过于拥挤
    .map(([k, v], index) => ({
      name: k.trim(),
      value: v,
      textStyle: {
        fontSize: Math.max(14, Math.min(40, v * 4 + 16)),
        // 使用固定的颜色数组，根据索引分配颜色
        color: getWordCloudColors()[index % getWordCloudColors().length]
      }
    }))

  console.log('词云数据:', wordCloudData)

  return {
    title: {
      text: '研究方向词云',
      subtext: '字体大小反映热门程度',
      left: 'center',
      textStyle: {
        fontSize: 20,
        fontWeight: 'bold',
        color: getThemeColors().textColor
      },
      subtextStyle: {
        fontSize: 14,
        color: isDark.value ? '#cccccc' : '#666666'
      }
    },
    tooltip: {
      formatter: function (params) {
        return `${params.name}: ${params.value} 人`
      },
      backgroundColor: isDark.value ? 'rgba(0, 0, 0, 0.8)' : 'rgba(255, 255, 255, 0.9)',
      borderColor: isDark.value ? '#666' : '#ccc',
      textStyle: {
        color: isDark.value ? '#fff' : '#333'
      }
    },
    backgroundColor: 'transparent',
    series: [{
      type: 'wordCloud',
      gridSize: 4,
      sizeRange: [14, 40],
      rotationRange: [-45, 45],
      rotationStep: 15,
      shape: 'circle',
      left: 'center',
      top: 'center',
      width: '85%',
      height: '75%',
      right: null,
      bottom: null,
      drawOutOfBound: false,
      layoutAnimation: true,
      textStyle: {
        fontFamily: 'Arial, Microsoft YaHei, sans-serif',
        fontWeight: 'bold'
      },
      emphasis: {
        focus: 'self',
        textStyle: {
          shadowBlur: 8,
          shadowColor: isDark.value ? 'rgba(255, 255, 255, 0.5)' : 'rgba(0, 0, 0, 0.5)',
          textBorderColor: isDark.value ? '#fff' : '#000',
          textBorderWidth: 1
        }
      },
      data: wordCloudData
    }]
  }
}

// 获取词云颜色的辅助函数
const getWordCloudColors = () => {
  if (isDark.value) {
    return [
      '#6b9bd2', '#a5d86c', '#ffcc5c', '#ff7875', '#87ceeb',
      '#52c41a', '#ff9c6e', '#b37feb', '#f759ab', '#36cfc9',
      '#ffc53d', '#ff85c0', '#95de64', '#5cdbd3', '#85a5ff'
    ]
  } else {
    return [
      '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de',
      '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc', '#13c2c2',
      '#faad14', '#eb2f96', '#52c41a', '#1890ff', '#722ed1'
    ]
  }
}

const createNetworkChartOption = () => {
  // 过滤和清理数据，确保没有重复或无效的节点
  const validMembers = members.value.filter(m => m && m.name && (m.id || m.name))
  const validDomains = Object.keys(domainCount.value).filter(d => d && d.trim())

  // 创建成员节点，使用Set确保唯一性
  const memberNodeIds = new Set()
  const nodes = validMembers.map(m => {
    const nodeId = `member_${m.id || m.name}`
    if (memberNodeIds.has(nodeId)) {
      console.warn(`重复的成员节点ID: ${nodeId}`)
      return null
    }
    memberNodeIds.add(nodeId)
    return {
      id: nodeId,
      name: m.name,
      category: 0,
      // 对数变换控制节点大小
      symbolSize: Math.max(20, Math.min(50, Math.log2((m.domain && Array.isArray(m.domain) ? m.domain.length : 1) + 1) * 15)),
      itemStyle: {
        color: '#5470c6'
      }
    }
  }).filter(Boolean) // 移除null值

  // 创建研究方向节点，使用对数变换控制大小
  const domainNodeIds = new Set()
  const domainNodes = validDomains.map(d => {
    const nodeId = `domain_${d}`
    if (domainNodeIds.has(nodeId)) {
      console.warn(`重复的研究方向节点ID: ${nodeId}`)
      return null
    }
    domainNodeIds.add(nodeId)
    const count = domainCount.value[d] || 1
    return {
      id: nodeId,
      name: d,
      category: 1,
      // 对数变换控制节点大小，避免过大
      symbolSize: Math.max(25, Math.min(80, Math.log2(count + 1) * 20)),
      itemStyle: {
        color: '#91cc75'
      }
    }
  }).filter(Boolean)

  // 合并所有节点
  const allNodes = [...nodes, ...domainNodes]

  // 创建边，确保源和目标节点都存在
  const edges = []
  const edgeSet = new Set() // 防止重复边

  validMembers.forEach(m => {
    const memberNodeId = `member_${m.id || m.name}`
    if (!memberNodeIds.has(memberNodeId)) return

    if (m.domain && Array.isArray(m.domain)) {
      m.domain.forEach(d => {
        if (d && d.trim()) {
          const domainNodeId = `domain_${d}`
          const edgeKey = `${memberNodeId}-${domainNodeId}`

          if (!edgeSet.has(edgeKey) && domainNodeIds.has(domainNodeId)) {
            edgeSet.add(edgeKey)
            edges.push({
              source: memberNodeId,
              target: domainNodeId,
              lineStyle: {
                color: isDark.value ? '#666' : '#999',
                width: 2,
                opacity: 0.6
              }
            })
          }
        }
      })
    }
  })

  return {
    tooltip: {
      trigger: 'item',
      formatter: function (params) {
        if (params.dataType === 'node') {
          if (params.data.category === 0) {
            const memberDomains = members.value.find(m => m.name === params.data.name)?.domain || []
            return `成员: ${params.data.name}<br/>研究方向: ${memberDomains.join(', ')}`
          } else {
            const count = domainCount.value[params.data.name] || 0
            return `研究方向: ${params.data.name}<br/>成员数量: ${count} 人`
          }
        }
        return params.data.name
      }
    },
    legend: {
      data: ['成员', '研究方向'],
      right: '3%',
      top: '2%',
      orient: 'vertical',
      itemGap: 15,
      textStyle: {
        color: getThemeColors().textColor,
        fontSize: 12
      },
      itemWidth: 14,
      itemHeight: 14
    },
    series: [{
      name: '关系网络',
      type: 'graph',
      layout: 'force',
      data: allNodes,
      links: edges,
      categories: [
        { name: '成员', itemStyle: { color: '#5470c6' } },
        { name: '研究方向', itemStyle: { color: '#91cc75' } }
      ],
      roam: true, // 保留缩放功能
      focusNodeAdjacency: true,
      draggable: true, // 保留拖拽功能
      scaleLimit: { min: 0.5, max: 3 },
      center: ['50%', '50%'],
      force: {
        repulsion: 250,
        gravity: 0.6,
        edgeLength: [20, 80],
        layoutAnimation: true,
        friction: 0.8,
        initLayout: 'circular'
      },
      left: 80,
      right: 120,
      top: 40,
      bottom: 40,
      label: {
        show: true,
        position: 'right',
        formatter: '{b}',
        fontSize: 10,
        color: getThemeColors().textColor,
        distance: 5
      },
      lineStyle: {
        color: 'source',
        curveness: 0.2,
        opacity: 0.6
      },
      emphasis: {
        focus: 'adjacency',
        lineStyle: {
          width: 6,
          opacity: 0.8
        }
      }
    }]
  }
}

// 刷新所有图表的函数
const refreshAllCharts = () => {
  try {
    console.log('开始刷新所有图表以适应主题变化')

    // 重新初始化饼图
    if (pieChart && pieRef.value) {
      pieChart.dispose()
      pieChart = echarts.init(pieRef.value, getEChartsTheme())
      pieChart.setOption(createPieChartOption())
    }

    // 重新初始化柱状图
    if (barChart && barRef.value) {
      barChart.dispose()
      barChart = echarts.init(barRef.value, getEChartsTheme())
      barChart.setOption(createBarChartOption())
    }

    // 重新初始化词云图
    if (wordCloudChart && wordCloudRef.value && wordCloudLoaded.value) {
      wordCloudChart.dispose()
      wordCloudChart = echarts.init(wordCloudRef.value, getEChartsTheme())
      wordCloudChart.setOption(createWordCloudOption())
    }

    // 重新初始化网络图
    if (networkChart && networkRef.value) {
      networkChart.dispose()
      networkChart = echarts.init(networkRef.value, getEChartsTheme())
      networkChart.setOption(createNetworkChartOption())
    }

    console.log('所有图表已刷新以适应主题变化')
  } catch (error) {
    console.error('刷新图表时出错:', error)
  }
}

// 统计信息
const stats = computed(() => {
  const totalMembers = members.value.length
  const totalDomains = Object.keys(domainCount.value).length
  const avgDomainsPerMember = totalMembers > 0 ?
    (members.value.reduce((sum, m) => sum + m.domain.length, 0) / totalMembers).toFixed(1) : 0

  return {
    totalMembers,
    totalDomains,
    avgDomainsPerMember,
    mostPopularDomain: Object.entries(domainCount.value).sort((a, b) => b[1] - a[1])[0]?.[0] || '暂无'
  }
})

onMounted(async () => {
  try {
    // 检测暗黑模式
    checkDarkMode()

    // 监听主题变化
    if (typeof window !== 'undefined') {
      const observer = new MutationObserver(() => {
        const newIsDark = document.documentElement.classList.contains('dark')
        if (newIsDark !== isDark.value) {
          isDark.value = newIsDark
          // 重新初始化所有图表以应用新主题
          setTimeout(() => {
            refreshAllCharts()
          }, 100)
        }
      })
      observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['class']
      })
    }

    // 等待DOM完全渲染
    await nextTick()

    // 动态获取 CSV 数据路径，适配开发和生产环境
    const basePath = import.meta.env.BASE_URL || '/'
    const jsonPath = `${basePath}data/members.json`.replace(/\/+/g, '/')

    console.log('Fetching data from:', jsonPath)

    const res = await fetch(jsonPath)
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`)
    }

    const responseJSON = await res.json()
    const parsedMembers = responseJSON.map(item => {
      Object.keys(item).forEach((key) => {
        let value = item[key] || '';
        if (typeof value === 'string') {
          value = value.trim().replace(/^"|"$/g, '')
        }
        if (['domain', 'repositories'].includes(key)) {
          if (value) {
            value = value.split(';').map(d => d.trim()).filter(d => d)
          } else {
            value = []
          }
        }
        item[key] = value
      })
      return item
    })

    members.value = parsedMembers
    console.log('Parsed members:', members.value)

    // 统计领域分布
    const domainCountData = {}
    members.value.forEach(m => {
      m.domain.forEach(d => {
        if (d) {
          domainCountData[d] = (domainCountData[d] || 0) + 1
        }
      })
    })

    domainCount.value = domainCountData
    console.log('Domain count:', domainCount.value)

    // 先设置loading为false，让DOM渲染
    loading.value = false

    // 等待DOM渲染完成
    await nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // 重新启用词云插件，添加超时和错误处理
    try {
      console.log('开始加载词云插件...')

      // 设置加载超时
      const loadTimeout = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('词云插件加载超时')), 5000)
      })

      // 动态加载词云插件
      const loadWordCloud = async () => {
        if (typeof window !== 'undefined') {
          // 客户端环境
          const wordCloudModule = await import('echarts-wordcloud')
          console.log('词云插件加载成功 (客户端)', wordCloudModule)
          return true
        }
        return false
      }

      // 使用Promise.race来实现超时控制
      await Promise.race([loadWordCloud(), loadTimeout])

      wordCloudLoaded.value = true
      console.log('词云插件已成功启用')
    } catch (e) {
      console.error('词云插件加载失败:', e)
      wordCloudLoaded.value = false
      console.warn('词云图将不会显示，但不影响其他功能')
    }

    // ---------------- 增强饼图 ----------------
    // 等待DOM更新后再初始化图表
    await nextTick()

    // 使用更可靠的重试机制
    const initPieChartWithRetry = async (retries = 5) => {
      if (!pieRef.value && retries > 0) {
        console.log(`饼图容器未找到，等待DOM渲染... (剩余重试: ${retries})`)
        await new Promise(resolve => setTimeout(resolve, 200))
        return initPieChartWithRetry(retries - 1)
      }

      if (!pieRef.value) {
        console.error('饼图容器最终未找到，跳过饼图初始化')
        return
      }

      initPieChart()
    }

    function initPieChart() {
      try {
        if (pieChart) {
          pieChart.dispose()
        }

        // 重新初始化图表实例
        pieChart = echarts.init(pieRef.value, getEChartsTheme())

        if (!pieChart) {
          console.error('饼图初始化失败')
          return
        }

        pieChart.setOption(createPieChartOption())
      } catch (error) {
        console.error('饼图初始化出错:', error)
      }
    }

    // 启动饼图初始化
    await initPieChartWithRetry()

    // ---------------- 增强柱状图 ----------------
    if (!barRef.value) {
      console.warn('柱状图容器未找到，跳过柱状图初始化')
    } else {
      try {
        if (barChart) {
          barChart.dispose()
        }
        barChart = echarts.init(barRef.value, getEChartsTheme())

        if (!barChart) {
          console.error('柱状图初始化失败')
          return
        }
        barChart.setOption(createBarChartOption())
      } catch (error) {
        console.error('柱状图初始化出错:', error)
      }
    }

    // ---------------- 词云图 ----------------
    if (wordCloudLoaded.value && wordCloudRef.value) {
      try {
        console.log('开始初始化词云图...')
        console.log('词云数据条目数:', Object.entries(domainCount.value).length)

        // 确保容器有尺寸
        const container = wordCloudRef.value
        console.log('词云容器尺寸:', {
          width: container.offsetWidth,
          height: container.offsetHeight,
          clientWidth: container.clientWidth,
          clientHeight: container.clientHeight
        })

        if (container.offsetWidth === 0 || container.offsetHeight === 0) {
          console.warn('词云图容器尺寸为0，设置默认尺寸')
          container.style.width = '100%'
          container.style.height = '450px'
          // 等待样式生效
          await nextTick()
        }

        // 初始化图表实例
        if (wordCloudChart) {
          wordCloudChart.dispose()
        }
        wordCloudChart = echarts.init(container, getEChartsTheme())

        if (!wordCloudChart) {
          throw new Error('词云图表实例创建失败')
        }

        // 设置配置选项
        const option = createWordCloudOption()
        console.log('词云图配置数据项数量:', option.series[0].data.length)
        console.log('词云图前5项数据:', option.series[0].data.slice(0, 5))

        wordCloudChart.setOption(option, true)

        // 强制重新渲染
        setTimeout(() => {
          if (wordCloudChart && !wordCloudChart.isDisposed()) {
            wordCloudChart.resize()
            console.log('词云图重新调整尺寸完成')
          }
        }, 200)

        console.log('词云图初始化完成')
      } catch (error) {
        console.error('词云图初始化失败:', error)
        console.error('错误堆栈:', error.stack)
      }
    } else {
      console.warn('词云图跳过:', {
        wordCloudLoaded: wordCloudLoaded.value,
        wordCloudRef: !!wordCloudRef.value,
        containerExists: !!wordCloudRef.value,
        containerVisible: wordCloudRef.value ? wordCloudRef.value.offsetWidth > 0 : false
      })
    }

    // ---------------- 增强关系网络图 ----------------

    if (!networkRef.value) {
      console.warn('网络图容器未找到，跳过网络图初始化')
    } else {
      try {
        networkChart = echarts.init(networkRef.value, getEChartsTheme())

        if (!networkChart) {
          console.error('网络图初始化失败')
          return
        }

        const networkOption = createNetworkChartOption()
        networkChart.setOption(networkOption)
      } catch (error) {
        console.error('网络图初始化出错:', error)
      }
    }

    // 响应式处理
    window.handleResize = () => {
      pieChart?.resize()
      barChart?.resize()
      wordCloudChart?.resize()
      networkChart?.resize()
    }
    window.addEventListener('resize', window.handleResize)

  } catch (err) {
    console.error('Error loading data:', err)
    error.value = err.message
    loading.value = false
  }
})

onUnmounted(() => {
  // 清理图表实例
  pieChart?.dispose()
  barChart?.dispose()
  wordCloudChart?.dispose()
  networkChart?.dispose()

  // 移除事件监听器
  window.removeEventListener('resize', window.handleResize)
})
</script>

<template>
  <div class="charts">
    <div v-if="loading" class="loading">
      <p>正在加载数据...</p>
    </div>

    <div v-else-if="error" class="error">
      <p>加载数据时出错: {{ error }}</p>
    </div>

    <div v-else>
      <!-- 统计概览 -->
      <div class="stats-overview">
        <div class="stat-card">
          <div class="stat-number">{{ stats.totalMembers }}</div>
          <div class="stat-label">总成员数</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ stats.totalDomains }}</div>
          <div class="stat-label">研究方向数</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ stats.avgDomainsPerMember }}</div>
          <div class="stat-label">平均方向数/人</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ stats.mostPopularDomain }}</div>
          <div class="stat-label">最热门方向</div>
        </div>
      </div>

      <!-- 饼图 -->
      <div class="chart-container">
        <div ref="pieRef" class="chart"></div>
      </div>

      <!-- 柱状图 -->
      <div class="chart-container">
        <div ref="barRef" class="chart"></div>
      </div>

      <!-- 词云图 -->
      <div v-if="wordCloudLoaded" class="chart-container">
        <div ref="wordCloudRef" class="chart" data-chart-type="wordcloud"></div>
      </div>
      <div v-else class="chart-container">
        <div class="loading">
          <p>词云插件加载中...</p>
        </div>
      </div>

      <!-- 关系网络图 -->
      <div class="chart-container">
        <div class="chart-title">
          <h3>成员与研究方向关系网络</h3>
          <p>节点大小反映连接数量，支持拖拽和缩放</p>
        </div>
        <div ref="networkRef" class="chart-large" data-chart-type="network"></div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.charts {
  width: 100%;
  padding: 20px 0;
  clear: both;
  overflow: hidden;
  position: relative;
  z-index: 1;
}

.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 3rem;
}

.stat-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 24px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.stat-number {
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: 8px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.stat-label {
  font-size: 1rem;
  opacity: 0.9;
  font-weight: 500;
}

.chart-container {
  margin-bottom: 4rem;
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  padding: 32px;
  background: var(--vp-c-bg);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  transition: box-shadow 0.3s ease, border-color 0.3s ease, background-color 0.3s ease;
  overflow: hidden;
  position: relative;
  min-height: 600px;
}

.chart-container:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

/* 暗黑模式适配 */
.dark .chart-container {
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.dark .chart-container:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.chart {
  width: 100%;
  height: 550px;
  min-height: 500px;
  max-width: 100%;
  overflow: hidden;
  position: relative;
}

.chart-large {
  width: 100%;
  height: 800px;
  min-height: 750px;
  max-width: 100%;
  overflow: hidden;
  position: relative;
  padding: 20px;
  box-sizing: border-box;
}

/* 确保chart-large内部的ECharts容器也受约束 */
.chart-large>div {
  width: 100% !important;
  height: 100% !important;
  max-width: 100%;
  max-height: 100%;
  overflow: hidden;
}

/* 图表标题（HTML 方式，避免与 ECharts 画布重叠） */
.chart-title {
  text-align: center;
  margin-bottom: 16px;
}

.chart-title h3 {
  font-size: 18px;
  font-weight: bold;
  margin: 0 0 4px 0;
  color: var(--vp-c-text-1);
}

.chart-title p {
  font-size: 12px;
  margin: 0;
  color: var(--vp-c-text-2);
}

/* 词云图专用样式 */
.chart[data-chart-type="wordcloud"] {
  height: 450px;
  min-height: 400px;
  background: transparent;
  overflow: visible;
}

/* 确保词云图在暗黑模式下正确显示 */
.dark .chart[data-chart-type="wordcloud"] {
  background: transparent;
}

.loading,
.error {
  text-align: center;
  padding: 60px;
  font-size: 18px;
  border-radius: 12px;
  margin: 20px 0;
}

.error {
  color: #e74c3c;
  background: #fdf2f2;
  border: 1px solid #fecaca;
}

.loading {
  color: #3498db;
  background: #f0f9ff;
  border: 1px solid #bae6fd;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stats-overview {
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
  }

  .stat-card {
    padding: 20px;
  }

  .stat-number {
    font-size: 2rem;
  }

  .chart {
    height: 350px;
  }

  .chart-large {
    height: 500px;
  }

  .chart-container {
    padding: 16px;
  }
}

@media (max-width: 480px) {
  .stats-overview {
    grid-template-columns: 1fr;
  }

  .stat-number {
    font-size: 1.8rem;
  }

  .chart {
    height: 300px;
  }

  .chart-large {
    height: 400px;
  }
}
</style>
