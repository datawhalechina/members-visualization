# 贡献者可视化

<script setup>
import Charts from './.vitepress/theme/Charts.vue'
import MembersList from './.vitepress/theme/MembersList.vue'
</script>



## 成员详情

以下是所有贡献者的详细信息，包括 GitHub 数据和研究方向：

<MembersList />

## 使用说明

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

## 数据更新

数据文件会通过 GitHub Actions 自动更新：

1. 每日自动运行数据收集脚本
2. 手动触发工作流也可以更新数据
3. 数据直接保存到 `docs/public/data/` 目录供前端使用

## 示例数据格式

```csv
id,name,github,domain
user1,张三,https://github.com/user1,"推荐系统;CV"
user2,李四,https://github.com/user2,"NLP"
```

---

*数据最后更新时间：{{ new Date().toLocaleDateString('zh-CN') }}*
