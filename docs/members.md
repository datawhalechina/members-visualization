# 👥 贡献者列表

<script setup>
import MembersList from './.vitepress/theme/members/MembersList.vue'
</script>



## 成员详情

以下是所有贡献者的详细信息，包括 GitHub 数据和研究方向：

<MembersList />

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
