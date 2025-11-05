# 📈 贡献者数据

<script setup>
import Charts from './.vitepress/theme/stats/Charts.vue'
import DataExport from './.vitepress/theme/stats/DataExport.vue'
</script>

## 📊 数据概览

以下图表展示了贡献者的研究方向分布情况：

<Charts />

## ⭐ 使用说明

### 饼图
- 显示各研究方向的贡献者数量分布
- 鼠标悬停可查看具体数值和百分比
- 点击图例可隐藏/显示对应的数据

### 柱状图
- 按贡献者数量排序显示各研究方向
- 支持鼠标悬停查看详细数值
- 渐变色彩增强视觉效果

### 关系图
- 绿色节点代表贡献者
- 蓝色节点代表研究方向
- 节点大小反映重要程度
- 支持拖拽和缩放操作
- 鼠标悬停可查看详细信息

## 📈 数据导出

<div style="margin-top: 4rem; padding-top: 2rem; border-top: 1px solid var(--vp-c-divider);">
  <DataExport />
</div>
