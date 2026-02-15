<template>
  <div class="graphql-demo">
    <h2>GraphQL API 演示</h2>
    
    <div class="demo-section">
      <h3>1. 查询统计信息</h3>
      <button @click="fetchStats" :disabled="loading">
        {{ loading ? '加载中...' : '获取统计信息' }}
      </button>
      
      <div v-if="stats" class="result-box">
        <pre>{{ JSON.stringify(stats, null, 2) }}</pre>
      </div>
    </div>

    <div class="demo-section">
      <h3>2. 查询成员列表</h3>
      <div class="filter-controls">
        <label>
          研究方向:
          <input v-model="memberFilter.domain" placeholder="例如: NLP" />
        </label>
        <label>
          最小 Followers:
          <input v-model.number="memberFilter.minFollowers" type="number" placeholder="0" />
        </label>
        <label>
          限制数量:
          <input v-model.number="memberLimit" type="number" placeholder="10" />
        </label>
      </div>
      
      <button @click="fetchMembers" :disabled="loading">
        {{ loading ? '加载中...' : '查询成员' }}
      </button>
      
      <div v-if="members.length > 0" class="result-box">
        <p>找到 {{ members.length }} 个成员</p>
        <div class="member-list">
          <div v-for="member in members" :key="member.id" class="member-item">
            <img v-if="member.avatar" :src="member.avatar" :alt="member.name" class="avatar" />
            <div class="member-info">
              <strong>{{ member.name || member.id }}</strong>
              <p>Followers: {{ member.followers }} | Following: {{ member.following }}</p>
              <p>研究方向: {{ member.domain.join(', ') }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="demo-section">
      <h3>3. 查询研究方向统计</h3>
      <label>
        显示前 N 个:
        <input v-model.number="domainLimit" type="number" placeholder="10" />
      </label>
      
      <button @click="fetchDomainStats" :disabled="loading">
        {{ loading ? '加载中...' : '查询研究方向' }}
      </button>
      
      <div v-if="domainStats.length > 0" class="result-box">
        <div class="domain-stats">
          <div v-for="stat in domainStats" :key="stat.domain" class="domain-stat-item">
            <div class="domain-name">{{ stat.domain }}</div>
            <div class="domain-count">{{ stat.count }} 人 ({{ stat.percentage }}%)</div>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: stat.percentage + '%' }"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="demo-section">
      <h3>4. 查询排行榜</h3>
      <label>
        排行榜类型:
        <select v-model="leaderboardId">
          <option value="popularity">人气王榜</option>
          <option value="productive">多产榜</option>
          <option value="social">社交达人榜</option>
          <option value="rising">新星榜</option>
          <option value="comprehensive">综合实力榜</option>
        </select>
      </label>
      
      <label>
        显示前 N 名:
        <input v-model.number="leaderboardLimit" type="number" placeholder="10" />
      </label>
      
      <button @click="fetchLeaderboard" :disabled="loading">
        {{ loading ? '加载中...' : '查询排行榜' }}
      </button>
      
      <div v-if="leaderboard" class="result-box">
        <h4>{{ leaderboard.title }}</h4>
        <p>{{ leaderboard.description }}</p>
        <div class="leaderboard-list">
          <div v-for="item in leaderboard.members" :key="item.rank" class="leaderboard-item">
            <div class="rank">{{ item.rank }}</div>
            <img v-if="item.member.avatar" :src="item.member.avatar" :alt="item.member.name" class="avatar-small" />
            <div class="member-info">
              <strong>{{ item.member.name || item.member.id }}</strong>
              <p>{{ item.scoreDisplay }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="demo-section">
      <h3>5. 使用原始 GraphQL 查询</h3>
      <textarea 
        v-model="customQuery" 
        placeholder="输入 GraphQL 查询..."
        rows="6"
      ></textarea>
      
      <button @click="executeCustomQuery" :disabled="loading">
        {{ loading ? '执行中...' : '执行查询' }}
      </button>
      
      <div v-if="customResult" class="result-box">
        <pre>{{ JSON.stringify(customResult, null, 2) }}</pre>
      </div>
    </div>

    <div v-if="error" class="error-box">
      <strong>错误:</strong> {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import {
  getStats,
  getMembers,
  getDomainStats,
  getLeaderboard,
  query
} from '../../graphql/index.js'

const loading = ref(false)
const error = ref(null)

// 统计信息
const stats = ref(null)

// 成员查询
const members = ref([])
const memberFilter = ref({ domain: '', minFollowers: 0 })
const memberLimit = ref(10)

// 研究方向统计
const domainStats = ref([])
const domainLimit = ref(10)

// 排行榜
const leaderboard = ref(null)
const leaderboardId = ref('popularity')
const leaderboardLimit = ref(10)

// 自定义查询
const customQuery = ref(`query {
  stats
}`)
const customResult = ref(null)

async function fetchStats() {
  loading.value = true
  error.value = null
  try {
    stats.value = await getStats()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function fetchMembers() {
  loading.value = true
  error.value = null
  try {
    const filter = {}
    if (memberFilter.value.domain) {
      filter.domain = memberFilter.value.domain
    }
    if (memberFilter.value.minFollowers > 0) {
      filter.minFollowers = memberFilter.value.minFollowers
    }
    
    members.value = await getMembers(filter, { 
      limit: memberLimit.value,
      sortBy: 'FOLLOWERS',
      sortOrder: 'DESC'
    })
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function fetchDomainStats() {
  loading.value = true
  error.value = null
  try {
    domainStats.value = await getDomainStats(domainLimit.value)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function fetchLeaderboard() {
  loading.value = true
  error.value = null
  try {
    leaderboard.value = await getLeaderboard(
      leaderboardId.value,
      {},
      leaderboardLimit.value
    )
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function executeCustomQuery() {
  loading.value = true
  error.value = null
  try {
    customResult.value = await query(customQuery.value)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.graphql-demo {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.demo-section {
  margin-bottom: 40px;
  padding: 20px;
  background: var(--vp-c-bg-soft);
  border-radius: 8px;
  border: 1px solid var(--vp-c-divider);
}

.demo-section h3 {
  margin-top: 0;
  color: var(--vp-c-brand-1);
}

.filter-controls {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.filter-controls label {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.filter-controls input,
.filter-controls select {
  padding: 8px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 4px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
}

button {
  padding: 10px 20px;
  background: var(--vp-c-brand-1);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background 0.3s;
}

button:hover:not(:disabled) {
  background: var(--vp-c-brand-2);
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 4px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  font-family: 'Courier New', monospace;
  margin-bottom: 12px;
}

.result-box {
  margin-top: 16px;
  padding: 16px;
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  max-height: 500px;
  overflow-y: auto;
}

.result-box pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-size: 12px;
}

.member-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.member-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: var(--vp-c-bg-soft);
  border-radius: 6px;
}

.avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-small {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.member-info {
  flex: 1;
}

.member-info strong {
  color: var(--vp-c-text-1);
}

.member-info p {
  margin: 4px 0;
  font-size: 13px;
  color: var(--vp-c-text-2);
}

.domain-stats {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.domain-stat-item {
  padding: 12px;
  background: var(--vp-c-bg-soft);
  border-radius: 6px;
}

.domain-name {
  font-weight: 600;
  color: var(--vp-c-text-1);
  margin-bottom: 4px;
}

.domain-count {
  font-size: 13px;
  color: var(--vp-c-text-2);
  margin-bottom: 8px;
}

.progress-bar {
  height: 6px;
  background: var(--vp-c-divider);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--vp-c-brand-1);
  transition: width 0.3s;
}

.leaderboard-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.leaderboard-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--vp-c-bg-soft);
  border-radius: 6px;
}

.rank {
  font-size: 20px;
  font-weight: bold;
  color: var(--vp-c-brand-1);
  min-width: 40px;
  text-align: center;
}

.error-box {
  padding: 16px;
  background: var(--vp-c-danger-soft);
  border: 1px solid var(--vp-c-danger);
  border-radius: 6px;
  color: var(--vp-c-danger-dark);
  margin-top: 20px;
}
</style>
