# 👍🏻 项目统计

<script setup>
import ProjectStar from './.vitepress/theme/projects/ProjectStar.vue'
import ProjectStarAddTop5 from './.vitepress/theme/projects/ProjectStarAddTop5.vue'
import NewProjectStarAddTop3 from './.vitepress/theme/projects/NewProjectStarAddTop3.vue'
import { ref, onMounted } from 'vue'

const startTime = ref('加载中...')
const endTime = ref('加载中...')

onMounted(async () => {
  try {
    const basePath = import.meta.env.BASE_URL || '/'
    const timePath = `${basePath}data/datawhalechina/fetch_time_key.json`.replace(/\/+/g, '/')
    const response = await fetch(timePath)
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

## 项目 Star 数

Datawhale 所有 Star 数大于 1000 的项目近一年趋势。拖动右侧滚动条可缩放图表。

<ProjectStar />

## Star 增长 Top 5

{{ startTime }} 至 {{ endTime }} 统计周期内，Star 增长数前 5 名：

<ProjectStarAddTop5 />

## 新秀项目 Top 3

{{ startTime }} 至 {{ endTime }} 统计周期内，新秀项目 Star 增长数前 3 名：

<NewProjectStarAddTop3 />
