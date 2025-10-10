<script setup>
import { ref, computed, watch } from 'vue'

// 接收organizationData作为props
const props = defineProps({
  organizationData: {
    type: Array,
    default: () => []
  }
})

// 表格数据状态
const tableData = ref(props.organizationData)

// 格式化数字（添加千位分隔符）
const formatNumber = (num) => {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

// 当props变化时更新表格数据
watch(() => props.organizationData, (newData) => {
  tableData.value = newData
}, { deep: true })
</script>

<template>
  <table class="organization-table">
    <thead>
      <tr>
        <th>排名</th>
        <th>组织名称</th>
        <th>Star数</th>
        <th>新增Star</th>
        <th>排名变化</th>
      </tr>
    </thead>
    <tbody>
      <tr 
        v-for="item in tableData" 
        :key="item.name"
        :class="{ 'highlight-row': item.name === 'datawhalechina' }"
      >
        <td>
          <span class="rank-number">{{ item.rank }}</span>
        </td>
        <td class="name-cell">{{ item.name }}</td>
        <td>{{ formatNumber(item.star_count) }}</td>
        <td>+{{ formatNumber(item.starAdd) }}</td>
        <td>
          <span :class="{ 'positive': item.rankAdd > 0, 'negative': item.rankAdd < 0 }">
            {{ item.rankAdd > 0 ? '+' : '' }}{{ item.rankAdd }}
          </span>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<style scoped>
.organization-table {
  width: 100%;
  border-collapse: collapse;
  margin: 0;
}

.organization-table th {
  padding: 14px 16px;
  text-align: left;
  font-weight: 600;
  font-size: 14px;
}

.organization-table td {
  padding: 12px 16px;
  font-size: 14px;
}

.rank-number {
  display: inline-block;
  width: 28px;
  height: 28px;
  line-height: 28px;
  text-align: center;
  background: var(--vp-c-brand-1);
  color: white;
  border-radius: 50%;
  font-size: 14px;
}

.name-cell {
  font-weight: 500;
}

.positive {
  color: var(--vp-c-success-1);
  font-weight: 500;
}

.negative {
  color: var(--vp-c-danger-1);
  font-weight: 500;
}

.no-data {
  text-align: center;
  padding: 60px 20px;
  border-radius: 12px;
}

/* 高亮行样式 - 增加整体边框和阴影 */
.highlight-row {
  background-color: rgba(78, 205, 196, 0.1);
  /* 整体边框加粗 */
  border: 2px solid #4ecdc4;
  /* 阴影效果 */
  box-shadow: 0 4px 12px rgba(78, 205, 196, 0.3);
  transition: all 0.3s ease; /* 过渡动画 */
}

/* 文字样式 */
.highlight-row .name-cell {
  color: rgb(34, 101, 203);
  font-weight: bold;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  font-size: 15px;
  transition: all 0.3s ease;
}

/* 悬浮效果增强 */
.highlight-row:hover {
  transform: translateY(-2px); /* 轻微上浮 */
  box-shadow: 0 6px 16px rgba(78, 205, 196, 0.4); /* 加深阴影 */
  border-color: #38b2ac; /* 边框颜色加深 */
}

.highlight-row:hover .name-cell {
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

@media (max-width: 768px) {
  .search-box {
    max-width: 100%;
  }

  .organization-table {
    font-size: 13px;
  }

  .organization-table th,
  .organization-table td {
    padding: 10px 8px;
  }

  .rank-number {
    width: 24px;
    height: 24px;
    line-height: 24px;
    font-size: 12px;
  }

  /* 响应式调整高亮样式 */
  .highlight-row {
    border-width: 1.5px;
    box-shadow: 0 3px 8px rgba(78, 205, 196, 0.25);
  }
}
</style>
