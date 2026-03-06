# 🏆 贡献者榜单

<script setup>
import Rankings from './.vitepress/theme/rankings/Rankings.vue'
</script>

基于 GitHub 数据的多维度排行榜，支持按研究方向筛选。

<Rankings />

---

## 榜单说明

| 榜单 | 计算规则 |
|------|----------|
| 🔥 一周卷王 | 近 7 天 commit 数 + 连续性/多仓库/质量奖励 |
| 🌙 夜猫榜 | 深夜（22:00-06:00）commit 数 × 2 + 深夜比例/连续性奖励 |
| 🏆 人气王 | Followers × 0.6 + 组织仓库总 Stars × 0.4 |
| 💼 多产榜 | 参与组织仓库数量 |
| 🤝 社交达人 | GitHub Following 数量 |
| ⭐ 新星榜 | (Followers + Stars) / 仓库数 × 新人加成 |
| 🌟 综合实力 | Stars × 0.3 + Followers × 0.25 + 仓库数 × 0.2 + Following × 0.15 + 贡献数 × 0.1 |
