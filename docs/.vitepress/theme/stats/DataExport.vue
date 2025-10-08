<script setup>
import { ref, computed, onMounted } from 'vue'

const isExporting = ref(false)
const members = ref([])
const domainCount = ref({})
const loading = ref(true)

// 加载数据
const loadData = async () => {
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
        let value = item[key] || ''
        if (typeof value === 'string') {
          value = value.trim().replace(/^"|"$/g, '')
        }
        if (['domain'].includes(key)) {
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

    // 计算领域统计
    const domainCountData = {}
    parsedMembers.forEach(member => {
      member.domain.forEach(domain => {
        if (domain) {
          domainCountData[domain] = (domainCountData[domain] || 0) + 1
        }
      })
    })
    domainCount.value = domainCountData

  } catch (error) {
    console.error('DataExport数据加载失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})

// 统计数据
const stats = computed(() => {
  const totalMembers = members.value.length
  const totalDomains = Object.keys(domainCount.value).length
  const avgDomainsPerMember = totalMembers > 0 ?
    (members.value.reduce((sum, m) => sum + m.domain.length, 0) / totalMembers).toFixed(2) : 0

  const domainStats = Object.entries(domainCount.value)
    .sort((a, b) => b[1] - a[1])
    .map(([domain, count]) => ({
      domain,
      count,
      percentage: ((count / totalMembers) * 100).toFixed(1)
    }))

  return {
    totalMembers,
    totalDomains,
    avgDomainsPerMember,
    domainStats,
    mostPopularDomain: domainStats[0]?.domain || '暂无',
    leastPopularDomain: domainStats[domainStats.length - 1]?.domain || '暂无'
  }
})

// 导出为 CSV
const exportToCSV = () => {
  isExporting.value = true

  try {
    const headers = ['ID', '姓名', 'GitHub链接', '研究方向']
    const rows = [headers.join(',')]

    members.value.forEach(member => {
      const row = [
        member.id,
        `"${member.name}"`,
        `"${member.github}"`,
        `"${member.domain.join(';')}"`
      ]
      rows.push(row.join(','))
    })

    const csvContent = rows.join('\n')
    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')

    if (link.download !== undefined) {
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `members_data_${new Date().toISOString().split('T')[0]}.csv`)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  } catch (error) {
    console.error('导出失败:', error)
    alert('导出失败，请重试')
  } finally {
    isExporting.value = false
  }
}

// 导出统计报告为 JSON
const exportStatsToJSON = () => {
  isExporting.value = true

  try {
    const reportData = {
      exportDate: new Date().toISOString(),
      summary: {
        totalMembers: stats.value.totalMembers,
        totalDomains: stats.value.totalDomains,
        avgDomainsPerMember: parseFloat(stats.value.avgDomainsPerMember),
        mostPopularDomain: stats.value.mostPopularDomain,
        leastPopularDomain: stats.value.leastPopularDomain
      },
      domainStatistics: stats.value.domainStats,
      memberDetails: members.value.map(member => ({
        id: member.id,
        name: member.name,
        github: member.github,
        domains: member.domain,
        domainCount: member.domain.length
      }))
    }

    const jsonContent = JSON.stringify(reportData, null, 2)
    const blob = new Blob([jsonContent], { type: 'application/json' })
    const link = document.createElement('a')

    if (link.download !== undefined) {
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `members_report_${new Date().toISOString().split('T')[0]}.json`)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  } catch (error) {
    console.error('导出失败:', error)
    alert('导出失败，请重试')
  } finally {
    isExporting.value = false
  }
}

// 复制统计数据到剪贴板
const copyStatsToClipboard = async () => {
  try {
    const statsText = `
组织成员统计报告
生成时间: ${new Date().toLocaleString()}

基本统计:
- 总成员数: ${stats.value.totalMembers}
- 研究方向数: ${stats.value.totalDomains}
- 平均方向数/人: ${stats.value.avgDomainsPerMember}
- 最热门方向: ${stats.value.mostPopularDomain}

研究方向分布:
${stats.value.domainStats.map(item =>
      `- ${item.domain}: ${item.count}人 (${item.percentage}%)`
    ).join('\n')}
    `.trim()

    await navigator.clipboard.writeText(statsText)
    alert('统计数据已复制到剪贴板')
  } catch (error) {
    console.error('复制失败:', error)
    alert('复制失败，请手动选择文本')
  }
}
</script>

<template>
  <div class="data-export">
    <div class="export-header">
      <h3>数据导出与统计</h3>
      <p>导出成员数据和统计报告</p>
    </div>

    <!-- 快速统计 -->
    <div class="quick-stats">
      <div class="stat-grid">
        <div class="stat-item">
          <div class="stat-value">{{ stats.totalMembers }}</div>
          <div class="stat-label">总成员数</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ stats.totalDomains }}</div>
          <div class="stat-label">研究方向数</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ stats.avgDomainsPerMember }}</div>
          <div class="stat-label">平均方向数/人</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ stats.mostPopularDomain }}</div>
          <div class="stat-label">最热门方向</div>
        </div>
      </div>
    </div>

    <!-- 研究方向详细统计 -->
    <div class="domain-details">
      <h4>研究方向详细统计</h4>
      <div class="domain-list">
        <div v-for="item in stats.domainStats" :key="item.domain" class="domain-item">
          <div class="domain-name">{{ item.domain }}</div>
          <div class="domain-stats">
            <span class="count">{{ item.count }} 人</span>
            <span class="percentage">{{ item.percentage }}%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: item.percentage + '%' }"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 导出操作 -->
    <div class="export-actions">
      <h4>导出选项</h4>
      <div class="action-buttons">
        <button @click="exportToCSV" :disabled="isExporting" class="export-btn csv-btn">
          <span class="btn-icon">📊</span>
          导出 CSV 数据
        </button>

        <button @click="exportStatsToJSON" :disabled="isExporting" class="export-btn json-btn">
          <span class="btn-icon">📋</span>
          导出统计报告
        </button>

        <button @click="copyStatsToClipboard" :disabled="isExporting" class="export-btn copy-btn">
          <span class="btn-icon">📄</span>
          复制统计数据
        </button>
      </div>

      <div v-if="isExporting" class="exporting-indicator">
        正在导出数据...
      </div>
    </div>
  </div>
</template>

<style scoped>
.data-export {
  background: var(--vp-c-bg);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 10px var(--vp-shadow-1);
  border: 1px solid var(--vp-c-divider);
}

.export-header {
  margin-bottom: 24px;
  text-align: center;
}

.export-header h3 {
  margin: 0 0 8px 0;
  color: var(--vp-c-text-1);
  font-size: 1.5rem;
}

.export-header p {
  margin: 0;
  color: var(--vp-c-text-2);
  font-size: 1rem;
}

.quick-stats {
  margin-bottom: 32px;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: var(--vp-c-bg-soft);
  border-radius: 8px;
  border: 1px solid var(--vp-c-divider);
}

.stat-value {
  font-size: 1.8rem;
  font-weight: bold;
  color: var(--vp-c-brand-1);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 0.9rem;
  color: var(--vp-c-text-2);
}

.domain-details {
  margin-bottom: 32px;
}

.domain-details h4 {
  margin: 0 0 16px 0;
  color: var(--vp-c-text-1);
  font-size: 1.2rem;
}

.domain-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 300px;
  overflow-y: auto;
}

.domain-item {
  padding: 12px;
  background: var(--vp-c-bg-soft);
  border-radius: 8px;
  border: 1px solid var(--vp-c-divider);
}

.domain-name {
  font-weight: 600;
  color: var(--vp-c-text-1);
  margin-bottom: 8px;
}

.domain-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.count {
  color: var(--vp-c-brand-1);
  font-weight: 500;
}

.percentage {
  color: var(--vp-c-text-2);
  font-size: 0.9rem;
}

.progress-bar {
  height: 6px;
  background: var(--vp-c-divider);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--vp-c-brand-1), var(--vp-c-brand-2));
  transition: width 0.3s ease;
}

.export-actions h4 {
  margin: 0 0 16px 0;
  color: var(--vp-c-text-1);
  font-size: 1.2rem;
}

.action-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.export-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.export-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.csv-btn {
  background: #28a745;
  color: white;
}

.csv-btn:hover:not(:disabled) {
  background: #218838;
}

.json-btn {
  background: #17a2b8;
  color: white;
}

.json-btn:hover:not(:disabled) {
  background: #138496;
}

.copy-btn {
  background: #6c757d;
  color: white;
}

.copy-btn:hover:not(:disabled) {
  background: #5a6268;
}

.btn-icon {
  font-size: 16px;
}

.exporting-indicator {
  margin-top: 16px;
  padding: 12px;
  background: var(--vp-c-warning-soft);
  border: 1px solid var(--vp-c-warning);
  border-radius: 8px;
  color: var(--vp-c-warning-dark);
  text-align: center;
  font-weight: 500;
}

@media (max-width: 768px) {
  .action-buttons {
    flex-direction: column;
  }

  .export-btn {
    justify-content: center;
  }

  .stat-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
