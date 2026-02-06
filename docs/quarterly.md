---
layout: doc
title: 季度贡献者
description: Datawhale 季度贡献者统计与展示
---

<script setup>
import QuarterlyContributors from './.vitepress/theme/quarterly/QuarterlyContributors.vue'
</script>

# 🎖️ 季度贡献者

<QuarterlyContributors />

---

## 📖 说明

### 评选标准

- **🏆 卓越贡献者**：有效commit次数 ≥ 50次
- **⭐ 优秀贡献者**：有效commit次数 ≥ 10次

### 有效commit定义

有效commit是指至少包含一个文件新增行数 ≥ 10行的commit。

这个标准旨在识别实质性的代码贡献，过滤掉仅包含小修改（如typo修复、格式调整）的提交。

### 数据来源

数据通过 GitHub API 自动采集，统计范围包括 Datawhale 组织下所有公开仓库的贡献记录。

### 更新频率

季度数据在每个季度结束后手动生成和更新。
