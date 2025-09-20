// .vitepress/theme/index.js
import { h } from 'vue'
import DefaultTheme from 'vitepress/theme'
import './custom.css'
import './styles/leaderboard-base.css'

export default {
  extends: DefaultTheme,
  Layout: () => {
    return h(DefaultTheme.Layout, null, {
      // https://vitepress.dev/guide/extending-default-theme#layout-slots
    })
  },
  enhanceApp({ app, router, siteData }) {
    // 目前无需额外增强逻辑
  }
}

