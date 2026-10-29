// .vitepress/theme/index.js
import { h } from 'vue'
import DefaultTheme from 'vitepress/theme'
import HomeOverview from './home/HomeOverview.vue'
import './custom.css'
import './styles/leaderboard-base.css'

export default {
  extends: DefaultTheme,
  Layout: () => {
    return h(DefaultTheme.Layout, null, {
      'home-hero-after': () => h(HomeOverview)
    })
  },
  enhanceApp({ app, router, siteData }) {
    // 目前无需额外增强逻辑
  }
}

