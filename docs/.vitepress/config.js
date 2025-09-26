// 根据环境动态设置 base 路径
const base = process.env.NODE_ENV === 'production' ? '/members-visualization/' : '/'

module.exports = {
  title: 'Datawhale 贡献者可视化',
  description: 'Datawhale 组织贡献者研究方向可视化展示平台',
  base,

  // 语言设置
  lang: 'zh-CN',

  // 路由配置
  cleanUrls: true,

  // 构建配置
  vite: {
    build: {
      chunkSizeWarningLimit: 2000
    }
  },

  // 网站头部配置
  head: [
    ['meta', { name: 'viewport', content: 'width=device-width, initial-scale=1.0' }],
    ['meta', { name: 'keywords', content: 'Datawhale, 数据可视化, 贡献者展示, ECharts, GitHub, 研究方向' }],
    ['meta', { name: 'author', content: 'Datawhale' }],
    ['meta', { property: 'og:title', content: 'Datawhale 贡献者可视化' }],
    ['meta', { property: 'og:description', content: 'Datawhale 组织贡献者研究方向可视化展示平台' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['link', { rel: 'icon', type: 'image/png', href: `${base}logo.png` }],
    ['link', { rel: 'apple-touch-icon', href: `${base}logo.png` }]
  ],

  themeConfig: {
    // 网站标题和 Logo
    logo: '/logo.png',
    siteTitle: 'Datawhale 贡献者可视化',

    // 导航栏
    nav: [
      { text: '🏠 首页', link: '/' },
      { text: '🏆 榜单页', link: '/rankings' },
      { text: '👥 贡献者页', link: '/members' },
      { text: '📈 统计页', link: '/stats' },
      { text: '⭐ 点 Star', link: '/star' },
      {
        text: '🔗 相关链接',
        items: [
          { text: 'Datawhale 官网', link: 'https://www.datawhale.cn/' },
          { text: 'GitHub 组织', link: 'https://github.com/datawhalechina' },
          { text: '项目仓库', link: 'https://github.com/datawhalechina/members-visualization' }
        ]
      }
    ],

    // 侧边栏
    sidebar: {
      '/': [
        {
          text: '📋 导航菜单',
          items: [
            { text: '🏠 首页', link: '/' },
            { text: '🏆 榜单页', link: '/rankings' },
            { text: '👥 贡献者页', link: '/members' },
            { text: '📈 统计页', link: '/stats' },
            { text: '⭐ 点 Star', link: '/star' },
          ]
        }
      ]
    },

    // 社交链接
    socialLinks: [
      { icon: 'github', link: 'https://github.com/datawhalechina/members-visualization' }
    ],

    // 页脚
    footer: {
      message: '基于 MIT 协议发布 | 使用 VitePress + ECharts 构建',
      copyright: 'Copyright © 2025 Datawhale 开源社区'
    },

    // 搜索配置 - 暂时简化
    search: {
      provider: 'local'
    },

    // 编辑链接
    editLink: {
      pattern: 'https://github.com/datawhalechina/members-visualization/edit/main/docs/:path',
      text: '在 GitHub 上编辑此页面'
    },

    // 最后更新时间
    lastUpdated: {
      text: '最后更新于',
      formatOptions: {
        dateStyle: 'short',
        timeStyle: 'medium'
      }
    },

    // 文档页脚导航
    docFooter: {
      prev: '上一页',
      next: '下一页'
    },

    // 大纲配置
    outline: {
      label: '页面导航'
    },

    // 返回顶部
    returnToTopLabel: '回到顶部'
  }
}
