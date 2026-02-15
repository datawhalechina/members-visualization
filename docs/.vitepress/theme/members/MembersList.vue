<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import MemberCard from './MemberCard.vue'

const members = ref([])
const loading = ref(true)
const error = ref(null)
const searchQuery = ref('')
const selectedDomain = ref('')
const currentPage = ref(1)
const pageSize = 24

// 获取所有研究方向
const allDomains = computed(() => {
  const domains = new Set()
  members.value.forEach(member => {
    member.domain.forEach(domain => domains.add(domain))
  })
  return Array.from(domains).sort()
})

// 过滤并排序后的成员列表
const filteredMembers = computed(() => {
  let filtered = members.value

  // 按姓名搜索
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim()
    filtered = filtered.filter(member => {
      const displayName = (member.name && member.name !== 'null' && member.name !== 'undefined' && member.name !== 'None' && member.name.trim() !== '')
        ? member.name
        : member.id

      return displayName.toLowerCase().includes(query) ||
        member.id.toLowerCase().includes(query)
    })
  }

  // 按研究方向筛选
  if (selectedDomain.value) {
    filtered = filtered.filter(member =>
      member.domain.includes(selectedDomain.value)
    )
  }

  // 默认按负责项目数降序排序
  filtered = [...filtered].sort((a, b) => {
    const aCount = Array.isArray(a.repositories) ? a.repositories.length : 0
    const bCount = Array.isArray(b.repositories) ? b.repositories.length : 0
    return bCount - aCount
  })

  return filtered
})

// 总页数
const totalPages = computed(() => Math.ceil(filteredMembers.value.length / pageSize))

// 当前页的成员
const pagedMembers = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredMembers.value.slice(start, start + pageSize)
})

// 分页按钮列表
const pageNumbers = computed(() => {
  const total = totalPages.value
  const current = currentPage.value
  const pages = []
  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i)
  } else {
    pages.push(1)
    if (current > 3) pages.push('...')
    for (let i = Math.max(2, current - 1); i <= Math.min(total - 1, current + 1); i++) {
      pages.push(i)
    }
    if (current < total - 2) pages.push('...')
    pages.push(total)
  }
  return pages
})

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

// 筛选条件变化时重置到第一页
watch([searchQuery, selectedDomain], () => {
  currentPage.value = 1
})

// 加载成员数据
const loadMembers = async () => {
  try {
    // 根据环境动态获取base路径
    const basePath = import.meta.env.BASE_URL || '/'
    const jsonPath = `${basePath}data/members.json`.replace(/\/+/g, '/')

    const response = await fetch(jsonPath)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const responseJSON = await response.json()
    const parsedMembers = responseJSON.map(item => {
      Object.keys(item).forEach((key) => {
        let value = item[key] || '';
        if (typeof value === 'string') {
          value = value.trim().replace(/^"|"$/g, '')
        }
        if (['domain', 'repositories'].includes(key)) {
          if (value) {
            value = value.split(';').map(d => d.trim()).filter(d => d)
          } else {
            value = []
          }
        }
        item[key] = value
      })
      return item
    })

    members.value = parsedMembers
    loading.value = false
  } catch (err) {
    console.error('加载成员数据失败:', err)
    error.value = err.message
    loading.value = false
  }
}

// 清除筛选
const clearFilters = () => {
  searchQuery.value = ''
  selectedDomain.value = ''
}

onMounted(() => {
  loadMembers()
})
</script>

<template>
  <div class="members-list">
    <!-- 搜索和筛选 -->
    <div class="filters">
      <div class="search-box">
        <input v-model="searchQuery" type="text" placeholder="搜索成员姓名或ID..." class="search-input" />
        <div class="search-icon">🔍</div>
      </div>

      <div class="filter-box">
        <select v-model="selectedDomain" class="domain-select">
          <option value="">所有研究方向</option>
          <option v-for="domain in allDomains" :key="domain" :value="domain">
            {{ domain }}
          </option>
        </select>
      </div>

      <button v-if="searchQuery || selectedDomain" @click="clearFilters" class="clear-btn">
        清除筛选
      </button>
    </div>

    <!-- 结果统计 -->
    <div v-if="!loading && !error" class="results-info">
      <p>
        显示 <strong>{{ filteredMembers.length }}</strong> / {{ members.length }} 个成员
        <span v-if="selectedDomain">（研究方向：{{ selectedDomain }}）</span>
        <span v-if="searchQuery">（搜索：{{ searchQuery }}）</span>
        <span v-if="totalPages > 1" class="page-info">· 第 {{ currentPage }} / {{ totalPages }} 页</span>
      </p>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading">
      <p>正在加载成员数据...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error">
      <p>加载失败: {{ error }}</p>
    </div>

    <!-- 成员列表 -->
    <div v-else-if="filteredMembers.length > 0" class="members-grid">
      <MemberCard v-for="member in pagedMembers" :key="member.id" :member="member" />
    </div>

    <!-- 分页控件 -->
    <div v-if="totalPages > 1" class="pagination">
      <button class="page-btn" :disabled="currentPage === 1" @click="goToPage(currentPage - 1)">上一页</button>
      <template v-for="page in pageNumbers" :key="page">
        <span v-if="page === '...'" class="page-ellipsis">...</span>
        <button v-else class="page-btn" :class="{ active: page === currentPage }" @click="goToPage(page)">{{ page }}</button>
      </template>
      <button class="page-btn" :disabled="currentPage === totalPages" @click="goToPage(currentPage + 1)">下一页</button>
    </div>

    <!-- 无结果 -->
    <div v-else class="no-results">
      <p>没有找到匹配的成员</p>
      <button @click="clearFilters" class="clear-btn">清除筛选条件</button>
    </div>
  </div>
</template>

<style scoped>
.members-list {
  width: 100%;
  padding: 20px 0;
}

.filters {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
  align-items: center;
}

.search-box {
  position: relative;
  flex: 1;
  min-width: 250px;
}

.search-input {
  width: 100%;
  padding: 12px 16px 12px 44px;
  border: 2px solid var(--vp-c-border);
  border-radius: 8px;
  font-size: 16px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  transition: border-color 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--vp-c-brand-1);
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--vp-c-text-2);
}

.filter-box {
  min-width: 200px;
}

.domain-select {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid var(--vp-c-border);
  border-radius: 8px;
  font-size: 16px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  cursor: pointer;
  transition: border-color 0.3s ease;
}

.domain-select:focus {
  outline: none;
  border-color: var(--vp-c-brand-1);
}

.clear-btn {
  padding: 12px 20px;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-border);
  border-radius: 8px;
  color: var(--vp-c-text-2);
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.clear-btn:hover {
  background: var(--vp-c-bg-mute);
  border-color: var(--vp-c-brand-1);
  color: var(--vp-c-brand-1);
}

.results-info {
  margin-bottom: 20px;
  padding: 12px 16px;
  background: var(--vp-c-bg-soft);
  border-radius: 8px;
  border-left: 4px solid var(--vp-c-brand-1);
}

.results-info p {
  margin: 0;
  color: var(--vp-c-text-1);
  font-size: 14px;
}

.loading,
.error,
.no-results {
  text-align: center;
  padding: 60px 20px;
  border-radius: 12px;
  margin: 20px 0;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-border);
  color: var(--vp-c-text-1);
}

.loading {
  border-color: var(--vp-c-brand-1);
  color: var(--vp-c-brand-1);
}

.error {
  border-color: var(--vp-c-danger-1);
  color: var(--vp-c-danger-1);
}

.no-results {
  color: var(--vp-c-text-2);
}

.members-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 24px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: 32px;
  padding: 16px 0;
  flex-wrap: wrap;
}

.page-btn {
  padding: 8px 14px;
  border: 1px solid var(--vp-c-border);
  border-radius: 6px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.page-btn:hover:not(:disabled):not(.active) {
  border-color: var(--vp-c-brand-1);
  color: var(--vp-c-brand-1);
}

.page-btn.active {
  background: var(--vp-c-brand-1);
  border-color: var(--vp-c-brand-1);
  color: #fff;
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-ellipsis {
  padding: 8px 4px;
  color: var(--vp-c-text-3);
}

.page-info {
  color: var(--vp-c-text-2);
}

@media (max-width: 768px) {
  .filters {
    flex-direction: column;
    align-items: stretch;
  }

  .search-box,
  .filter-box {
    min-width: auto;
  }

  .members-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}
</style>
