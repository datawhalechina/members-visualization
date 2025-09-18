<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  member: {
    type: Object,
    required: true
  }
})

const githubData = ref(null)
const loading = ref(true)  // 保持兼容性，但会在mounted中设为false
const error = ref(null)

// 注释：已移除实时GitHub API调用，改为使用本地CSV数据

// 获取头像URL（优先使用本地缓存）
const getAvatarUrl = (member) => {
  // 如果有本地头像路径，使用本地头像
  if (member.avatar && member.avatar.startsWith('avatars/')) {
    // 使用VitePress的base路径，避免重复
    const basePath = import.meta.env.BASE_URL || '/'
    return `${basePath}${member.avatar}`.replace(/\/+/g, '/')
  }
  // 否则使用GitHub头像URL或默认头像
  return member.avatar || `https://github.com/${member.id}.png`
}

// 获取显示名称（优先使用name，为空时使用id）
const getDisplayName = (member) => {
  // 检查name字段是否为空、null、undefined或"None"
  const name = member.name
  if (!name || name === 'null' || name === 'undefined' || name === 'None' || name.trim() === '') {
    return member.id
  }
  return name
}

onMounted(() => {
  // 直接使用CSV中的数据，不再实时调用GitHub API
  const displayName = getDisplayName(props.member)

  githubData.value = {
    login: props.member.id,
    avatar_url: getAvatarUrl(props.member),
    html_url: props.member.github,
    name: displayName,
    bio: props.member.bio || '',
    location: props.member.location || '',
    company: props.member.company || '',
    public_repos: props.member.public_repos || 0,
    followers: props.member.followers || 0,
    following: props.member.following || 0,
    totalStars: props.member.total_stars || 0,
    repos: props.member.repositories || []  // 参与的组织仓库
  }
  loading.value = false
})
</script>

<template>
  <div class="member-card">
    <div class="member-header">
      <div class="avatar-container">
        <img
          v-if="githubData?.avatar_url"
          :src="githubData.avatar_url"
          :alt="githubData?.name || member.id"
          class="avatar"
        />
        <div v-else class="avatar-placeholder">
          {{ (githubData?.name || member.id).charAt(0) }}
        </div>
      </div>
      
      <div class="member-info">
        <h3 class="member-name">
          <a :href="member.github" target="_blank" rel="noopener noreferrer">
            {{ githubData?.name || member.id }}
          </a>
        </h3>
        <p v-if="githubData?.bio" class="member-bio">{{ githubData.bio }}</p>
        <div class="member-domains">
          <span 
            v-for="domain in member.domain" 
            :key="domain" 
            class="domain-tag"
          >
            {{ domain }}
          </span>
        </div>
      </div>
    </div>

    <div v-if="githubData" class="github-stats">
      <div class="stat-item">
        <span class="stat-number">{{ githubData.public_repos || 0 }}</span>
        <span class="stat-label">仓库</span>
      </div>
      <div class="stat-item">
        <span class="stat-number">{{ githubData.totalStars || 0 }}</span>
        <span class="stat-label">总 Stars</span>
      </div>
      <div class="stat-item">
        <span class="stat-number">{{ githubData.followers || 0 }}</span>
        <span class="stat-label">关注者</span>
      </div>
      <div class="stat-item">
        <span class="stat-number">{{ githubData.following || 0 }}</span>
        <span class="stat-label">关注中</span>
      </div>
    </div>

    <div v-if="githubData?.repos?.length" class="recent-repos">
      <h4>参与的组织仓库</h4>
      <div class="repo-list">
        <div
          v-for="repoName in githubData.repos.slice(0, 5)"
          :key="repoName"
          class="repo-item"
        >
          <a
            :href="`https://github.com/datawhalechina/${repoName}`"
            target="_blank"
            rel="noopener noreferrer"
            class="repo-name"
          >
            {{ repoName }}
          </a>
          <div class="repo-meta">
            <span class="repo-org">datawhalechina</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.member-card {
  background: var(--vp-c-bg);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 10px var(--vp-shadow-1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: 1px solid var(--vp-c-border);
}

.member-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px var(--vp-shadow-2);
  border-color: var(--vp-c-brand-1);
}

.member-header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 16px;
}

.avatar-container {
  flex-shrink: 0;
}

.avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #f0f0f0;
}

.avatar-placeholder {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  font-weight: bold;
}

.member-info {
  flex: 1;
  min-width: 0;
}

.member-name {
  margin: 0 0 8px 0;
  font-size: 1.2rem;
  font-weight: bold;
}

.member-name a {
  color: var(--vp-c-text-1);
  text-decoration: none;
  transition: color 0.3s ease;
}

.member-name a:hover {
  color: var(--vp-c-brand-1);
}

.member-bio {
  margin: 0 0 12px 0;
  color: var(--vp-c-text-2);
  font-size: 0.9rem;
  line-height: 1.4;
}

.member-domains {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.domain-tag {
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-2);
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
  border: 1px solid var(--vp-c-border);
}

.github-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 16px;
  padding: 16px;
  background: var(--vp-c-bg-soft);
  border-radius: 8px;
  border: 1px solid var(--vp-c-border);
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 1.2rem;
  font-weight: bold;
  color: var(--vp-c-text-1);
}

.stat-label {
  display: block;
  font-size: 0.8rem;
  color: var(--vp-c-text-2);
  margin-top: 2px;
}

.recent-repos h4 {
  margin: 0 0 12px 0;
  font-size: 1rem;
  color: var(--vp-c-text-1);
}

.repo-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.repo-item {
  padding: 12px;
  background: var(--vp-c-bg-soft);
  border-radius: 8px;
  border-left: 3px solid var(--vp-c-brand-1);
  border: 1px solid var(--vp-c-border);
}

.repo-name {
  color: var(--vp-c-brand-1);
  text-decoration: none;
  font-weight: 600;
  font-size: 0.9rem;
}

.repo-name:hover {
  text-decoration: underline;
}

.repo-description {
  margin: 4px 0;
  color: var(--vp-c-text-2);
  font-size: 0.8rem;
  line-height: 1.3;
}

.repo-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}

.repo-language {
  font-size: 0.8rem;
  color: var(--vp-c-text-2);
  background: var(--vp-c-bg-mute);
  padding: 2px 6px;
  border-radius: 4px;
}

.repo-org {
  font-size: 0.8rem;
  color: var(--vp-c-text-2);
  background: var(--vp-c-bg-mute);
  padding: 2px 6px;
  border-radius: 4px;
}

.repo-stars {
  font-size: 0.8rem;
  color: var(--vp-c-text-2);
}

@media (max-width: 768px) {
  .github-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .member-header {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
}
</style>
