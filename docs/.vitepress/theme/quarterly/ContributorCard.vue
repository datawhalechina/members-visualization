<template>
  <div class="contributor-card" :class="`level-${level}`">
    <div class="card-body">
      <div class="contributor-info">
        <div class="user-header">
          <img
            :src="`https://github.com/${contributor.username}.png?size=48`"
            :alt="contributor.username"
            class="avatar"
          />
          <a :href="`https://github.com/${contributor.username}`" target="_blank" class="username">
            @{{ contributor.username }}
          </a>
        </div>
        <div class="stats-row">
          <div class="stat-item">
            <span class="stat-icon">✅</span>
            <span class="stat-value">{{ contributor.valid_commits }}</span>
            <span class="stat-label">有效commit</span>
          </div>
          <div class="stat-item">
            <span class="stat-icon">📦</span>
            <span class="stat-value">{{ contributor.repos_count }}</span>
            <span class="stat-label">仓库</span>
          </div>
        </div>
      </div>

      <div class="repos-list" v-if="contributor.repos && contributor.repos.length > 0">
        <div class="repos-title">参与仓库：</div>
        <div class="repos-tags">
          <a
            v-for="repo in contributor.repos.slice(0, 4)"
            :key="repo"
            :href="`https://github.com/datawhalechina/${repo}`"
            target="_blank"
            class="repo-tag"
          >
            {{ repo }}
          </a>
          <span v-if="contributor.repos.length > 4" class="more-tag">
            +{{ contributor.repos.length - 4 }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  contributor: {
    type: Object,
    required: true
  },
  level: {
    type: String,
    required: true,
    validator: (value) => ['outstanding', 'excellent', 'active'].includes(value)
  },
  rank: {
    type: Number,
    default: null
  }
})

const levelText = computed(() => {
  const levelMap = {
    outstanding: '🏆 卓越贡献者',
    excellent: '⭐ 优秀贡献者',
    active: '👥 活跃贡献者'
  }
  return levelMap[props.level] || ''
})

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}
</script>

<style scoped>
.contributor-card {
  background: var(--vp-c-bg-soft);
  border-radius: 12px;
  padding: 20px;
  transition: transform 0.3s, box-shadow 0.3s;
  border: 2px solid transparent;
}

.contributor-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.level-outstanding {
  border-color: #ffd700;
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.05) 0%, var(--vp-c-bg-soft) 100%);
}

.level-excellent {
  border-color: #667eea;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, var(--vp-c-bg-soft) 100%);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.rank-badge {
  background: var(--vp-c-brand-1);
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: bold;
}

.level-badge {
  font-size: 14px;
  font-weight: 500;
  color: var(--vp-c-text-2);
}

.contributor-info {
  margin-bottom: 16px;
}

.user-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--vp-c-divider);
}

.username {
  font-size: 18px;
  font-weight: bold;
  color: var(--vp-c-text-1);
  text-decoration: none;
  transition: color 0.2s;
}

.username:hover {
  color: var(--vp-c-brand-1);
  text-decoration: underline;
}

.stats-row {
  display: flex;
  gap: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.stat-icon {
  font-size: 16px;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: var(--vp-c-text-1);
}

.stat-label {
  font-size: 12px;
  color: var(--vp-c-text-2);
}

.repos-list {
  margin-bottom: 16px;
}

.repos-title,
.commits-title {
  font-size: 12px;
  color: var(--vp-c-text-2);
  margin-bottom: 8px;
}

.repos-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.repo-tag {
  background: var(--vp-c-bg);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  color: var(--vp-c-brand-1);
  border: 1px solid var(--vp-c-divider);
  text-decoration: none;
  transition: background-color 0.2s, border-color 0.2s;
}

.repo-tag:hover {
  background: var(--vp-c-brand-soft);
  border-color: var(--vp-c-brand-1);
}

.more-tag {
  background: var(--vp-c-brand-1);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  color: white;
  border: none;
}

.recent-commits {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--vp-c-divider);
}

.commit-item {
  margin-bottom: 12px;
}

.commit-item:last-child {
  margin-bottom: 0;
}

.commit-message {
  font-size: 13px;
  color: var(--vp-c-text-1);
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.commit-meta {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: var(--vp-c-text-3);
}

.commit-repo {
  font-weight: 500;
}

@media (max-width: 768px) {
  .stats-row {
    flex-direction: column;
    gap: 12px;
  }
}
</style>
