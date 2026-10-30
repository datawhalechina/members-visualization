<script setup>
import { computed } from 'vue'
import { useData, withBase } from 'vitepress'

const { frontmatter } = useData()
const summary = computed(() => frontmatter.value.communityOverview || {})
const metrics = computed(() => [
  { label: '社区贡献者', value: summary.value.contributors, link: '/members' },
  { label: '收录项目', value: summary.value.repositories, link: '/projects', detail: summary.value.projectPeriod ? `项目快照 ${summary.value.projectPeriod}` : '' },
  { label: '研究方向', value: summary.value.domains, link: '/organization' },
  { label: summary.value.days ? `近 ${summary.value.days} 天提交` : '本期提交', value: summary.value.commits, link: '/rankings' }
])
</script>

<template>
  <section class="home-overview" aria-labelledby="overview-heading">
    <div class="overview-heading">
      <h2 id="overview-heading">社区数据一览</h2>
      <p>来自 Datawhale 社区的公开数据，<br>展现社区的参与和活跃情况。</p>
    </div>
    <a v-for="metric in metrics" :key="metric.label" :href="withBase(metric.link)" class="overview-metric" :title="metric.detail || undefined">
      <strong>{{ metric.value == null ? '—' : Number(metric.value).toLocaleString('zh-CN') }}</strong>
      <span>{{ metric.label }}</span>
    </a>
    <p v-if="summary.updated" class="overview-date">采集快照 ·<br><time :datetime="summary.updated">{{ summary.updated }}</time></p>
  </section>
</template>

<style scoped>
.home-overview { display: grid; grid-template-columns: 1.6fr repeat(4, 1fr) .75fr; align-items: center; border-top: 2px solid var(--vp-c-text-1); border-bottom: 2px solid var(--vp-c-text-1); padding: 25px 0; gap: 0; }
.overview-heading h2 { margin: 0 0 8px; font: 800 clamp(23px, 2.7vw, 36px)/1.4 var(--editorial-serif); letter-spacing: -.04em; }
.overview-heading p { margin: 0; font-size: 12px; line-height: 1.8; color: var(--vp-c-text-2); }
.overview-metric { display: flex; flex-direction: column; align-items: center; justify-content: center; border-left: 1px solid var(--vp-c-divider); gap: 8px; padding: 0 10px; }
.overview-metric strong { font: 700 clamp(44px, 5vw, 68px)/1 Georgia, serif; font-variant-numeric: lining-nums tabular-nums; letter-spacing: -.055em; transition: color .2s; }
.overview-metric:hover strong { color: var(--vp-c-brand-1); }
.overview-metric span { font: 700 16px/1.5 var(--editorial-serif); }
.overview-date { margin: 0; padding-left: 20px; border-left: 1px solid var(--vp-c-divider); color: var(--vp-c-text-2); font-size: 11px; line-height: 1.7; }
@media (max-width: 959px) { .home-overview { grid-template-columns: repeat(4, 1fr); gap: 22px 0; } .overview-heading { grid-column: 1 / 4; } .overview-heading p br { display: none; } .overview-heading h2 { font-size: 26px; } .overview-date { grid-column: 4; grid-row: 1; border: 0; padding: 0; text-align: right; } .overview-metric:nth-child(2) { border-left: 0; } }
@media (max-width: 639px) { .home-overview { grid-template-columns: repeat(2, 1fr); padding: 22px 0; gap: 22px 0; } .overview-heading { grid-column: 1 / -1; } .overview-heading h2 { font-size: 26px; } .overview-heading p { font-size: 12px; } .overview-metric { align-items: flex-start; padding: 0 18px; } .overview-metric:nth-child(even) { padding-left: 0; border: 0; } .overview-metric strong { font-size: 50px; } .overview-metric span { font-size: 15px; } .overview-date { grid-row: auto; grid-column: 1 / -1; text-align: left; border-top: 1px solid var(--vp-c-divider); padding-top: 14px; } .overview-date br { display: none; } }
</style>
