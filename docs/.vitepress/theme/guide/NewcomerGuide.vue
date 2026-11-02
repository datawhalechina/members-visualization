<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { loadMembers } from '../utils/dataLoader.js'

const loading = ref(true)
const error = ref(null)
const members = ref([])
const activeStep = ref(0)
const isDark = ref(false)
const pieRef = ref(null)
let pieChart = null
let themeObserver = null

const memberCount = computed(() => members.value.length)

const domainDistribution = computed(() => {
  const counts = {}
  members.value.forEach(m => {
    const domains = Array.isArray(m.domain) ? m.domain : []
    domains.forEach(d => { if (d) counts[d] = (counts[d] || 0) + 1 })
  })
  return Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, 10)
})

const popularRepos = computed(() => {
  const repoMap = new Map()
  members.value.forEach(m => {
    const repos = Array.isArray(m.repositories) ? m.repositories : []
    repos.forEach(repo => {
      if (!repoMap.has(repo)) repoMap.set(repo, { name: repo, contributors: 0 })
      repoMap.get(repo).contributors++
    })
  })
  return Array.from(repoMap.values()).sort((a, b) => b.contributors - a.contributors).slice(0, 8)
})

const topContributors = computed(() => {
  return [...members.value]
    .sort((a, b) => (Number(b.org_total_contributions) || 0) - (Number(a.org_total_contributions) || 0))
    .slice(0, 5)
})

const steps = [
  { icon: '🔍', title: '了解组织', desc: 'Datawhale 是一个专注于 AI 领域的开源学习社区，汇聚了众多热爱开源的贡献者。' },
  { icon: '🧭', title: '选择方向', desc: '探索社区成员的研究方向分布，找到你感兴趣的领域。' },
  { icon: '📂', title: '找到项目', desc: '浏览热门项目，选择一个开始你的贡献之旅。' },
  { icon: '🚀', title: '开始贡献', desc: 'Fork 仓库、阅读文档、提交 PR，成为社区的一份子。' },
  { icon: '🌱', title: '持续成长', desc: '向优秀贡献者学习，持续提升你的开源影响力。' },
]

function toggleStep(index) {
  activeStep.value = activeStep.value === index ? -1 : index
}

function getAvatarUrl(member) {
  if (member.avatar && member.avatar.startsWith('avatars/')) {
    const basePath = import.meta.env.BASE_URL || '/'
    return `${basePath}${member.avatar}`.replace(/\/+/g, '/')
  }
  return member.avatar || `https://github.com/${member.id}.png`
}

function initPieChart() {
  if (!pieRef.value || domainDistribution.value.length === 0) return
  if (pieChart) pieChart.dispose()
  pieChart = echarts.init(pieRef.value, isDark.value ? 'dark' : 'light')
  pieChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', formatter: '{b}: {c} 人 ({d}%)' },
    series: [{
      type: 'pie',
      radius: ['35%', '65%'],
      center: ['50%', '50%'],
      itemStyle: { borderRadius: 6, borderColor: isDark.value ? '#1a1a1a' : '#fff', borderWidth: 2 },
      label: { show: true, fontSize: 11, color: isDark.value ? '#eee' : '#333' },
      data: domainDistribution.value.map(([name, value]) => ({ name, value })),
    }]
  })
}

function checkDarkMode() {
  isDark.value = document.documentElement.classList.contains('dark')
}

onMounted(async () => {
  try {
    checkDarkMode()
    if (typeof window !== 'undefined') {
      themeObserver = new MutationObserver(() => {
        const newDark = document.documentElement.classList.contains('dark')
        if (newDark !== isDark.value) {
          isDark.value = newDark
          setTimeout(initPieChart, 100)
        }
      })
      themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] })
      window.addEventListener('resize', () => pieChart?.resize())
    }
    members.value = await loadMembers()
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
})

// 模板 ref 回调：DOM 元素挂载时直接初始化饼图
function onPieMount(el) {
  pieRef.value = el
  if (el && !loading.value) {
    nextTick(() => setTimeout(initPieChart, 50))
  }
}

onUnmounted(() => {
  pieChart?.dispose()
  themeObserver?.disconnect()
})
</script>

<template>
  <div class="newcomer-guide">
    <div v-if="loading" class="status-box loading"><p>正在加载数据...</p></div>
    <div v-else-if="error" class="status-box error"><p>加载失败: {{ error }}</p></div>
    <div v-else>
      <!-- 欢迎区 -->
      <div class="welcome-card">
        <div class="welcome-icon">👋</div>
        <div class="welcome-text">
          <h3>欢迎加入 Datawhale 开源社区</h3>
          <p>目前已有 <strong>{{ memberCount }}</strong> 位贡献者，点击下方步骤了解如何开始你的开源之旅</p>
        </div>
      </div>

      <!-- 时间线 -->
      <div class="timeline">
        <div
          v-for="(step, i) in steps" :key="i"
          class="timeline-step"
          :class="{ active: activeStep === i, last: i === steps.length - 1 }"
        >
          <!-- 竖线 + 圆点 -->
          <div class="timeline-track">
            <div class="step-circle" :class="{ active: activeStep === i }" @click="toggleStep(i)">
              {{ step.icon }}
            </div>
            <div v-if="i < steps.length - 1" class="step-line"></div>
          </div>

          <!-- 内容 -->
          <div class="step-content" @click="toggleStep(i)">
            <div class="step-header">
              <span class="step-number">步骤 {{ i + 1 }}</span>
              <h4 class="step-title">{{ step.title }}</h4>
              <span class="step-arrow">{{ activeStep === i ? '▾' : '▸' }}</span>
            </div>
            <p class="step-desc">{{ step.desc }}</p>

            <!-- 展开内容 -->
            <div v-if="activeStep === i" class="step-detail" @click.stop>
              <!-- 步骤1: 了解组织 -->
              <template v-if="i === 0">
                <div class="detail-stats">
                  <div class="mini-stat"><span class="mini-num">{{ memberCount }}</span><span class="mini-label">贡献者</span></div>
                  <div class="mini-stat"><span class="mini-num">{{ domainDistribution.length }}+</span><span class="mini-label">研究方向</span></div>
                  <div class="mini-stat"><span class="mini-num">{{ popularRepos.length }}+</span><span class="mini-label">活跃项目</span></div>
                </div>
                <div class="detail-links">
                  <a href="https://www.datawhale.cn/" target="_blank" class="link-btn">🌐 Datawhale 官网</a>
                  <a href="https://github.com/datawhalechina" target="_blank" class="link-btn">🐙 GitHub 组织</a>
                </div>
              </template>

              <!-- 步骤2: 选择方向 -->
              <template v-if="i === 1">
                <div :ref="onPieMount" class="mini-chart"></div>
              </template>

              <!-- 步骤3: 找到项目 -->
              <template v-if="i === 2">
                <div class="repo-list">
                  <a
                    v-for="repo in popularRepos" :key="repo.name"
                    :href="`https://github.com/datawhalechina/${repo.name}`"
                    target="_blank" class="repo-item"
                  >
                    <span class="repo-name">📁 {{ repo.name }}</span>
                    <span class="repo-contributors">{{ repo.contributors }} 位贡献者</span>
                  </a>
                </div>
              </template>

              <!-- 步骤4: 开始贡献 -->
              <template v-if="i === 3">
                <div class="contrib-steps">
                  <div class="contrib-step"><span class="contrib-num">1</span> Fork 感兴趣的仓库到你的账号</div>
                  <div class="contrib-step"><span class="contrib-num">2</span> 阅读 README 和贡献指南</div>
                  <div class="contrib-step"><span class="contrib-num">3</span> 在本地修改代码并测试</div>
                  <div class="contrib-step"><span class="contrib-num">4</span> 提交 Pull Request 并等待 Review</div>
                </div>
                <a href="https://github.com/datawhalechina" target="_blank" class="link-btn" style="margin-top: 12px;">🚀 前往 GitHub 开始贡献</a>
              </template>

              <!-- 步骤5: 持续成长 -->
              <template v-if="i === 4">
                <p class="detail-hint">向社区顶级贡献者学习：</p>
                <div class="top-contributors">
                  <div v-for="c in topContributors" :key="c.id" class="contributor-row">
                    <img :src="getAvatarUrl(c)" :alt="c.name || c.id" class="contributor-avatar" loading="lazy" />
                    <div class="contributor-info">
                      <a :href="c.github || `https://github.com/${c.id}`" target="_blank" class="contributor-name">{{ c.name || c.id }}</a>
                      <span class="contributor-stat">{{ c.org_total_contributions }} 次贡献 · {{ c.org_repos_count }} 个仓库</span>
                    </div>
                  </div>
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.newcomer-guide { width: 100%; padding: 0; }

.status-box {
  text-align: center; padding: 60px 20px; border-radius: 12px;
  margin: 20px 0; background: var(--vp-c-bg-soft); border: 1px solid var(--vp-c-border);
}
.status-box.loading { border-color: var(--vp-c-brand-1); color: var(--vp-c-brand-1); }
.status-box.error { border-color: var(--vp-c-danger-1); color: var(--vp-c-danger-1); }

.welcome-card {
  display: flex; align-items: center; gap: 20px; padding: 28px 24px;
  background: var(--vp-c-bg-soft); border: 1px solid var(--vp-c-border);
  border-radius: 12px; margin-bottom: 32px;
}
.welcome-icon { font-size: 48px; flex-shrink: 0; }
.welcome-text h3 { margin: 0 0 6px; font-size: 18px; color: var(--vp-c-text-1); }
.welcome-text p { margin: 0; font-size: 14px; color: var(--vp-c-text-2); }
.welcome-text strong { color: var(--vp-c-brand-1); }

/* 时间线 */
.timeline { padding-left: 8px; }
.timeline-step { display: flex; gap: 20px; }
.timeline-track { display: flex; flex-direction: column; align-items: center; flex-shrink: 0; width: 40px; }
.step-circle {
  width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-size: 20px; background: var(--vp-c-bg-soft); border: 2px solid var(--vp-c-border);
  cursor: pointer; transition: all 0.2s; flex-shrink: 0; z-index: 1;
}
.step-circle.active { border-color: var(--vp-c-brand-1); background: var(--vp-c-brand-soft); }
.step-line { width: 2px; flex: 1; background: var(--vp-c-border); min-height: 20px; }

.step-content {
  flex: 1; padding-bottom: 28px; cursor: pointer; min-width: 0;
}
.step-header { display: flex; align-items: center; gap: 8px; }
.step-number { font-size: 11px; color: var(--vp-c-text-3); text-transform: uppercase; }
.step-title { margin: 0; font-size: 16px; color: var(--vp-c-text-1); flex: 1; }
.step-arrow { color: var(--vp-c-text-3); font-size: 12px; }
.step-desc { margin: 4px 0 0; font-size: 13px; color: var(--vp-c-text-2); }

/* 展开详情 */
.step-detail {
  margin-top: 16px; padding: 16px; background: var(--vp-c-bg); border: 1px solid var(--vp-c-border);
  border-radius: 10px; cursor: default;
}

.detail-stats { display: flex; gap: 16px; margin-bottom: 12px; }
.mini-stat {
  flex: 1; text-align: center; padding: 12px 8px; background: var(--vp-c-bg-soft);
  border-radius: 8px;
}
.mini-num { display: block; font-size: 22px; font-weight: 700; color: var(--vp-c-brand-1); }
.mini-label { font-size: 12px; color: var(--vp-c-text-2); }

.detail-links { display: flex; gap: 10px; flex-wrap: wrap; }
.link-btn {
  display: inline-block; padding: 8px 16px; background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-border); border-radius: 8px; font-size: 13px;
  color: var(--vp-c-brand-1); text-decoration: none; transition: all 0.2s;
}
.link-btn:hover { border-color: var(--vp-c-brand-1); background: var(--vp-c-brand-soft); }

.mini-chart { width: 100%; height: 300px; }

.repo-list { display: flex; flex-direction: column; gap: 6px; }
.repo-item {
  display: flex; justify-content: space-between; align-items: center; padding: 10px 12px;
  background: var(--vp-c-bg-soft); border-radius: 8px; text-decoration: none; transition: background 0.15s;
}
.repo-item:hover { background: var(--vp-c-brand-soft); }
.repo-name { font-size: 13px; color: var(--vp-c-text-1); }
.repo-contributors { font-size: 12px; color: var(--vp-c-text-2); white-space: nowrap; }

.contrib-steps { display: flex; flex-direction: column; gap: 8px; }
.contrib-step {
  display: flex; align-items: center; gap: 10px; font-size: 13px; color: var(--vp-c-text-1);
}
.contrib-num {
  width: 24px; height: 24px; border-radius: 50%; background: var(--vp-c-brand-1); color: #fff;
  display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; flex-shrink: 0;
}

.detail-hint { font-size: 13px; color: var(--vp-c-text-2); margin: 0 0 10px; }
.top-contributors { display: flex; flex-direction: column; gap: 8px; }
.contributor-row { display: flex; align-items: center; gap: 10px; padding: 8px 0; }
.contributor-avatar { width: 36px; height: 36px; border-radius: 50%; object-fit: cover; }
.contributor-info { display: flex; flex-direction: column; }
.contributor-name { font-size: 13px; color: var(--vp-c-brand-1); text-decoration: none; }
.contributor-name:hover { text-decoration: underline; }
.contributor-stat { font-size: 12px; color: var(--vp-c-text-2); }

@media (max-width: 768px) {
  .welcome-card { flex-direction: column; text-align: center; }
  .timeline { padding-left: 0; }
  .timeline-step { gap: 12px; }
  .detail-stats { flex-direction: column; gap: 8px; }
  .mini-chart { height: 250px; }
}
</style>
