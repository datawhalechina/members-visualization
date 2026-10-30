import { defineConfig } from 'vitepress'
import { communitySummary } from './communitySummary.mjs'

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

  transformPageData(pageData) {
    if (pageData.relativePath === 'index.md') {
      pageData.frontmatter.communityOverview = communitySummary()
    }
  },

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
      { text: "首页", link: "/" },
      {
        text: "贡献者",
        items: [
          { text: "贡献者榜单", link: "/rankings" },
          { text: "阶段贡献者", link: "/quarterly" },
          { text: "贡献者列表", link: "/members" },
          { text: "开源荣誉", link: "/rewards" },
        ],
      },
      {
        text: "数据统计",
        items: [
          { text: "OSS Insight 统计", link: "/stats" },
          { text: "项目统计", link: "/projects" },
          { text: "成员与协作分析", link: "/organization" },
          { text: "项目徽章", link: "/repo-badge" },
        ],
      },
      {
        text: "社区功能",
        items: [
          { text: "成就徽章", link: "/badges" },
          { text: "新人引导", link: "/guide" },
          { text: "个人开源报告", link: "/report" },
          { text: "点 Star", link: "/star" },
          { text: "Datawhale 官网", link: "https://www.datawhale.cn/" },
          { text: "GitHub 组织", link: "https://github.com/datawhalechina" },
        ],
      },
    ],

    // 侧边栏
    sidebar: {
      "/": [
        {
          text: "贡献者",
          items: [
            { text: "首页", link: "/" },
            { text: "贡献者榜单", link: "/rankings" },
            { text: "阶段贡献者", link: "/quarterly" },
            { text: "贡献者列表", link: "/members" },
            { text: "开源荣誉", link: "/rewards" },
          ],
        },
        {
          text: "数据统计",
          items: [
            { text: "OSS Insight 统计", link: "/stats" },
            { text: "项目统计", link: "/projects" },
            { text: "成员与协作分析", link: "/organization" },
            { text: "项目徽章", link: "/repo-badge" },
          ],
        },
        {
          text: "社区功能",
          items: [
            { text: "成就徽章", link: "/badges" },
            { text: "新人引导", link: "/guide" },
            { text: "个人开源报告", link: "/report" },
          ],
        },
        {
          text: "其他",
          items: [
            { text: "点 Star", link: "/star" },
          ],
        },
      ],
    },

    // 社交链接
    socialLinks: [
      {
        icon: { svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="currentColor" d="M12 .297c-6.63 0-12 5.373-12 12c0 5.303 3.438 9.8 8.205 11.385c.6.113.82-.258.82-.577c0-.285-.01-1.04-.015-2.04c-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729c1.205.084 1.838 1.236 1.838 1.236c1.07 1.835 2.809 1.305 3.495.998c.108-.776.417-1.305.76-1.605c-2.665-.3-5.466-1.332-5.466-5.93c0-1.31.465-2.38 1.235-3.22c-.135-.303-.54-1.523.105-3.176c0 0 1.005-.322 3.3 1.23c.96-.267 1.98-.399 3-.405c1.02.006 2.04.138 3 .405c2.28-1.552 3.285-1.23 3.285-1.23c.645 1.653.24 2.873.12 3.176c.765.84 1.23 1.91 1.23 3.22c0 4.61-2.805 5.625-5.475 5.92c.42.36.81 1.096.81 2.22c0 1.606-.015 2.896-.015 3.286c0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg>` },
        ariaLabel: "GitHub 项目仓库",
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
      options: {
        translations: {
          button: { buttonText: "搜索站内内容", buttonAriaLabel: "搜索站内内容" },
          modal: { displayDetails: "显示详情", resetButtonTitle: "清除搜索", backButtonTitle: "关闭搜索", noResultsText: "没有找到相关内容", footer: { selectText: "选择", navigateText: "切换", closeText: "关闭" } }
        }
      }
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
