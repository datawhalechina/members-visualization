# 📊 组织数据统计

<script setup>
import OrgStatsCards from './.vitepress/theme/stats/OrgStatsCards.vue'
</script>

## 📈 OSS Insight 统计面板

以下数据来自 [OSS Insight](https://next.ossinsight.io/analyze/datawhalechina)，展示 Datawhale 组织的各项统计指标：

<OrgStatsCards />

---

## 📋 数据说明

所有统计数据均基于 GitHub 公开数据，通过 OSS Insight 平台生成。您可以：

1. **切换时间范围** - 使用顶部的按钮切换 7天/28天/90天/12个月的数据视图
2. **点击卡片** - 跳转到 OSS Insight 查看更详细的分析
3. **自动适配主题** - 卡片会根据当前 VitePress 主题自动切换明亮/暗黑模式

### 指标说明

| 分组 | 指标 | 说明 |
|------|------|------|
| ⭐ 受欢迎程度 | Stars 增长趋势 | 组织获得的 Stars 总数变化趋势 |
| ⭐ 受欢迎程度 | Star 数最高仓库 | 按 Stars 数排名的热门仓库 |
| ⭐ 受欢迎程度 | 活跃仓库 | 当前最活跃的仓库排名 |
| 👥 参与者分析 | 活跃参与者趋势 | 活跃贡献者数量变化趋势 |
| 👥 参与者分析 | 新增参与者趋势 | 新加入贡献者数量变化趋势 |
| 👥 参与者分析 | 活跃参与者排名 | 最活跃的贡献者排行榜 |
| 👥 参与者分析 | 新增参与者排名 | 新加入贡献者排行榜 |
| 🤝 参与度分析 | 最活跃贡献者 | 贡献者参与度散点图分析 |
| 🤝 参与度分析 | 代码提交时间分布 | 基于北京时间的代码提交热力图 |
| 📈 生产力分析 | Stars 概览 | Stars 获取概览统计 |
| 📈 生产力分析 | 活跃贡献者 | 活跃贡献者数量统计 |
| 📈 生产力分析 | Pull Requests | PR 提交和合并统计 |
| 📈 生产力分析 | Code Reviews | 代码审查活动统计 |
| 📈 生产力分析 | Issues | Issue 创建和解决统计 |
