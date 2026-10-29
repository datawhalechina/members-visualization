<script setup>
import { ref, computed, onMounted } from 'vue'
import { domToPng } from 'modern-screenshot'
import { loadMembers, loadCommitsWeekly } from '../utils/dataLoader.js'
import { computeMemberBadges, TIER_COLORS } from '../utils/badges.js'

const loading = ref(true)
const error = ref(null)
const members = ref([])
const commitsData = ref(null)
const searchQuery = ref('')
const searchSubmitted = ref(false)
const selectedMember = ref(null)
const cardRef = ref(null)
const copyStatus = ref('')
const linkStatus = ref('')
const examples = computed(() => [...members.value]
  .sort((a, b) => (Number(b.org_total_contributions) || 0) - (Number(a.org_total_contributions) || 0))
  .slice(0, 3))

function normalizeUsername(value) {
  return value.trim().replace(/^(?:https?:\/\/)?(?:www\.)?github\.com\//i, '').replace(/^@/, '').split(/[/?#]/)[0].toLowerCase()
}

function mergeCommitsData(membersArr, commits) {
  if (!commits?.user_commits) return membersArr
  return membersArr.map(m => ({
    ...m,
    night_owl_percentage: commits.user_commits[m.id]?.night_owl_percentage || 0,
    weekly_commits: commits.user_commits[m.id]?.total_commits || 0,
  }))
}

function findMember() {
  searchSubmitted.value = true
  const q = normalizeUsername(searchQuery.value)
  if (!q) { selectedMember.value = null; return }
  selectedMember.value = members.value.find(m =>
    m.id.toLowerCase() === q || (m.name && m.name.toLowerCase() === q)
  ) || null
  const url = new URL(window.location.href)
  if (selectedMember.value) url.searchParams.set('user', selectedMember.value.id)
  else url.searchParams.delete('user')
  window.history.replaceState(window.history.state, '', url)
}

function useExample(member) {
  searchQuery.value = member.id
  findMember()
}

async function copyReportLink() {
  try {
    await navigator.clipboard.writeText(window.location.href)
    linkStatus.value = '链接已复制'
  } catch {
    linkStatus.value = '可复制浏览器地址分享'
  }
  setTimeout(() => { linkStatus.value = '' }, 2500)
}

function topPercentage(ranking) {
  const value = ranking.rank / members.value.length * 100
  return Number(Math.max(0.1, value).toFixed(value < 1 ? 1 : 0))
}

function handleKeydown(e) {
  if (e.key === 'Enter') findMember()
}

// 百分位计算
function percentile(field) {
  if (!selectedMember.value) return { rank: 0, pct: 0 }
  const val = Number(selectedMember.value[field]) || 0
  const total = members.value.length
  const rank = members.value.filter(x => (Number(x[field]) || 0) > val).length + 1
  return { rank, pct: Math.round((1 - rank / total) * 100) }
}

const report = computed(() => {
  if (!selectedMember.value) return null
  const m = selectedMember.value
  const badges = computeMemberBadges(m)
  const stars = percentile('org_total_stars')
  const contribs = percentile('org_total_contributions')
  const followers = percentile('followers')
  const repos = percentile('org_repos_count')

  return {
    member: m,
    badges,
    rankings: { stars, contribs, followers, repos },
    summary: generateSummary(m, { stars, contribs, followers, repos }),
  }
})

function generateSummary(m, rankings) {
  const parts = []
  if (rankings.stars.pct >= 90) parts.push('你是社区中的 Star 收割机')
  else if (rankings.stars.pct >= 70) parts.push('你参与的项目很受欢迎')
  if (rankings.contribs.pct >= 90) parts.push('代码贡献量名列前茅')
  else if (rankings.contribs.pct >= 50) parts.push('持续为社区贡献代码')
  const domains = Array.isArray(m.domain) ? m.domain : []
  if (domains.length >= 5) parts.push(`涉猎 ${domains.length} 个研究方向，堪称全能选手`)
  else if (domains.length >= 3) parts.push(`在 ${domains.length} 个方向都有建树`)
  if (m.night_owl_percentage >= 50) parts.push('是一位资深夜猫子开发者 🦉')
  if (rankings.followers.pct >= 80) parts.push('在社区中颇具影响力')
  return parts.length > 0 ? parts.join('，') + '！' : '继续加油，你的开源之旅才刚刚开始！'
}

function getAvatarUrl(member) {
  if (member.avatar && member.avatar.startsWith('avatars/')) {
    const basePath = import.meta.env.BASE_URL || '/'
    return `${basePath}${member.avatar}`.replace(/\/+/g, '/')
  }
  return member.avatar || `https://github.com/${member.id}.png`
}

function pctColor(pct) {
  if (pct >= 90) return '#52c41a'
  if (pct >= 70) return '#1890ff'
  if (pct >= 50) return '#722ed1'
  return 'var(--vp-c-text-2)'
}

// 复制为高清 PNG
async function copyAsPng() {
  if (!cardRef.value) return
  copyStatus.value = '生成中...'
  try {
    const dataUrl = await domToPng(cardRef.value, {
      scale: 2,
      features: { removeControlCharacter: false },
    })
    const resp = await fetch(dataUrl)
    const blob = await resp.blob()
    try {
      await navigator.clipboard.write([new ClipboardItem({ 'image/png': blob })])
      copyStatus.value = '已复制'
    } catch {
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `datawhale-report-${selectedMember.value?.id || 'user'}.png`
      a.click()
      URL.revokeObjectURL(url)
      copyStatus.value = '已下载'
    }
    setTimeout(() => { copyStatus.value = '' }, 2000)
  } catch (e) {
    console.error('截图失败:', e)
    copyStatus.value = '生成失败'
    setTimeout(() => { copyStatus.value = '' }, 2000)
  }
}

onMounted(async () => {
  try {
    const [membersData, commits] = await Promise.all([loadMembers(), loadCommitsWeekly()])
    members.value = mergeCommitsData(membersData, commits)
    commitsData.value = commits
    const initialUser = new URLSearchParams(window.location.search).get('user')
    if (initialUser) {
      searchQuery.value = initialUser
      findMember()
    }
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="annual-report">
    <div v-if="loading" class="status-box loading"><p>正在加载数据...</p></div>
    <div v-else-if="error" class="status-box error"><p>加载失败: {{ error }}</p></div>
    <div v-else>
      <!-- 搜索区 -->
      <div class="search-section">
        <div class="search-box">
          <input
            v-model="searchQuery"
            type="text"
            aria-label="报告用户"
            placeholder="GitHub 用户名或个人主页链接"
            class="search-input"
            @keydown="handleKeydown"
          />
          <button class="search-btn" :disabled="!searchQuery.trim()" @click="findMember">生成报告</button>
          <button class="search-btn secondary" :disabled="!report || copyStatus === '生成中...'" @click="copyAsPng" title="复制为高清 PNG 图片">{{ copyStatus || '📷 复制图片' }}</button>
          <button v-if="report" class="search-btn secondary" @click="copyReportLink">{{ linkStatus || '复制报告链接' }}</button>
        </div>
        <p class="search-hint">基于社区已收录成员生成报告，可复制图片或通过链接分享。</p>
        <div v-if="!report && !searchSubmitted" class="report-examples">
          <span>先看看社区伙伴：</span>
          <button v-for="member in examples" :key="member.id" @click="useExample(member)">@{{ member.id }}</button>
        </div>
      </div>

      <!-- 未找到 -->
      <div v-if="searchSubmitted && !selectedMember && searchQuery.trim()" class="not-found">
        <div class="not-found-icon">🔍</div>
        <p>未找到用户 <strong>{{ searchQuery }}</strong></p>
        <p class="not-found-hint">该用户可能还不是 Datawhale 的贡献者。<a href="https://github.com/datawhalechina" target="_blank">加入我们</a>，开始你的开源之旅！</p>
      </div>

      <!-- 报告卡片 -->
      <div v-if="report" class="report-wrapper">
        <div ref="cardRef" class="report-card">
          <div class="report-inner">
            <!-- 头部 -->
            <div class="report-header">
              <div class="report-badge-label">Datawhale 个人开源报告</div>
              <img :src="getAvatarUrl(report.member)" :alt="report.member.name || report.member.id" class="report-avatar" />
              <h2 class="report-name">{{ report.member.name || report.member.id }}</h2>
              <p v-if="report.member.name && report.member.name !== report.member.id" class="report-id">@{{ report.member.id }}</p>
              <p v-if="report.member.bio" class="report-bio">{{ report.member.bio }}</p>
              <div class="report-meta">
                <span v-if="report.member.location">📍 {{ report.member.location }}</span>
                <span v-if="report.member.company">🏢 {{ report.member.company }}</span>
              </div>
            </div>

            <!-- 关键指标 -->
            <div class="metrics-grid">
              <div class="metric-card">
                <div class="metric-value">{{ report.member.org_repos_count || 0 }}</div>
                <div class="metric-label">参与仓库</div>
                <div class="metric-pct" :style="{ color: pctColor(report.rankings.repos.pct) }">社区前 {{ topPercentage(report.rankings.repos) }}%</div>
              </div>
              <div class="metric-card">
                <div class="metric-value">{{ report.member.org_total_stars || 0 }}</div>
                <div class="metric-label">参与项目 Stars</div>
                <div class="metric-pct" :style="{ color: pctColor(report.rankings.stars.pct) }">社区前 {{ topPercentage(report.rankings.stars) }}%</div>
              </div>
              <div class="metric-card">
                <div class="metric-value">{{ report.member.org_total_contributions || 0 }}</div>
                <div class="metric-label">贡献次数</div>
                <div class="metric-pct" :style="{ color: pctColor(report.rankings.contribs.pct) }">社区前 {{ topPercentage(report.rankings.contribs) }}%</div>
              </div>
              <div class="metric-card">
                <div class="metric-value">{{ report.member.followers || 0 }}</div>
                <div class="metric-label">关注者</div>
                <div class="metric-pct" :style="{ color: pctColor(report.rankings.followers.pct) }">社区前 {{ topPercentage(report.rankings.followers) }}%</div>
              </div>
            </div>

            <p class="report-scope">累计指标来自成员采集快照；参与项目 Stars 按所参与的组织仓库汇总。近期活跃与深夜比例使用最近 {{ commitsData?.days_range || 7 }} 天的采集窗口<span v-if="commitsData?.update_time">，更新于 {{ commitsData.update_time.slice(0, 10) }}</span>。</p>

            <!-- 研究方向 -->
            <div v-if="report.member.domain && report.member.domain.length" class="section">
              <h3 class="section-title">🎯 研究方向</h3>
              <div class="domain-tags">
                <span v-for="d in report.member.domain" :key="d" class="domain-tag">{{ d }}</span>
              </div>
            </div>

            <!-- 参与仓库 -->
            <div v-if="report.member.repositories && report.member.repositories.length" class="section">
              <h3 class="section-title">📦 参与仓库</h3>
              <div class="repo-tags">
                <a
                  v-for="r in report.member.repositories" :key="r"
                  :href="`https://github.com/datawhalechina/${r}`"
                  target="_blank" class="repo-tag"
                >{{ r }}</a>
              </div>
            </div>

            <!-- 徽章 -->
            <div class="section">
              <h3 class="section-title">🏅 获得徽章</h3>
              <div v-if="report.badges.length" class="badges-row">
                <div v-for="b in report.badges" :key="b.id" class="badge-item">
                  <span class="badge-icon">{{ b.icon }}</span>
                  <span class="badge-name">{{ b.name }}</span>
                  <span class="badge-tier" :style="{ color: TIER_COLORS[b.tier] }">{{ b.tierLabel }}</span>
                </div>
              </div>
              <p v-else class="no-badges">还没有获得徽章，继续努力！</p>
            </div>

            <!-- 趣味总结 -->
            <div class="summary-box">
              <p>{{ report.summary }}</p>
            </div>

            <!-- 底部 -->
            <div class="report-footer">
              <span>Datawhale Members Visualization</span>
              <span v-if="commitsData?.update_time">{{ commitsData.update_time.slice(0, 10) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.annual-report { width: 100%; padding: 20px 0; }

.status-box {
  text-align: center; padding: 60px 20px; border-radius: 12px;
  margin: 20px 0; background: var(--vp-c-bg-soft); border: 1px solid var(--vp-c-border);
}
.status-box.loading { border-color: var(--vp-c-brand-1); color: var(--vp-c-brand-1); }
.status-box.error { border-color: var(--vp-c-danger-1); color: var(--vp-c-danger-1); }

/* 搜索区 */
.search-section { text-align: center; margin-bottom: 32px; }
.search-box { display: flex; gap: 10px; max-width: 680px; margin: 0 auto; flex-wrap: wrap; justify-content: center; }
.search-input {
  flex: 1 1 200px; padding: 12px 16px; border: 2px solid var(--vp-c-border); border-radius: 10px;
  font-size: 15px; background: var(--vp-c-bg); color: var(--vp-c-text-1); outline: none;
  transition: border-color 0.2s;
}
.search-input:focus { border-color: var(--vp-c-brand-1); }
.search-btn {
  padding: 12px 20px; background: var(--vp-c-brand-1); color: #fff; border: none;
  border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer;
  transition: all 0.2s; white-space: nowrap;
}
.search-btn:hover { opacity: 0.9; }
.search-btn.secondary {
  background: var(--vp-c-bg-soft); color: var(--vp-c-text-1);
  border: 1px solid var(--vp-c-border); font-weight: 500;
}
.search-btn.secondary:hover:not(:disabled) { border-color: var(--vp-c-brand-1); color: var(--vp-c-brand-1); }
.search-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.search-hint { font-size: 13px; color: var(--vp-c-text-2); margin-top: 10px; }
.report-examples { display: flex; flex-wrap: wrap; justify-content: center; gap: 8px 12px; margin-top: 18px; color: var(--vp-c-text-3); font-size: 12px; }
.report-examples button { color: var(--vp-c-brand-1); text-decoration: underline; text-underline-offset: 3px; }
.report-scope { margin: 0 0 24px; color: var(--vp-c-text-2); font-size: 12px; line-height: 1.8; }

/* 未找到 */
.not-found { text-align: center; padding: 48px 20px; }
.not-found-icon { font-size: 48px; margin-bottom: 12px; }
.not-found p { margin: 4px 0; color: var(--vp-c-text-1); }
.not-found strong { color: var(--vp-c-brand-1); }
.not-found-hint { font-size: 13px; color: var(--vp-c-text-2); }
.not-found-hint a { color: var(--vp-c-brand-1); }

/* 报告卡片 */
.report-wrapper { display: flex; flex-direction: column; align-items: center; }

.report-card {
  max-width: 680px; width: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px; padding: 3px;
}
.report-inner {
  background: var(--vp-c-bg); border-radius: 18px; padding: 40px 32px;
}

/* 头部 */
.report-header { text-align: center; margin-bottom: 28px; }
.report-badge-label {
  display: inline-block; padding: 4px 14px; background: var(--vp-c-brand-soft);
  color: var(--vp-c-brand-1); border-radius: 20px; font-size: 12px; font-weight: 600;
  margin-bottom: 16px;
}
.report-avatar {
  width: 80px; height: 80px; border-radius: 50%; object-fit: cover;
  border: 3px solid var(--vp-c-brand-1); display: block; margin: 0 auto 12px;
}
.report-name { margin: 0; padding: 0; border: 0; font-size: 24px; color: var(--vp-c-text-1); }
.report-id { margin: 2px 0 0; font-size: 14px; color: var(--vp-c-text-2); }
.report-bio { margin: 8px 0 0; font-size: 13px; color: var(--vp-c-text-2); max-width: 400px; margin-left: auto; margin-right: auto; }
.report-meta { margin-top: 8px; font-size: 13px; color: var(--vp-c-text-2); display: flex; gap: 16px; justify-content: center; flex-wrap: wrap; }

/* 指标网格 */
.metrics-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 24px; }
.metric-card {
  text-align: center; padding: 16px 12px; background: var(--vp-c-bg-soft);
  border-radius: 10px; border: 1px solid var(--vp-c-border);
}
.metric-value { font-size: 26px; font-weight: 700; color: var(--vp-c-text-1); }
.metric-label { font-size: 12px; color: var(--vp-c-text-2); margin: 2px 0; }
.metric-pct { font-size: 12px; font-weight: 600; }

/* 段落 */
.section { margin-bottom: 20px; }
.section-title { font-size: 15px; color: var(--vp-c-text-1); margin: 0 0 10px; border: none; }

.domain-tags, .repo-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.domain-tag {
  padding: 4px 12px; background: var(--vp-c-brand-soft); color: var(--vp-c-brand-1);
  border-radius: 20px; font-size: 13px;
}
.repo-tag {
  padding: 4px 10px; background: var(--vp-c-bg-soft); border: 1px solid var(--vp-c-border);
  border-radius: 6px; font-size: 12px; color: var(--vp-c-text-1); text-decoration: none;
  transition: all 0.15s; white-space: nowrap;
}
.repo-tag:hover { border-color: var(--vp-c-brand-1); color: var(--vp-c-brand-1); }

/* 徽章 */
.badges-row { display: flex; flex-wrap: wrap; gap: 10px; }
.badge-item {
  display: flex; align-items: center; gap: 6px; padding: 6px 12px;
  background: var(--vp-c-bg-soft); border-radius: 8px; border: 1px solid var(--vp-c-border);
  white-space: nowrap;
}
.badge-icon { font-size: 18px; }
.badge-name { font-size: 13px; color: var(--vp-c-text-1); }
.badge-tier { font-size: 12px; font-weight: 600; }
.no-badges { font-size: 13px; color: var(--vp-c-text-3); margin: 0; }

/* 总结 */
.summary-box {
  margin: 24px 0 20px; padding: 16px 20px; border-left: 4px solid var(--vp-c-brand-1);
  background: var(--vp-c-bg-soft); border-radius: 0 8px 8px 0;
}
.summary-box p { margin: 0; font-size: 15px; color: var(--vp-c-text-1); line-height: 1.6; }

/* 底部 */
.report-footer {
  display: flex; justify-content: space-between; font-size: 12px; color: var(--vp-c-text-3);
  padding-top: 16px; border-top: 1px solid var(--vp-c-border);
}

@media print {
  .search-section { display: none; }
  .report-card { box-shadow: none; max-width: 100%; }
}

@media (max-width: 768px) {
  .report-inner { padding: 28px 20px; }
  .metrics-grid { grid-template-columns: repeat(2, 1fr); gap: 8px; }
  .search-box { flex-direction: column; }
  .search-btn { width: 100%; }
  .search-input { flex: 1 1 100%; }
}
</style>
