<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { useData } from 'vitepress'
import * as echarts from 'echarts'
import { loadProjectStats, sortedMonths, formatStars } from './projectData'

const props = defineProps({
  dataKey: { type: String, required: true },
  ranking: { type: Boolean, default: false },
  initialVisible: { type: Number, default: 8 }
})
const { isDark } = useData()
const chartRef = ref(null)
const items = ref([])
const meta = ref({})
const loading = ref(true)
const error = ref('')
const showAll = ref(false)
const isEmpty = computed(() => !items.value.some(item =>
  props.ranking ? Number.isFinite(item.starAdd) :
    Object.values(item.monthly_total_stars || {}).some(Number.isFinite)))
let chart
let observer
let disposed = false

function renderChart() {
  if (!chartRef.value || loading.value || error.value || isEmpty.value) return
  const mobile = chartRef.value.clientWidth < 520
  const color = isDark.value ? '#a6b1c2' : '#66758a'
  const border = isDark.value ? '#303a48' : '#e5eaf0'
  const palette = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4', '#f97316', '#64748b']
  const months = sortedMonths(items.value)
  const common = {
    backgroundColor: 'transparent', color: palette,
    textStyle: { fontFamily: 'sans-serif', color }, animationDuration: 350,
    tooltip: {
      trigger: 'axis', confine: true,
      backgroundColor: isDark.value ? '#202938' : '#fff', borderColor: border,
      textStyle: { color: isDark.value ? '#e2e8f0' : '#273449', fontSize: 12 },
      valueFormatter: value => value == null ? '未采集' : `${Number(value).toLocaleString('zh-CN')} Stars`
    },
    aria: { enabled: true }
  }
  let option
  if (props.ranking) {
    const rows = items.value.filter(item => Number.isFinite(item.starAdd))
    option = {
      ...common,
      grid: { left: 12, right: mobile ? 60 : 76, top: 16, bottom: 20, containLabel: true },
      xAxis: {
        type: 'value', minInterval: 1, splitNumber: mobile ? 3 : 5,
        axisLabel: { color, fontSize: 11, formatter: formatStars, hideOverlap: true },
        axisLine: { show: false }, axisTick: { show: false },
        splitLine: { lineStyle: { color: border, type: 'dashed' } }
      },
      yAxis: {
        type: 'category', inverse: true, data: rows.map(item => item.name),
        axisLine: { show: false }, axisTick: { show: false },
        axisLabel: { color, fontSize: 12, width: mobile ? 105 : 220, overflow: 'truncate' }
      },
      series: [{
        name: '净增 Star', type: 'bar', barMaxWidth: 23,
        data: rows.map((item, index) => ({ value: item.starAdd, itemStyle: { color: palette[index % palette.length] } })),
        itemStyle: { borderRadius: [0, 5, 5, 0] },
        label: { show: true, position: 'right', color, fontSize: 12,
          formatter: ({ value }) => `${value > 0 ? '+' : ''}${formatStars(value)}` }
      }]
    }
  } else {
    const currentSelection = chart?.getOption().legend?.[0]?.selected || {}
    const selected = Object.fromEntries(items.value.map((item, index) =>
      [item.name, currentSelection[item.name] ?? (showAll.value || index < props.initialVisible)]))
    option = {
      ...common,
      tooltip: { ...common.tooltip, trigger: 'item' },
      legend: {
        type: 'scroll', top: 2, left: 0, right: 0, itemWidth: 14, itemHeight: 8,
        textStyle: { color, fontSize: 12 }, pageTextStyle: { color },
        pageIconColor: color, pageIconInactiveColor: border,
        selected, data: items.value.map(item => item.name)
      },
      grid: { left: 8, right: 18, top: 68, bottom: 60, containLabel: true },
      xAxis: {
        type: 'category', boundaryGap: false, data: months,
        axisLine: { lineStyle: { color: border } }, axisTick: { show: false },
        axisLabel: { color, fontSize: 11, margin: 14, hideOverlap: true,
          formatter: value => { const [year, month] = value.split('-'); return `${year.slice(2)}/${month.padStart(2, '0')}` } }
      },
      yAxis: {
        type: 'value', name: 'Stars', nameTextStyle: { color, padding: [0, 0, 8, 0] },
        splitNumber: 4, minInterval: 1,
        axisLine: { show: false }, axisTick: { show: false },
        axisLabel: { color, fontSize: 11, formatter: formatStars, hideOverlap: true },
        splitLine: { lineStyle: { color: border, type: 'dashed' } }
      },
      dataZoom: [{
        type: 'slider', xAxisIndex: 0, bottom: 4, height: 20,
        borderColor: 'transparent', backgroundColor: isDark.value ? '#202938' : '#f1f5f9',
        fillerColor: 'rgba(59,130,246,.12)', showDetail: false,
        handleStyle: { color: '#3b82f6', borderColor: '#3b82f6' },
        dataBackground: { lineStyle: { color: border }, areaStyle: { color: border } }
      }],
      series: items.value.map(item => ({
        name: item.name, type: 'line', smooth: false, showSymbol: false,
        connectNulls: false, lineStyle: { width: 2 },
        emphasis: { focus: 'series', lineStyle: { width: 3 } },
        data: months.map(month => item.monthly_total_stars?.[month] ?? null)
      }))
    }
  }
  if (!chart) chart = echarts.init(chartRef.value)
  chart.setOption(option, true)
  chart.resize()
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const result = await loadProjectStats()
    if (disposed) return
    items.value = Array.isArray(result[props.dataKey]) ? result[props.dataKey] : []
    meta.value = result.meta || {}
  } catch (cause) {
    if (!disposed) error.value = cause.message || '暂时无法获取项目统计'
  } finally {
    if (!disposed) {
      loading.value = false
      await nextTick()
      renderChart()
    }
  }
}

function toggleSeries() {
  showAll.value = !showAll.value
  chart?.setOption({ legend: { selected: Object.fromEntries(items.value.map((item, index) =>
    [item.name, showAll.value || index < props.initialVisible])) } })
}

watch(isDark, renderChart)
onMounted(() => {
  observer = new ResizeObserver(renderChart)
  observer.observe(chartRef.value)
  load()
})
onBeforeUnmount(() => {
  disposed = true
  observer?.disconnect()
  chart?.dispose()
})
</script>

<template>
  <section class="project-chart" :class="{ ranking }" :aria-busy="loading">
    <div v-if="loading" class="chart-state" role="status">正在加载项目统计…</div>
    <div v-else-if="error" class="chart-state chart-error" role="alert">
      <p>{{ error }}</p><button type="button" @click="load">重新加载</button>
    </div>
    <div v-else-if="isEmpty" class="chart-state">本期暂无可用的项目统计，稍后更新后再来看看。</div>
    <div v-else class="chart-toolbar">
      <span>{{ items.length }} 个项目<span v-if="meta.period_end"> · 截至 {{ meta.period_end }}</span></span>
      <button v-if="!ranking && items.length > initialVisible" type="button" @click="toggleSeries">
        {{ showAll ? `仅看前 ${initialVisible} 项` : '显示全部项目' }}
      </button>
    </div>
    <div ref="chartRef" class="chart-canvas" :class="{ 'chart-hidden': loading || error || isEmpty }"
      role="img" :aria-label="ranking ? '项目净增 Star 排行图' : '项目月度 Star 快照趋势图'"></div>
    <p v-if="!loading && !error && !isEmpty" class="chart-hint">
      {{ ranking ? '采集快照之间的净增 Star，包含取消 Star 的影响。' : '点击图例切换项目，拖动底部滑块查看月份；缺失快照以断线显示。' }}
    </p>
  </section>
</template>

<style scoped>
.project-chart { margin: 20px 0 32px; padding: 18px 18px 12px; border: 1px solid var(--vp-c-divider); border-radius: 12px; background: var(--vp-c-bg); }
.chart-toolbar { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 18px; color: var(--vp-c-text-2); font-size: 12px; }
.chart-toolbar button, .chart-state button { border: 1px solid var(--vp-c-divider); padding: 5px 10px; border-radius: 6px; color: var(--vp-c-brand-1); font: inherit; cursor: pointer; }
.chart-toolbar button:hover, .chart-state button:hover { background: var(--vp-c-bg-soft); }
.chart-toolbar button:focus-visible, .chart-state button:focus-visible { outline: 2px solid var(--vp-c-brand-1); outline-offset: 3px; }
.chart-canvas { height: 440px; width: 100%; min-width: 0; }
.ranking .chart-canvas { height: 300px; }
.chart-hidden { display: none; }
.chart-state { padding: 60px 12px; text-align: center; color: var(--vp-c-text-2); font-size: 14px; }
.chart-error { color: var(--vp-c-danger-1); }
.chart-hint { margin: 10px 0 0; color: var(--vp-c-text-3); font-size: 12px; line-height: 1.6; }
@media (max-width: 640px) { .project-chart { padding: 14px 10px 10px; } .chart-canvas { height: 360px; } .ranking .chart-canvas { height: 300px; } .chart-toolbar { align-items: flex-start; font-size: 11px; } }
</style>
