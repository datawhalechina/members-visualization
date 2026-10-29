<script setup>
import { computed } from 'vue'
import { useData, withBase } from 'vitepress'

const { frontmatter } = useData()
const summary = computed(() => frontmatter.value.communityOverview || {})
const metrics = computed(() => [
  { label: '社区贡献者', value: summary.value.contributors, description: '发现一起共建的伙伴', link: '/members' },
  { label: '收录项目', value: summary.value.repositories, description: summary.value.projectPeriod ? `项目快照 ${summary.value.projectPeriod}` : '了解社区项目', link: '/projects' },
  { label: '研究方向', value: summary.value.domains, description: '找到感兴趣的领域', link: '/organization' },
  { label: '本期提交', value: summary.value.commits, description: summary.value.days ? `采集时近 ${summary.value.days} 天` : '查看贡献活跃度', link: '/rankings' }
])
</script>

<template>
  <section class="home-overview" aria-labelledby="overview-heading">
    <div class="overview-heading">
      <h2 id="overview-heading">社区数据一览</h2>
      <p>基于已采集数据<span v-if="summary.updated"> · 提交数据更新于 <time :datetime="summary.updated">{{ summary.updated }}</time></span></p>
    </div>
    <div class="overview-metrics">
      <a v-for="metric in metrics" :key="metric.label" :href="withBase(metric.link)" class="overview-metric">
        <span class="metric-label">{{ metric.label }}</span>
        <strong>{{ metric.value == null ? '—' : Number(metric.value).toLocaleString('zh-CN') }}</strong>
        <span class="metric-description">{{ metric.description }}</span>
      </a>
    </div>
  </section>
</template>

<style scoped>
.home-overview { max-width: 1152px; margin: 0 auto 48px; padding: 26px 0 30px; border-top: 1px solid var(--vp-c-divider); border-bottom: 1px solid var(--vp-c-divider); }
.overview-heading { display: flex; align-items: baseline; justify-content: space-between; flex-wrap: wrap; gap: 8px 20px; margin-bottom: 22px; }
.overview-heading h2 { font-size: 19px; font-weight: 650; letter-spacing: -.02em; }
.overview-heading p { color: var(--vp-c-text-2); font-size: 12px; }
.overview-metrics { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 24px; }
.overview-metric { display: flex; flex-direction: column; align-items: flex-start; gap: 8px; padding: 0 0 0 24px; border-left: 1px solid var(--vp-c-divider); border-radius: 2px; }
.overview-metric:first-child { padding-left: 0; border-left: 0; }
.metric-label { font-size: 13px; color: var(--vp-c-text-2); }
.overview-metric strong { font-size: 36px; font-weight: 650; line-height: 1.15; letter-spacing: -.04em; font-variant-numeric: tabular-nums; color: var(--vp-c-text-1); transition: color .2s; }
.overview-metric:hover strong { color: var(--vp-c-brand-1); }
.metric-description { font-size: 12px; line-height: 1.6; color: var(--vp-c-text-2); }
@media (max-width: 1279px) { .home-overview { margin-left: 64px; margin-right: 64px; } }
@media (max-width: 767px) { .home-overview { margin: 0 24px 32px; padding: 24px 0; } .overview-metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 24px 16px; } .overview-metric:nth-child(odd) { padding-left: 0; border-left: 0; } .overview-metric { padding-left: 16px; } .overview-metric strong { font-size: 30px; } }
</style>
