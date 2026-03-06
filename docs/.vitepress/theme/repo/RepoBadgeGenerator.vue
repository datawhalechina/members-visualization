<script setup>
import { computed, onMounted, ref } from 'vue'
import RepoBadge from './RepoBadge.vue'

const repoName = ref('')
const selectedRepo = ref('')
const isEmbed = ref(false)
const embedCode = ref('')
const iframeCode = ref('')
const copyStatus = ref('')
const repoOptions = ref([])

const fallbackRepos = [
  'torch-rechub',
  'self-llm',
  'happy-llm',
  'hello-agents',
  'llm-cookbook',
  'members-visualization'
]

const normalizePath = (path) => path.replace(/([^:]\/)\/+/g, '$1')
const normalizeRepo = (value = '') => value.trim().replace(/^datawhalechina\//i, '').toLowerCase()

const topRepos = computed(() => repoOptions.value.slice(0, 12))

const updateEmbedCode = (repo) => {
  if (!repo) {
    embedCode.value = ''
    iframeCode.value = ''
    return
  }
  const basePath = import.meta.env.BASE_URL || '/'
  const badgeUrl = `${window.location.origin}${basePath}badges/${repo}.png`.replace(/([^:]\/)\/+/g, '$1')
  const pageUrl = `${window.location.origin}${basePath}repo-badge?repo=${repo}`.replace(/([^:]\/)\/+/g, '$1')
  const embedUrl = `${window.location.origin}${basePath}repo-badge?repo=${repo}&embed=1`.replace(/([^:]\/)\/+/g, '$1')

  embedCode.value = `[![${repo} stats](${badgeUrl})](${pageUrl})`
  iframeCode.value = `<iframe src="${embedUrl}" width="980" height="450" frameborder="0"></iframe>`
}

const loadRepoOptions = async () => {
  try {
    const basePath = import.meta.env.BASE_URL || '/'
    const source = normalizePath(`${basePath}data/datawhalechina/organization/repo_list.json`)
    const response = await fetch(source)
    if (!response.ok) throw new Error('failed')
    const repoList = await response.json()

    const repos = repoList
      .map((item) => String(item?.name || '').split('/').pop() || '')
      .map((name) => normalizeRepo(name))
      .filter(Boolean)

    repoOptions.value = [...new Set(repos)]
  } catch (error) {
    repoOptions.value = fallbackRepos
  }
}

const chooseRepo = (repo) => {
  const normalized = normalizeRepo(repo)
  if (!normalized) return
  selectedRepo.value = normalized
  repoName.value = normalized
  updateEmbedCode(normalized)
}

const generateBadge = () => {
  chooseRepo(repoName.value)
}

const copyCode = async (code) => {
  if (!code) return
  try {
    await navigator.clipboard.writeText(code)
    copyStatus.value = 'Copied'
    setTimeout(() => {
      copyStatus.value = ''
    }, 1200)
  } catch (error) {
    copyStatus.value = 'Copy failed'
  }
}

onMounted(async () => {
  const params = new URLSearchParams(window.location.search)
  const repoFromQuery = normalizeRepo(params.get('repo') || '')
  isEmbed.value = params.get('embed') === '1'

  if (isEmbed.value) {
    document.body.classList.add('embed-mode')
  }

  await loadRepoOptions()
  const initialRepo = repoFromQuery || 'torch-rechub'
  chooseRepo(initialRepo)
})
</script>

<template>
  <RepoBadge v-if="selectedRepo" :repo-name="selectedRepo" :is-embed="isEmbed" />

  <div v-if="!isEmbed" class="repo-generator">
    <div class="repo-generator-header">
      <h2>项目统计徽章</h2>
      <p>输入仓库名称（例如：<code>torch-rechub</code>）生成可嵌入的统计卡片。</p>
    </div>

    <div class="repo-input-row">
      <input
        v-model="repoName"
        class="repo-input"
        placeholder="输入仓库名称"
        list="repo-options"
        @keydown.enter="generateBadge"
      >
      <datalist id="repo-options">
        <option v-for="repo in repoOptions" :key="repo" :value="repo" />
      </datalist>
      <button class="repo-generate-btn" @click="generateBadge">生成</button>
    </div>

    <div class="repo-quick-list">
      <button
        v-for="repo in topRepos"
        :key="`quick-${repo}`"
        class="repo-chip"
        @click="chooseRepo(repo)"
      >
        {{ repo }}
      </button>
    </div>

    <div v-if="embedCode" class="repo-code-section">
      <div class="repo-code-block">
        <div class="code-label">Markdown 图片链接（项目 README 请使用此方式嵌入）</div>
        <pre>{{ embedCode }}</pre>
        <button class="repo-copy-btn" @click="copyCode(embedCode)">{{ copyStatus || 'Copy' }}</button>
      </div>

      <div class="repo-code-block">
        <div class="code-label">iframe 嵌入代码 （其他页面请使用此方式嵌入）</div>
        <pre>{{ iframeCode }}</pre>
        <button class="repo-copy-btn" @click="copyCode(iframeCode)">{{ copyStatus || 'Copy' }}</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.repo-generator {
  border: 1px solid var(--vp-c-divider);
  border-radius: 14px;
  padding: 20px;
  margin-top: 20px;
  margin-bottom: 20px;
  background:
    radial-gradient(circle at left top, color-mix(in srgb, var(--vp-c-brand-1) 12%, transparent), transparent 45%),
    var(--vp-c-bg-soft);
}

.repo-generator-header h2 {
  margin: 0;
}

.repo-generator-header p {
  margin: 8px 0 0;
  color: var(--vp-c-text-2);
}

.repo-input-row {
  margin-top: 14px;
  display: flex;
  gap: 10px;
  align-items: center;
}

.repo-input {
  flex: 1;
  border: 1px solid var(--vp-c-divider);
  border-radius: 10px;
  padding: 10px 12px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  font-size: 14px;
}

.repo-input::-webkit-calendar-picker-indicator {
  display: none;
}

.repo-generate-btn {
  border: none;
  border-radius: 10px;
  padding: 10px 16px;
  background: #0a66d1;
  color: #fff;
  cursor: pointer;
  font-weight: 600;
}

.repo-quick-list {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.repo-chip {
  border: 1px solid var(--vp-c-divider);
  border-radius: 999px;
  padding: 4px 10px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-2);
  cursor: pointer;
  font-size: 12px;
}

.repo-chip:hover {
  color: var(--vp-c-text-1);
  border-color: #0a66d1;
}

.repo-code-section {
  margin-top: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.repo-code-block {
  position: relative;
  border: 1px solid var(--vp-c-divider);
  border-radius: 10px;
  background: var(--vp-c-bg);
  padding: 12px;
}

.code-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--vp-c-text-2);
  margin-bottom: 8px;
}

.repo-code-block pre {
  margin: 0;
  overflow-x: auto;
  font-size: 12px;
}

.repo-copy-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  padding: 4px 8px;
  background: var(--vp-c-bg-soft);
  cursor: pointer;
  font-size: 12px;
}

@media (max-width: 768px) {
  .repo-input-row {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>

<style>
body.embed-mode .VPNav,
body.embed-mode .VPSidebar,
body.embed-mode .VPFooter,
body.embed-mode .VPDocFooter {
  display: none !important;
}

body.embed-mode .VPContent,
body.embed-mode .VPDoc,
body.embed-mode .VPDoc .container {
  padding: 0 !important;
  margin: 0 !important;
}

body.embed-mode h1 {
  display: none !important;
}
</style>
