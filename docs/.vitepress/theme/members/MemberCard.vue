<script setup>
import { ref, computed } from 'vue'
import { withBase } from 'vitepress'

const props = defineProps({
  member: {
    type: Object,
    required: true
  }
})

const showAllRepos = ref(false)
const showAllDomains = ref(false)
const reportUrl = computed(() => withBase(`/report?user=${encodeURIComponent(props.member.id)}`))
const visibleDomains = computed(() => showAllDomains.value ? props.member.domain : props.member.domain.slice(0, 3))

function handleAvatarError(event) {
  const fallback = withBase('/default-avatar.svg')
  if (!event.target.src.endsWith(fallback)) event.target.src = fallback
}

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

const githubData = computed(() => {
  // 直接使用CSV中的数据，不再实时调用GitHub API
  const displayName = getDisplayName(props.member)

  return {
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
          loading="lazy"
          width="60"
          height="60"
          @error="handleAvatarError"
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
        <p class="member-id">@{{ member.id }}</p>
        <p v-if="githubData?.bio" class="member-bio" :title="githubData.bio">{{ githubData.bio }}</p>
        <div class="member-domains">
          <span 
            v-for="domain in visibleDomains"
            :key="domain" 
            class="domain-tag"
          >
            {{ domain }}
          </span>
          <button v-if="member.domain.length > 3" class="domain-toggle" :aria-expanded="showAllDomains" @click="showAllDomains = !showAllDomains">
            {{ showAllDomains ? '收起方向' : `+${member.domain.length - 3} 个方向` }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="githubData" class="github-stats">
      <div class="stat-item">
        <span class="stat-number">{{ githubData.public_repos || 0 }}</span>
        <span class="stat-label">公开仓库</span>
      </div>
      <div class="stat-item">
        <span class="stat-number">{{ githubData.totalStars || 0 }}</span>
        <span class="stat-label">个人 Stars</span>
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
      <h4>参与项目 <span>{{ githubData.repos.length }}</span></h4>
      <div class="repo-list">
        <div
          v-for="repoName in showAllRepos ? githubData.repos : githubData.repos.slice(0, 3)"
          :key="repoName"
          class="repo-item"
        >
          <a
            :href="`https://github.com/datawhalechina/${repoName}`"
            target="_blank"
            rel="noopener noreferrer"
            class="repo-name"
            :title="repoName"
          >
            {{ repoName }}
          </a>
        </div>
      </div>
      <button v-if="githubData.repos.length > 3" class="repos-toggle" :aria-expanded="showAllRepos" @click="showAllRepos = !showAllRepos">
        {{ showAllRepos ? '收起项目' : `查看全部 ${githubData.repos.length} 个项目` }}
      </button>
    </div>
    <footer class="member-footer"><a :href="reportUrl">查看个人报告 <span class="vpi-arrow-right" aria-hidden="true"></span></a></footer>
  </div>
</template>

<style scoped>
.member-card {
  background: var(--vp-c-bg);
  border-radius: 12px;
  padding: 20px;
  margin: 0;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: 1px solid var(--vp-c-divider);
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
  margin: 0;
  font-size: 1.2rem;
  font-weight: bold;
}

.member-id { margin: 2px 0 8px; color: var(--vp-c-text-3); font-size: 12px; overflow-wrap: anywhere; }

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
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
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

.domain-toggle, .repos-toggle { color: var(--vp-c-brand-1); font-size: 12px; cursor: pointer; }
.domain-toggle { padding: 4px 2px; }
.repos-toggle { margin-top: 10px; }
.member-footer { margin-top: 18px; padding-top: 14px; border-top: 1px solid var(--vp-c-divider); }
.member-footer a { display: inline-flex; gap: 10px; align-items: center; color: var(--vp-c-brand-1); font-size: 13px; font-weight: 600; text-decoration: none; }

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

.recent-repos h4 span { margin-left: 5px; color: var(--vp-c-text-3); font-weight: 400; font-size: 12px; }

.repo-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.repo-item {
  padding: 7px 10px;
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
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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
  
  .member-header { gap: 12px; }
}
</style>
