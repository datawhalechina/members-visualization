// .vitepress/theme/index.js
import { h } from 'vue'
import DefaultTheme from 'vitepress/theme'
import HomeEditorial from './home/HomeEditorial.vue'
import './custom.css'
import './styles/leaderboard-base.css'

export default {
  extends: DefaultTheme,
  Layout: () => {
    return h(DefaultTheme.Layout, null, {
      'home-hero-before': () => h(HomeEditorial)
    })
  },
  enhanceApp({ app, router, siteData }) {
    // 目前无需额外增强逻辑
  }
}

