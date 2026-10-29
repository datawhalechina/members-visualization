# 📊 OSS Insight 统计

<script setup>
import OrgStatsCards from './.vitepress/theme/stats/OrgStatsCards.vue'
import { ref } from 'vue'

const selectedPeriod = ref('past_90_days')
</script>

以下数据来自 [OSS Insight](https://next.ossinsight.io/analyze/datawhalechina)，展示 Datawhale 组织的各项统计指标。点击卡片可跳转查看详细分析。

<OrgStatsCards v-model:period="selectedPeriod" :selector-only="true" />

## ⭐ 受欢迎程度

<OrgStatsCards :period="selectedPeriod" :show-period-selector="false" group="popularity" />

## 👥 参与者分析

<OrgStatsCards :period="selectedPeriod" :show-period-selector="false" group="participants" />

## 🤝 参与度分析

<OrgStatsCards :period="selectedPeriod" :show-period-selector="false" group="engagement" />

## 📈 生产力分析

<OrgStatsCards :period="selectedPeriod" :show-period-selector="false" group="productivity" />
