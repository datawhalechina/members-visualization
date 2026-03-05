import { defineConfig } from 'vitepress'

// 1. 获取环境变量并判断
// 如果环境变量 EDGEONE 等于 '1'，说明在 EdgeOne 环境，使用根路径 '/'
// 否则默认是 GitHub Pages 环境，使用仓库子路径
const isEdgeOne = process.env.EDGEONE === '1'
const baseConfig = isEdgeOne ? '/' : '/members-visualization/'

export default defineConfig({
  title: "Datawhale 数据可视化",
  description: "Datawhale 组织数据可视化展示平台",
  base: baseConfig,

  // 语言设置
  lang: "zh-CN",

  // 路由配置
  cleanUrls: true,

  // 构建配置
  vite: {
    build: {
      chunkSizeWarningLimit: 2000,
    },
  },

  // 网站头部配置
  head: [
    [
      "meta",
      { name: "viewport", content: "width=device-width, initial-scale=1.0" },
    ],
    [
      "meta",
      {
        name: "keywords",
        content:
          "Datawhale, 数据可视化, 贡献者展示, 项目统计, ECharts, GitHub, 研究方向",
      },
    ],
    ["meta", { name: "author", content: "Datawhale" }],
    ["meta", { property: "og:title", content: "Datawhale 数据可视化" }],
    [
      "meta",
      {
        property: "og:description",
        content: "Datawhale 组织贡献者研究方向可视化展示平台",
      },
    ],
    ["meta", { property: "og:type", content: "website" }],
    ["link", { rel: "icon", type: "image/png", href: `${baseConfig}logo.png` }],
    ["link", { rel: "apple-touch-icon", href: `${baseConfig}logo.png` }],
  ],

  themeConfig: {
    // 网站标题和 Logo
    logo: "/logo.png",
    siteTitle: "Datawhale 可视化",

    // 导航栏
    nav: [
      { text: "🏠 首页", link: "/" },
      {
        text: "👥 贡献者",
        items: [
          { text: "🏆 贡献者榜单", link: "/rankings" },
          { text: "🎖️ 季度贡献者", link: "/quarterly" },
          { text: "👥 贡献者列表", link: "/members" },
          { text: "🏅 开源荣誉", link: "/rewards" },
        ],
      },
      {
        text: "📊 数据统计",
        items: [
          { text: "📊 OSS Insight 统计", link: "/stats" },
          { text: "👍🏻 项目统计", link: "/projects" },
          { text: "📚 成员与协作分析", link: "/organization" },
          { text: "🎯 项目徽章", link: "/repo-badge" },
        ],
      },
      {
        text: "🎮 社区功能",
        items: [
          { text: "🏅 成就徽章", link: "/badges" },
          { text: "🗺️ 新人引导", link: "/guide" },
          { text: "📋 开源年报", link: "/report" },
        ],
      },
      { text: "⭐ 点 Star", link: "/star" },
      {
        text: "🔗 相关链接",
        items: [
          { text: "Datawhale 官网", link: "https://www.datawhale.cn/" },
          { text: "GitHub 组织", link: "https://github.com/datawhalechina" },
          {
            text: "项目仓库",
            link: "https://github.com/datawhalechina/members-visualization",
          },
        ],
      },
    ],

    // 侧边栏
    sidebar: {
      "/": [
        {
          text: "👥 贡献者",
          items: [
            { text: "🏠 首页", link: "/" },
            { text: "🏆 贡献者榜单", link: "/rankings" },
            { text: "🎖️ 季度贡献者", link: "/quarterly" },
            { text: "👥 贡献者列表", link: "/members" },
            { text: "🏅 开源荣誉", link: "/rewards" },
          ],
        },
        {
          text: "📊 数据统计",
          items: [
            { text: "📊 OSS Insight 统计", link: "/stats" },
            { text: "👍🏻 项目统计", link: "/projects" },
            { text: "📚 成员与协作分析", link: "/organization" },
            { text: "🎯 项目徽章", link: "/repo-badge" },
          ],
        },
        {
          text: "🎮 社区功能",
          items: [
            { text: "🏅 成就徽章", link: "/badges" },
            { text: "🗺️ 新人引导", link: "/guide" },
            { text: "📋 开源年报", link: "/report" },
          ],
        },
        {
          text: "🔗 其他",
          items: [
            { text: "⭐ 点 Star", link: "/star" },
          ],
        },
      ],
    },

    // 社交链接
    socialLinks: [
      {
        icon: "github",
        link: "https://github.com/datawhalechina/members-visualization",
      },
    ],

    // 页脚
    footer: {
      message: '<a href="https://beian.miit.gov.cn/" target="_blank">京ICP备2026002630号-1</a> | <a href="https://beian.mps.gov.cn/#/query/webSearch?code=11010602202215" rel="noreferrer" target="_blank">京公网安备11010602202215号</a>',
      copyright: '基于 MIT 协议发布 | 使用 VitePress + ECharts 构建'
    },

    // 搜索配置 - 暂时简化
    search: {
      provider: "local",
    },

    // 编辑链接
    editLink: {
      pattern:
        "https://github.com/datawhalechina/members-visualization/edit/main/docs/:path",
      text: "在 GitHub 上编辑此页面",
    },

    // 最后更新时间
    lastUpdated: {
      text: "最后更新于",
      formatOptions: {
        dateStyle: "short",
        timeStyle: "medium",
      },
    },

    // 文档页脚导航
    docFooter: {
      prev: "上一页",
      next: "下一页",
    },

    // 大纲配置
    outline: {
      label: "页面导航",
    },

    // 返回顶部
    returnToTopLabel: "回到顶部",
  },
});
