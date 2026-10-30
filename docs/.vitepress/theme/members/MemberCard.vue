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
.member-card { background: transparent; border: 0; border-top: 2px solid var(--vp-c-text-1); border-radius: 0; padding: 24px 0 18px; margin: 0; min-width: 0; }
.member-header { display: flex; align-items: flex-start; gap: 16px; margin-bottom: 20px; }
.avatar-container { flex-shrink: 0; }
.avatar { width: 64px; height: 64px; border-radius: 4px; object-fit: cover; border: 1px solid var(--vp-c-divider); padding: 3px; }
.avatar-placeholder { width: 64px; height: 64px; border-radius: 4px; background: var(--vp-c-bg-soft); color: var(--vp-c-brand-1); display: flex; align-items: center; justify-content: center; font: 800 30px var(--editorial-serif); }
.member-info { flex: 1; min-width: 0; }
.member-name { margin: 0; font: 800 22px/1.4 var(--editorial-serif); overflow-wrap: anywhere; }
.member-name a { color: var(--vp-c-text-1); text-decoration: none; }
.member-name a:hover { color: var(--vp-c-brand-1); }
.member-id { margin: 3px 0 10px; color: var(--vp-c-text-3); font-size: 12px; overflow-wrap: anywhere; }
.member-bio { margin: 0 0 12px; color: var(--vp-c-text-2); font-size: 13px; line-height: 1.8; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.member-domains { display: flex; flex-wrap: wrap; gap: 6px; }
.domain-tag { color: var(--vp-c-text-2); background: var(--vp-c-bg-soft); padding: 2px 7px; border-radius: 2px; font-size: 11px; line-height: 1.8; }
.domain-toggle, .repos-toggle { color: var(--vp-c-brand-1); font-size: 12px; cursor: pointer; }
.domain-toggle { padding: 2px; }
.repos-toggle { margin-top: 10px; text-decoration: underline; text-underline-offset: 4px; }
.github-stats { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); margin-bottom: 20px; padding: 14px 0; border-block: 1px solid var(--vp-c-divider); }
.stat-item { text-align: center; border-right: 1px solid var(--vp-c-divider); min-width: 0; }
.stat-item:last-child { border: 0; }
.stat-number { display: block; font: 700 24px/1.3 Georgia, serif; color: var(--vp-c-text-1); overflow-wrap: anywhere; }
.stat-label { display: block; font-size: 11px; color: var(--vp-c-text-2); margin-top: 4px; }
.recent-repos h4 { margin: 0 0 8px; font: 700 15px/1.5 var(--editorial-serif); color: var(--vp-c-text-1); }
.recent-repos h4 span { margin-left: 5px; color: var(--editorial-red); font: italic 16px Georgia, serif; }
.repo-list { display: flex; flex-direction: column; gap: 0; }
.repo-item { padding: 8px 0; border-bottom: 1px solid var(--vp-c-divider); }
.repo-name { display: block; color: var(--vp-c-brand-1); text-decoration: none; font-weight: 500; font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.repo-name:hover { text-decoration: underline; }
.member-footer { margin-top: 22px; }
.member-footer a { display: inline-flex; gap: 10px; align-items: center; color: var(--vp-c-brand-1); font-size: 13px; font-weight: 600; text-decoration: underline; text-underline-offset: 5px; }
@media (max-width: 639px) { .member-header { gap: 14px; } .member-name { font-size: 21px; } }
</style>
