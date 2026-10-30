---
layout: doc
title: 阶段贡献者
description: 按月份范围查看 Datawhale 贡献者的有效提交与参与项目
---

<script setup>
import QuarterlyContributors from './.vitepress/theme/quarterly/QuarterlyContributors.vue'
</script>

# 阶段贡献者

按已发布的月份范围查看贡献成果，支持跨季度统计。选择周期后，可一键复制卓越与优秀贡献者名单。

<QuarterlyContributors />

---

## 评选标准

| 等级 | 条件 |
|------|------|
| 🏆 卓越贡献者 | 有效 commit ≥ 50 次 |
| ⭐ 优秀贡献者 | 有效 commit ≥ 10 次 |

有效 commit：至少包含一个文件新增行数 ≥ 10 行的提交，旨在识别实质性代码贡献。
