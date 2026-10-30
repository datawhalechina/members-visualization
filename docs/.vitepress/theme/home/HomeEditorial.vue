<script setup>
import { withBase } from 'vitepress'
import HomeOverview from './HomeOverview.vue'
import EditorialIcon from './EditorialIcon.vue'

const features = [
  { number: '03', title: '个人开源报告', description: '记录并分享你的开源足迹。', action: '生成个人报告', link: '/report', icon: 'report' },
  { number: '04', title: '成就徽章', description: '认可你在社区的贡献。', action: '查看成就徽章', link: '/badges', icon: 'medal' },
  { number: '05', title: '新人引导', description: '从这里开始你的第一次贡献。', action: '查看新手指南', link: '/guide', icon: 'compass' },
  { number: '06', title: '组织统计', description: '探索社区的整体活跃情况。', action: '查看社区统计', link: '/stats', icon: 'chart' }
]
</script>

<template>
  <main id="main-content" class="editorial-home">
    <section class="editorial-hero" aria-labelledby="home-heading">
      <div class="hero-copy">
        <h1 id="home-heading">看见每一份<br>开源贡献</h1>
        <svg class="hero-underline" viewBox="0 0 420 34" fill="none" aria-hidden="true"><path d="M3 24C114 4 262-1 234 11s-60 20 17 17c55-2 115-6 165-12" stroke="currentColor" stroke-width="2" stroke-linecap="round" /></svg>
        <p class="hero-description">认识社区伙伴，发现感兴趣的项目，<br class="desktop-break">记录自己的开源足迹。</p>
        <div class="hero-actions">
          <a class="editorial-button primary" :href="withBase('/members')">探索社区贡献者 <EditorialIcon /></a>
          <a class="editorial-button secondary" :href="withBase('/report')">查看个人报告</a>
        </div>
        <a class="editorial-link hero-guide" :href="withBase('/guide')">开始你的第一次贡献 <EditorialIcon /></a>
      </div>
      <div class="hero-art">
        <img :src="withBase('/editorial/hero.webp')" alt="蓝色鲸鱼连接开源笔记、项目与社区伙伴的纸张拼贴插画" width="1200" height="1000" fetchpriority="high" decoding="async">
      </div>
    </section>
    <HomeOverview />
    <section class="editorial-features" aria-label="探索社区">
      <div class="feature-stories">
        <a class="feature-story" :href="withBase('/members')">
          <div class="story-copy">
            <span class="feature-number" aria-hidden="true">01</span>
            <h2>找到志同道合的伙伴</h2>
            <p>搜索贡献者，发现有相同兴趣的社区伙伴。</p>
            <span class="editorial-link">探索贡献者 <EditorialIcon /></span>
          </div>
          <img :src="withBase('/editorial/people.webp')" alt="三位社区伙伴一起交流" width="600" height="600" loading="lazy" decoding="async">
        </a>
        <a class="feature-story" :href="withBase('/projects')">
          <div class="story-copy">
            <span class="feature-number" aria-hidden="true">02</span>
            <h2>发现社区项目</h2>
            <p>浏览社区收录的开源项目，了解每月的 Star 趋势。</p>
            <span class="editorial-link">探索项目 <EditorialIcon /></span>
          </div>
          <img :src="withBase('/editorial/projects.webp')" alt="开源项目笔记与海洋明信片拼贴" width="600" height="600" loading="lazy" decoding="async">
        </a>
      </div>
      <div class="feature-index">
        <a v-for="feature in features" :key="feature.link" class="index-item" :href="withBase(feature.link)">
          <div class="index-copy">
            <h2><span class="feature-number" aria-hidden="true">{{ feature.number }}</span>{{ feature.title }}</h2>
            <p>{{ feature.description }}</p>
            <span class="editorial-link">{{ feature.action }} <EditorialIcon /></span>
          </div>
          <EditorialIcon :name="feature.icon" class="feature-icon" />
        </a>
      </div>
    </section>
    <div class="editorial-signoff"><p><strong>Datawhale</strong><span> · 与开源社区共同成长</span></p><svg viewBox="0 0 120 20" fill="none" aria-hidden="true"><path d="M2 12c25-18 49 13 80 0 12-5 21-7 36-4" stroke="currentColor" /></svg></div>
  </main>
</template>

<style scoped>
.editorial-home { max-width: 1420px; margin: 0 auto; padding: 0 46px; }
.editorial-hero { display: grid; grid-template-columns: 40% 60%; align-items: center; min-height: 650px; padding: 24px 0 30px; }
.hero-copy { position: relative; z-index: 1; padding: 16px 0; }
.hero-copy h1 { margin: 0; font: 900 clamp(68px, 8vw, 110px)/1.16 var(--editorial-serif); color: var(--vp-c-text-1); letter-spacing: -.065em; white-space: nowrap; }
.hero-underline { display: block; width: 95%; height: 35px; color: var(--editorial-red); margin: 10px 0 18px; }
.hero-description { margin: 0; font-size: clamp(17px, 1.65vw, 23px); line-height: 1.7; font-family: var(--editorial-serif); font-weight: 700; color: var(--vp-c-text-1); }
.hero-actions { display: flex; gap: 16px; margin-top: 28px; flex-wrap: wrap; }
.editorial-button { display: inline-flex; align-items: center; justify-content: center; gap: 12px; padding: 14px 22px; min-height: 50px; border: 1px solid var(--vp-c-text-2); border-radius: 3px; font-size: 15px; font-weight: 600; transition: background .2s, border-color .2s; }
.editorial-button.primary { background: var(--editorial-blue); border-color: var(--editorial-blue); color: #fff; }
.editorial-button.primary:hover { background: var(--vp-c-brand-2); border-color: var(--vp-c-brand-2); }
.editorial-button.secondary:hover { background: var(--vp-c-bg-soft); border-color: var(--vp-c-brand-1); }
.editorial-link { display: inline-flex; align-items: center; gap: 9px; color: var(--vp-c-brand-1); font-size: 14px; font-weight: 600; text-decoration: underline; text-underline-offset: 7px; text-decoration-thickness: 1px; }
.hero-guide { margin-top: 28px; }
.hero-art { width: 105%; margin-left: -3%; }
.hero-art img { width: 100%; height: auto; aspect-ratio: 1.5; object-fit: contain; }
.feature-stories { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); padding: 22px 0 16px; border-bottom: 1px solid var(--vp-c-divider); }
.feature-story { display: flex; min-height: 230px; min-width: 0; align-items: center; position: relative; overflow: hidden; }
.feature-story:first-child { border-right: 1px solid var(--vp-c-divider); padding-right: 18px; }
.feature-story:last-child { padding-left: 30px; }
.story-copy { position: relative; width: 59%; z-index: 1; }
.feature-number { color: var(--editorial-red); font: italic 700 54px/1 Georgia, serif; letter-spacing: -.05em; }
.story-copy h2 { margin: 14px 0; font: 800 clamp(23px, 2.15vw, 30px)/1.45 var(--editorial-serif); letter-spacing: -.04em; }
.story-copy p { font-size: 14px; line-height: 1.85; color: var(--vp-c-text-2); max-width: 230px; margin: 0 0 18px; }
.feature-story img { width: 53%; height: auto; aspect-ratio: 1; object-fit: contain; margin-left: -12%; align-self: flex-end; transition: transform .3s; }
.feature-story:hover img { transform: translateY(-4px); }
.feature-story:hover h2, .index-item:hover h2 { color: var(--vp-c-brand-1); }
.feature-index { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); padding: 28px 0; border-bottom: 1.5px solid var(--vp-c-text-1); }
.index-item { display: flex; align-items: center; gap: 10px; padding: 0 20px; border-right: 1px solid var(--vp-c-divider); min-width: 0; }
.index-item:first-child { padding-left: 0; }
.index-item:last-child { border: 0; padding-right: 0; }
.index-copy { flex: 1; }
.index-copy h2 { margin: 0; font: 800 19px/1.5 var(--editorial-serif); white-space: nowrap; }
.index-copy .feature-number { font-size: 29px; margin-right: 8px; }
.index-copy p { font-size: 12px; color: var(--vp-c-text-2); line-height: 1.8; margin: 10px 0 12px; }
.index-copy .editorial-link { font-size: 13px; }
.feature-icon { width: 44px; height: 44px; color: var(--vp-c-brand-1); }
.editorial-signoff { display: flex; align-items: center; justify-content: space-between; padding: 26px 0 20px; font-size: 13px; color: var(--vp-c-text-2); }
.editorial-signoff p { margin: 0; }
.editorial-signoff strong { font: 700 18px Georgia, serif; color: var(--vp-c-text-1); }
.editorial-signoff svg { width: 120px; color: var(--vp-c-text-3); }
@media (max-width: 1199px) {
  .editorial-hero { min-height: 565px; }
  .editorial-button { padding: 12px 18px; font-size: 14px; }
  .hero-actions { gap: 12px; }
  .feature-icon { width: 32px; height: 32px; }
  .index-item { padding: 0 14px; gap: 4px; }
  .index-copy h2 { font-size: 17px; }
}
@media (max-width: 959px) {
  .editorial-home { padding: 0 28px; }
  .editorial-hero { min-height: 510px; grid-template-columns: 44% 56%; }
  .hero-copy h1 { font-size: clamp(48px, 6.5vw, 64px); }
  .hero-description { font-size: 17px; }
  .hero-actions { gap: 10px; }
  .editorial-button { padding: 11px 13px; font-size: 13px; }
  .feature-index { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 24px 0; }
  .index-item { padding: 0 22px; }
  .index-item:nth-child(odd) { padding-left: 0; }
  .index-item:nth-child(even) { border-right: 0; padding-right: 0; }
  .feature-icon { width: 40px; height: 40px; }
}
@media (max-width: 639px) {
  .editorial-home { padding: 0 22px; }
  .editorial-hero { grid-template-columns: 1fr; padding: 28px 0 16px; min-height: 0; }
  .hero-copy { padding: 0; }
  .hero-copy h1 { font-size: clamp(45px, 11.6vw, 70px); letter-spacing: -.055em; }
  .hero-underline { width: 90%; max-width: 360px; margin: 2px 0 12px; height: 29px; }
  .hero-description { font-size: 17px; line-height: 1.9; }
  .desktop-break { display: none; }
  .hero-actions { margin-top: 20px; flex-wrap: nowrap; gap: 10px; }
  .editorial-button { padding: 12px 14px; font-size: 13px; }
  .hero-guide { margin-top: 22px; }
  .hero-art { width: 100%; margin: 20px 0 0; }
  .feature-stories { grid-template-columns: 1fr; padding: 0; }
  .feature-story { display: grid; grid-template-columns: 60% 40%; min-height: 250px; padding: 24px 0 !important; }
  .feature-story:first-child { border-right: 0; border-bottom: 1px solid var(--vp-c-divider); }
  .story-copy { width: auto; }
  .feature-story img { width: 100%; margin-left: 0; align-self: center; }
  .story-copy h2 { font-size: 23px; margin: 10px 0; }
  .story-copy p { font-size: 13px; max-width: 190px; }
  .feature-number { font-size: 44px; }
  .feature-index { padding: 24px 0; }
  .index-item { padding: 0 14px; align-items: flex-start; }
  .index-copy h2 { font-size: 16px; white-space: normal; }
  .index-copy .feature-number { display: block; font-size: 25px; margin: 0 0 7px; }
  .index-copy p { min-height: 44px; }
  .feature-icon { display: none; }
  .index-copy .editorial-link { font-size: 12px; gap: 3px; }
  .editorial-signoff { font-size: 11px; padding: 24px 0 16px; }
  .editorial-signoff strong { font-size: 15px; }
  .editorial-signoff svg { width: 48px; }
}
</style>
