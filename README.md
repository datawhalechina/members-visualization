# 成员可视化

一个基于 VitePress + ECharts 的组织成员研究方向可视化展示项目。

### [🔗 访问连接](https://datawhalechina.github.io/members-visualization/)

## 🚀 功能特性

### 📊 数据可视化
- **增强饼图** - 直观显示各研究方向的成员分布比例，支持交互和动画
- **柱状图统计** - 按数量排序展示各研究方向的成员统计
- **词云展示** - 以词云形式展示热门研究方向
- **关系网络图** - 展示成员与研究方向之间的复杂关联关系
- **趋势分析** - 显示研究方向的发展趋势（模拟数据）

### 🔍 搜索和筛选
- **实时搜索** - 按成员姓名或ID进行实时搜索
- **方向筛选** - 按研究方向进行精确筛选
- **多条件组合** - 支持搜索和筛选的组合使用
- **结果统计** - 显示筛选结果的统计信息

### 👥 GitHub 集成
- **头像展示** - 自动获取并显示成员的 GitHub 头像
- **主页跳转** - 点击成员名字直接跳转到 GitHub 主页
- **仓库统计** - 显示成员的仓库数量和总 star 数
- **活跃度展示** - 展示关注者、关注中等社交数据
- **最新仓库** - 显示成员最近更新的仓库信息

### � 统计分析
- **概览信息** - 显示总成员数、研究方向数等关键指标
- **详细统计** - 每个领域的成员数量和占比分析
- **数据导出** - 支持 CSV 和 JSON 格式的数据导出
- **统计报告** - 生成完整的统计分析报告

### 🛠️ 技术特性
- **自动数据拉取** - 从 GitHub API 自动获取最新成员信息
- **响应式设计** - 完美适配各种设备和屏幕尺寸
- **自动部署** - 基于 GitHub Actions 自动构建和部署

## 📂 项目结构

```
members-visualization/
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions 自动部署配置
├── docs/
│   ├── index.md                # 首页
│   └── members.md              # 成员可视化页面
├── docs/public/data/
│   ├── members.csv             # 成员数据 (CSV 格式)
│   └── commits_weekly.json     # 提交活跃度数据 (JSON 格式)
├── .vitepress/
│   ├── config.js               # VitePress 配置
│   └── theme/
│       ├── Charts.vue          # 主图表组件
│       ├── MemberCard.vue      # 成员卡片组件
│       ├── MembersList.vue     # 成员列表组件
│       └── DataExport.vue      # 数据导出组件
├── scripts/
│   └── fetch-members.py        # 数据拉取脚本 (Python)
├── package.json
├── .gitignore
├── .npmrc
├── .editorconfig
└── README.md
```

## 🛠️ 技术栈

- **VitePress** - 静态站点生成器
- **ECharts** - 数据可视化图表库
- **echarts-wordcloud** - 词云插件
- **Vue 3** - 前端框架
- **GitHub API** - 数据源接口
- **GitHub Actions** - 自动化部署

## 📊 数据格式

数据存储在 `docs/public/data/members.csv` 文件中，格式如下：

```csv
id,name,github,domain
user1,张三,https://github.com/user1,"推荐系统;CV"
user2,李四,https://github.com/user2,"NLP"
user3,王五,https://github.com/user3,"推荐系统;NLP"
```

### 字段说明

- `id`: 成员唯一标识符
- `name`: 成员姓名
- `github`: GitHub 个人主页链接
- `domain`: 研究方向，多个方向用分号 `;` 分隔

## 🚀 快速开始

### 本地开发

1. **克隆项目**
   ```bash
   git clone https://github.com/datawhalechina/members-visualization.git
   cd members-visualization
   ```

2. **安装依赖**
   ```bash
   npm install
   ```

3. **配置环境变量（推荐）**
   ```bash
   # 复制环境变量模板
   cp .env.example .env

   # 编辑 .env 文件，添加你的 GitHub Token
   # GITHUB_TOKEN=ghp_your_token_here
   ```

   > 💡 **提示**：配置 GitHub Token 可以避免 API 速率限制，详见 [环境变量配置指南](ENVIRONMENT_SETUP.md)

4. **启动开发服务器**
   ```bash
   npm run docs:dev
   ```

5. **访问网站**
   打开浏览器访问 `http://localhost:5173`

### 数据管理

**手动更新数据**：
```bash
# 使用 Python 脚本（推荐）
npm run fetch-data

# 或直接运行 Python 脚本
python scripts/fetch-members.py

# 快速测试模式（处理较少数据）
npm run fetch-data:test
```

**环境变量配置**：
```bash
# 设置 GitHub Token（可选，避免 API 限制）
export GITHUB_TOKEN=your_github_token

# 设置组织名称（默认：datawhalechina）
export GITHUB_ORG=your_org_name
```

### 构建部署

```bash
# 构建静态文件
npm run docs:build

# 预览构建结果
npm run docs:serve
```

## 📝 使用方法

### 更新数据

数据通过 GitHub Actions 自动更新：

1. **自动更新**：每日定时运行数据收集脚本
2. **手动触发**：在 Actions 页面手动触发工作流
3. **数据存储**：直接保存到 `docs/public/data/` 目录供前端使用
4. GitHub Actions 会自动重新构建和部署

### 自定义配置

- **修改网站标题**: 编辑 `.vitepress/config.js` 中的 `title` 字段
- **调整图表样式**: 修改 `.vitepress/theme/Charts.vue` 组件
- **更改部署设置**: 编辑 `.github/workflows/deploy.yml`

## 🎨 功能说明

### 📊 数据可视化图表
- **增强饼图** - 环形设计，支持悬停交互和动画效果
- **柱状图** - 渐变色彩，显示详细统计和占比信息
- **词云图** - 动态词云，字体大小反映研究方向热度
- **关系网络图** - 力导向布局，展示成员与方向的复杂关系
- **趋势分析图** - 堆叠面积图，展示各方向的发展趋势

### 🔍 搜索和筛选
- **实时搜索** - 输入即搜，支持成员姓名和ID
- **方向筛选** - 下拉选择，精确筛选特定研究方向
- **组合筛选** - 搜索和筛选可同时使用
- **结果统计** - 实时显示筛选结果数量

### 👥 成员信息展示
- **GitHub 头像** - 自动获取并显示用户头像
- **基本信息** - 姓名、简介、研究方向标签
- **GitHub 统计** - 仓库数、star 数、关注者等
- **最新仓库** - 显示最近更新的项目信息

### 📈 数据导出功能
- **CSV 导出** - 导出完整的成员数据表格
- **JSON 报告** - 导出包含统计分析的详细报告
- **剪贴板复制** - 快速复制统计数据到剪贴板
- **实时统计** - 显示各种统计指标和分析结果

## 🔧 开发指南

### 添加新的图表类型

1. 在 `Charts.vue` 中添加新的 ref 和图表初始化代码
2. 在模板中添加对应的 DOM 元素
3. 添加相应的样式

### 修改数据源

如果需要使用其他数据源（如 API），可以修改 `Charts.vue` 中的数据获取逻辑。

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 所有贡献者

感谢所有为本项目做出贡献的开发者们！

<div align="center">

<a href="https://github.com/datawhalechina/members-visualization/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=datawhalechina/members-visualization" />
</a>

</div>

## 📞 联系我们

- GitHub: [Datawhale](https://github.com/datawhalechina)
- 官网: [https://datawhale.club](https://datawhale.club)

---

*由 Datawhale 开源社区维护*
