<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  repoName: {
    type: String,
    default: ''
  },
  isEmbed: {
    type: Boolean,
    default: false
  }
})

const loading = ref(false)
const error = ref('')
const repoData = ref(null)
const contributors = ref([])
const recentContributorCount = ref(0)
const allContributorCount = ref(0)
const repoRank = ref(null)
const repoPopulation = ref(0)
const chartRef = ref(null)

let chartInstance = null
let loadToken = 0

const basePath = computed(() => import.meta.env.BASE_URL || '/')

const normalizePath = (path) => path.replace(/([^:]\/)\/+/g, '$1')
const normalizeRepoName = (value = '') => value.trim().replace(/^datawhalechina\//i, '').toLowerCase()

const parseMonthKey = (key) => {
  const [yearText, monthText] = key.split('-')
  const year = Number(yearText)
  const month = Number(monthText)
  if (!Number.isFinite(year) || !Number.isFinite(month)) return 0
  return new Date(year, month - 1, 1).getTime()
}

const formatMonthLabel = (key) => {
  const [yearText, monthText] = key.split('-')
  const year = yearText?.slice(-2) || '--'
  const month = String(Number(monthText || 0)).padStart(2, '0')
  return `${year}/${month}`
}

const monthlyStarsEntries = computed(() => {
  const source = repoData.value?.monthly_stars || {}
  return Object.entries(source).sort((a, b) => parseMonthKey(a[0]) - parseMonthKey(b[0]))
})

const monthlyTotalEntries = computed(() => {
  const source = repoData.value?.monthly_total_stars || {}
  return Object.entries(source).sort((a, b) => parseMonthKey(a[0]) - parseMonthKey(b[0]))
})

const monthlyStars = computed(() => monthlyStarsEntries.value.map(([, stars]) => Number(stars) || 0))
const monthlyTotals = computed(() => monthlyTotalEntries.value.map(([, stars]) => Number(stars) || 0))

const lastMonthStars = computed(() => monthlyStars.value.at(-1) || 0)
const starsLast3Months = computed(() => monthlyStars.value.slice(-3).reduce((sum, value) => sum + value, 0))
const previous3Months = computed(() => monthlyStars.value.slice(-6, -3).reduce((sum, value) => sum + value, 0))

const momentum = computed(() => {
  const current = starsLast3Months.value
  const previous = previous3Months.value
  const delta = current - previous
  const ratio = previous > 0 ? (delta / previous) * 100 : 0
  return { delta, ratio }
})

const momentumText = computed(() => {
  const delta = momentum.value.delta
  const ratio = momentum.value.ratio
  if (delta === 0) return 'flat'
  const deltaText = `${delta > 0 ? '+' : ''}${delta}`
  if (!Number.isFinite(ratio) || ratio === 0) return deltaText
  return `${deltaText} (${ratio > 0 ? '+' : ''}${ratio.toFixed(0)}%)`
})

const peakMonth = computed(() => {
  const entries = monthlyStarsEntries.value
  if (entries.length === 0) return { month: '--', stars: 0 }
  const [month, stars] = entries.reduce((best, current) => (Number(current[1]) > Number(best[1]) ? current : best))
  return { month, stars: Number(stars) || 0 }
})

const chartMonths = computed(() => monthlyStarsEntries.value.map(([month]) => month))

const renderChart = () => {
  if (!chartRef.value || chartMonths.value.length === 0) return

  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }

  const monthLabels = chartMonths.value.map((month) => formatMonthLabel(month))
  const starBars = monthlyStars.value
  const totalLine = monthlyTotals.value.length ? monthlyTotals.value : starBars

  chartInstance = echarts.init(chartRef.value)
  chartInstance.setOption({
    animation: false,
    grid: {
      left: 6,
      right: 10,
      top: 28,
      bottom: 24,
      containLabel: false
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'line'
      }
    },
    xAxis: {
      type: 'category',
      data: monthLabels,
      axisTick: { show: false },
      axisLine: { lineStyle: { color: '#d0d7de' } },
      axisLabel: {
        color: '#57606a',
        fontSize: 10,
        interval: (index) => index % 2 !== 0
      }
    },
    yAxis: [
      {
        type: 'value',
        show: false
      },
      {
        type: 'value',
        show: false
      }
    ],
    series: [
      {
        name: 'Monthly Stars',
        type: 'bar',
        barWidth: 12,
        data: starBars,
        itemStyle: {
          color: '#2f81f7',
          borderRadius: [4, 4, 0, 0]
        }
      },
      {
        name: 'Total Stars',
        type: 'line',
        yAxisIndex: 1,
        smooth: true,
        symbol: 'none',
        lineStyle: {
          width: 2,
          color: '#20b486'
        },
        data: totalLine
      }
    ]
  })
}

const resizeChart = () => {
  if (chartInstance) chartInstance.resize()
}

const loadRepoData = async (repoSlug) => {
  const candidates = [
    normalizePath(`${basePath.value}data/datawhalechina/repo/${repoSlug}.json`),
    normalizePath(`${basePath.value}data/datawhalechina/repo/${repoSlug.toLowerCase()}.json`)
  ]

  let lastError = null
  const uniqueCandidates = [...new Set(candidates)]
  for (const candidate of uniqueCandidates) {
    try {
      const response = await fetch(candidate)
      if (!response.ok) {
        lastError = new Error(`repo data not found (${response.status})`)
        continue
      }
      return await response.json()
    } catch (fetchError) {
      lastError = fetchError
    }
  }

  throw lastError || new Error('repo data not found')
}

const loadCommitsData = async () => {
  const response = await fetch(normalizePath(`${basePath.value}data/commits_weekly.json`))
  if (!response.ok) throw new Error('failed to load weekly commits')
  return await response.json()
}

const loadMembersData = async () => {
  const response = await fetch(normalizePath(`${basePath.value}data/members.json`))
  if (!response.ok) throw new Error('failed to load members')
  return await response.json()
}

const loadRepoListData = async () => {
  const response = await fetch(normalizePath(`${basePath.value}data/datawhalechina/organization/repo_list.json`))
  if (!response.ok) return []
  return await response.json()
}

const memberRepoSet = (member) =>
  String(member?.repositories || '')
    .split(';')
    .map((name) => normalizeRepoName(name))
    .filter(Boolean)

const buildContributorData = (repoSlug, commitsData, membersData) => {
  const memberMap = new Map()
  for (const member of membersData) {
    if (!member?.id) continue
    memberMap.set(member.id, member)
    memberMap.set(member.id.toLowerCase(), member)
  }

  const repoMembers = membersData.filter((member) => memberRepoSet(member).includes(repoSlug))
  allContributorCount.value = repoMembers.length

  const recentCommitMap = new Map()
  const userCommits = commitsData?.user_commits || {}
  for (const [username, payload] of Object.entries(userCommits)) {
    const repoCommits = payload?.repo_commits || {}
    let commitCount = 0
    for (const [repoName, rawCount] of Object.entries(repoCommits)) {
      if (normalizeRepoName(repoName) === repoSlug) {
        commitCount += Number(rawCount) || 0
      }
    }
    if (commitCount > 0) recentCommitMap.set(username, commitCount)
  }

  recentContributorCount.value = recentCommitMap.size

  const recentRows = [...recentCommitMap.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([username, commitsRecent]) => {
      const member = memberMap.get(username) || memberMap.get(username.toLowerCase())
      return {
        username,
        name: member?.name || username,
        avatar: member?.avatar || '',
        commitsRecent,
        totalContributions: Number(member?.org_total_contributions) || 0
      }
    })

  const seen = new Set(recentRows.map((row) => row.username.toLowerCase()))
  const fallbackRows = repoMembers
    .filter((member) => !seen.has(String(member.id || '').toLowerCase()))
    .sort((a, b) => (Number(b.org_total_contributions) || 0) - (Number(a.org_total_contributions) || 0))
    .map((member) => ({
      username: member.id,
      name: member.name || member.id,
      avatar: member.avatar || '',
      commitsRecent: 0,
      totalContributions: Number(member.org_total_contributions) || 0
    }))

  return [...recentRows, ...fallbackRows].slice(0, 12)
}

const updateRepoRank = (repoSlug, repoListData) => {
  const normalized = repoListData
    .map((item) => {
      const fullName = String(item?.name || '')
      const shortName = fullName.split('/').at(-1) || fullName
      return {
        repo: normalizeRepoName(shortName),
        starCount: Number(item?.star_count) || 0
      }
    })
    .filter((item) => item.repo)
    .sort((a, b) => b.starCount - a.starCount)

  repoPopulation.value = normalized.length
  const index = normalized.findIndex((item) => item.repo === repoSlug)
  repoRank.value = index >= 0 ? index + 1 : null
}

const avatarSource = (avatarPath) => {
  if (!avatarPath) return normalizePath(`${basePath.value}default-avatar.svg`)
  if (/^https?:\/\//i.test(avatarPath)) return avatarPath
  return normalizePath(`${basePath.value}${String(avatarPath).replace(/^\/+/, '')}`)
}

const handleImageError = (event) => {
  event.target.src = normalizePath(`${basePath.value}default-avatar.svg`)
}

const loadAllData = async (rawRepoName) => {
  const repoSlug = normalizeRepoName(rawRepoName)
  if (!repoSlug) {
    repoData.value = null
    contributors.value = []
    error.value = ''
    return
  }

  const token = ++loadToken
  loading.value = true
  error.value = ''

  try {
    const [repo, commits, members, repoListData] = await Promise.all([
      loadRepoData(repoSlug),
      loadCommitsData(),
      loadMembersData(),
      loadRepoListData()
    ])

    if (token !== loadToken) return

    repoData.value = repo
    contributors.value = buildContributorData(repoSlug, commits, members)
    updateRepoRank(normalizeRepoName(repo.repo_name || repoSlug), repoListData)

    loading.value = false
    await nextTick()
    renderChart()
  } catch (loadError) {
    if (token !== loadToken) return
    repoData.value = null
    contributors.value = []
    repoRank.value = null
    repoPopulation.value = 0
    error.value = loadError?.message || 'failed to load repository data'
  } finally {
    if (token === loadToken) loading.value = false
  }
}

watch(
  () => props.repoName,
  (repoName) => {
    loadAllData(repoName)
  },
  { immediate: true }
)

if (typeof window !== 'undefined') {
  window.addEventListener('resize', resizeChart)
}

onBeforeUnmount(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('resize', resizeChart)
  }
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})
</script>

<template>
  <div class="repo-badge" :class="{ embed: isEmbed }">
    <div v-if="loading" class="state loading">Loading repository pulse...</div>
    <div v-else-if="error" class="state error">{{ error }}</div>

    <article v-else-if="repoData" class="badge-card">
      <header class="badge-header">
        <div>
          <p class="eyebrow">Repository Pulse</p>
          <h2 class="repo-name">{{ repoData.repo_name }}</h2>
        </div>

        <div class="headline-pills">
          <div class="pill">
            <span class="pill-label">Stars</span>
            <span class="pill-value">{{ Number(repoData.star_count || 0).toLocaleString() }}</span>
          </div>
          <div v-if="repoRank" class="pill">
            <span class="pill-label">Org Rank</span>
            <span class="pill-value">#{{ repoRank }} / {{ repoPopulation }}</span>
          </div>
          <div class="pill">
            <span class="pill-label">Contributors</span>
            <span class="pill-value">{{ recentContributorCount }} active / {{ allContributorCount }} all</span>
          </div>
        </div>
      </header>

      <div class="badge-main">
        <section class="chart-panel">
          <div ref="chartRef" class="star-chart" />
          <div class="metric-grid">
            <div class="metric-item">
              <div class="metric-label">30D Stars</div>
              <div class="metric-value">+{{ lastMonthStars }}</div>
            </div>
            <div class="metric-item">
              <div class="metric-label">90D Stars</div>
              <div class="metric-value">+{{ starsLast3Months }}</div>
            </div>
            <div class="metric-item">
              <div class="metric-label">Peak Month</div>
              <div class="metric-value">{{ formatMonthLabel(peakMonth.month) }} (+{{ peakMonth.stars }})</div>
            </div>
            <div class="metric-item">
              <div class="metric-label">Momentum (3M)</div>
              <div class="metric-value">{{ momentumText }}</div>
            </div>
          </div>
        </section>

        <aside class="contributors-panel">
          <div class="avatar-stack">
            <img
              v-for="person in contributors.slice(0, 12)"
              :key="`avatar-${person.username}`"
              :src="avatarSource(person.avatar)"
              :alt="person.name"
              :title="`${person.name} | recent: ${person.commitsRecent}`"
              class="avatar"
              @error="handleImageError"
            >
          </div>

          <div class="contributor-list">
            <div
              v-for="person in contributors.slice(0, 5)"
              :key="person.username"
              class="contributor-row"
            >
              <div class="contributor-left">
                <img
                  :src="avatarSource(person.avatar)"
                  :alt="person.name"
                  class="avatar small"
                  @error="handleImageError"
                >
                <span class="contributor-name">{{ person.name || person.username }}</span>
              </div>
              <div class="contributor-metrics">
                <span v-if="person.commitsRecent > 0" class="recent">{{ person.commitsRecent }} / 7d</span>
                <span class="total">{{ person.totalContributions }} total</span>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </article>
  </div>
</template>

<style scoped>
.repo-badge {
  width: min(980px, 100%);
  min-height: 340px;
}

.repo-badge.embed {
  width: 100%;
  min-height: 100%;
}

.state {
  min-height: 320px;
  border: 1px solid #d0d7de;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  background: #ffffff;
}

.state.loading {
  color: #57606a;
}

.state.error {
  color: #cf222e;
  background: #fff8f8;
}

.badge-card {
  border: 1px solid #d0d7de;
  border-radius: 16px;
  background:
    radial-gradient(circle at right top, rgba(47, 129, 247, 0.12), transparent 42%),
    radial-gradient(circle at left bottom, rgba(32, 180, 134, 0.12), transparent 40%),
    #ffffff;
  box-shadow: 0 12px 32px rgba(31, 35, 40, 0.08);
  padding: 18px 20px;
}

.badge-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 14px;
}

.eyebrow {
  margin: 0;
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #57606a;
}

.repo-name {
  margin: 4px 0 0;
  font-size: 24px;
  line-height: 1.15;
  color: #0b3557;
  max-width: 460px;
  overflow-wrap: anywhere;
}

.headline-pills {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.pill {
  min-width: 128px;
  border: 1px solid #d0d7de;
  border-radius: 12px;
  padding: 8px 10px;
  background: rgba(255, 255, 255, 0.9);
}

.pill-label {
  display: block;
  color: #57606a;
  font-size: 11px;
  margin-bottom: 2px;
}

.pill-value {
  color: #1f2328;
  font-weight: 700;
  font-size: 14px;
}

.badge-main {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(280px, 1fr);
  gap: 14px;
}

.chart-panel {
  border: 1px solid #d0d7de;
  border-radius: 14px;
  padding: 10px;
  background: #ffffff;
}

.star-chart {
  width: 100%;
  height: 164px;
}

.metric-grid {
  margin-top: 8px;
  border-top: 1px solid #d8dee4;
  padding-top: 8px;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.metric-item {
  border: 1px solid #d8dee4;
  border-radius: 8px;
  background: #f6f8fa;
  padding: 8px;
}

.metric-label {
  font-size: 11px;
  color: #57606a;
}

.metric-value {
  margin-top: 2px;
  font-size: 13px;
  color: #1f2328;
  font-weight: 700;
  line-height: 1.2;
}

.contributors-panel {
  border: 1px solid #d0d7de;
  border-radius: 14px;
  background: #ffffff;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.avatar-stack {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
}

.avatar {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: 1px solid #d0d7de;
  object-fit: cover;
  background: #f6f8fa;
}

.avatar.small {
  width: 20px;
  height: 20px;
}

.contributor-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.contributor-row {
  border: 1px solid #d8dee4;
  border-radius: 8px;
  padding: 6px 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  background: #f6f8fa;
}

.contributor-left {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
}

.contributor-name {
  font-size: 12px;
  color: #1f2328;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.contributor-metrics {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.recent,
.total {
  font-size: 11px;
  border-radius: 999px;
  padding: 2px 6px;
  border: 1px solid #d0d7de;
  background: #ffffff;
  color: #44515f;
}

.recent {
  border-color: #9ecbff;
  color: #0a58ca;
  background: #eff6ff;
}

@media (max-width: 980px) {
  .repo-badge {
    width: 100%;
  }

  .badge-header {
    flex-direction: column;
  }

  .headline-pills {
    justify-content: flex-start;
  }

  .badge-main {
    grid-template-columns: 1fr;
  }
}
</style>
