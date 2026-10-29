# 👍🏻 项目统计

<script setup>
import ProjectStar from './.vitepress/theme/projects/ProjectStar.vue'
import ProjectStarAddTop5 from './.vitepress/theme/projects/ProjectStarAddTop5.vue'
import NewProjectStarAddTop3 from './.vitepress/theme/projects/NewProjectStarAddTop3.vue'
import { ref, onMounted } from 'vue'
import { loadProjectStats } from './.vitepress/theme/projects/projectData'

const startTime = ref('—')
const endTime = ref('—')

onMounted(async () => {
  try {
    const data = await loadProjectStats()
    startTime.value = data.meta?.period_start || '—'
    endTime.value = data.meta?.period_end || '—'
  } catch (error) {
    console.error('获取时间数据失败:', error)
  }
})
</script>

## 项目 Star 数

Datawhale Star 数不少于 1000 的项目近一年趋势，默认展示前 8 个项目。数据来自每月采集时的仓库 Star 总数快照，当前月份随数据同步更新。

<ProjectStar />

## Star 净增 Top 5

{{ startTime }} 至 {{ endTime }} 的采集快照之间，Star 净增数前 5 名：

<ProjectStarAddTop5 />

## 新秀项目 Top 3

{{ startTime }} 至 {{ endTime }} 的采集快照之间，基期 Star 不超过 10 的项目中，当前 Star 总数前 3 名。条形图展示同期净增数；基期尚未收录的项目按 0 计算。

<NewProjectStarAddTop3 />
