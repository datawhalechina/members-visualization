# 📚 成员与协作分析

<script setup>
import Organization from './.vitepress/theme/organization/Organization.vue'
import Charts from './.vitepress/theme/stats/Charts.vue'
import DataExport from './.vitepress/theme/stats/DataExport.vue'
import CollaborationNetwork from './.vitepress/theme/collaboration/CollaborationNetwork.vue'
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

## 同类组织对比

GitHub 上 Star 数排名前十的知识分享类组织在 {{ startTime }} 至 {{ endTime }} 统计周期内的变化情况：

<Organization />

## 研究方向分布

<Charts />

## 仓库协作网络

通过共同参与的仓库，展示成员之间的协作关系。两位成员参与了同一个仓库，即视为存在协作关系。

<CollaborationNetwork />

## 数据导出

<DataExport />
