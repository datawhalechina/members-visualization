# 📚 同类组织统计

<script setup>
import Organization from './.vitepress/theme/organization/Organization.vue'

import { ref, onMounted } from 'vue'

// 使用 ref 响应式变量存储数据
const startTime = ref('加载中...')
const endTime = ref('加载中...')

onMounted(async () => {
  try {
    const response = await fetch('/members-visualization/data/datawhalechina/fetch_time_key.json')
    if (response.ok) {
      const res = await response.json()
      startTime.value = res[res.length - 4]
      endTime.value = res[res.length - 1]
    }
  } catch (error) {
    console.error('获取时间数据失败:', error)
  }
})
</script>

## 同类组织数据概览

以下是 GitHub 上 Star 数排名前十的知识分享类组织在 {{ startTime }} 至 {{ endTime }} 统计周期内的变化情况：

<Organization />

## 数据更新

数据文件会通过 GitHub Actions 自动更新：

1. 每月自动运行数据收集脚本
2. 数据直接保存到 `docs/public/data/` 目录供前端使用

_数据最后更新时间：{{ new Date().getFullYear() }} 年 {{ new Date().getMonth() + 1 }} 月 1 日_
