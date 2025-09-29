# 👍🏻 组织项目统计

<script setup>
import ProjectStar from './.vitepress/theme/projects/ProjectStar.vue'
import ProjectStarAddTop5 from './.vitepress/theme/projects/ProjectStarAddTop5.vue'
import NewProjectStarAddTop3 from './.vitepress/theme/projects/NewProjectStarAddTop3.vue'
</script>

## 项目 Star 数

以下是近一年 Datawhale 所有 Star 数大于 1000 的项目 Star 数的情况：

注：拖动右侧滚动条可以对图表进行缩放。

<ProjectStar />

## 项目本年度 Star 增长数 Top5

以下是近一年 Datawhale 所有 Star 数大于 1000 的项目 Star 增长数前 5 名：

<ProjectStarAddTop5 />

## 本季度新项目 Star 增长数 Top3

以下是近三个月 Datawhale 所有新增项目中 Star 增长数前 3 名：

<NewProjectStarAddTop3 />

## 数据更新

数据文件会通过 GitHub Actions 自动更新：

1. 每月自动运行数据收集脚本
2. 数据直接保存到 `docs/public/data/` 目录供前端使用

_数据最后更新时间：{{ new Date().getFullYear() }} 年 {{ new Date().getMonth() + 1 }} 月 1 日_
