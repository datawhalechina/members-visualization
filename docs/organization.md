# 📚 同类组织统计

<script setup>
import Organization from './.vitepress/theme/organization/Organization.vue'
</script>

## 同类组织数据概览

以下是GitHub上 Star 数排名前十的知识分享类组织情况：

<Organization />

## 数据更新

数据文件会通过 GitHub Actions 自动更新：

1. 每月自动运行数据收集脚本
2. 数据直接保存到 `docs/public/data/` 目录供前端使用

_数据最后更新时间：{{ new Date().getFullYear() }} 年 {{ new Date().getMonth() + 1 }} 月 1 日_
