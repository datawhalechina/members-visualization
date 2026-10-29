<script setup>
import { ref, onMounted } from 'vue'
import OrganizationTable from './OrganizationTable.vue'

const organizationData = ref([]);
const loading = ref(true)
const error = ref(null)

const loadData = async () => {
    const basePath = import.meta.env.BASE_URL || '/'
    const commitsPath = `${basePath}data/datawhalechina/organization_datasource.json`.replace(/\/+/g, '/')
    const response = await fetch(commitsPath)
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
    }
    const source = await response.json()
    return Array.isArray(source.top10KnowledgeSharingOrganizationInfo) ? source.top10KnowledgeSharingOrganizationInfo : []
}

onMounted(async () => {
    try {
        loading.value = true
        error.value = null
        organizationData.value = await loadData()
    } catch (err) {
        error.value = err.message
    } finally {
        loading.value = false
    }
})
</script>

<template>
    <div class="wrapper">
        <div v-if="loading" class="loading">
            <p>正在加载数据...</p>
        </div>

        <div v-else-if="error" class="error">
            <p>加载数据时出错: {{ error }}</p>
        </div>

        <OrganizationTable v-else-if="organizationData.length" :organization-data="organizationData" />
        <p v-else class="empty-state">暂无组织对比数据，请稍后再试。</p>
    </div>
</template>

<style scoped>
.wrapper {
    width: 100%;
    padding: 20px 0;
}

.chart {
    width: 100%;
    height: 600px;
}

.loading,
.error,
.empty-state {
    text-align: center;
    padding: 60px;
    font-size: 18px;
    border-radius: 12px;
    margin: 20px 0;
}

.error {
    color: var(--vp-c-danger-1);
    background: var(--vp-c-danger-soft);
    border: 1px solid var(--vp-c-divider);
}

.loading {
    color: var(--vp-c-text-2);
    background: var(--vp-c-bg-soft);
    border: 1px solid var(--vp-c-divider);
}
</style>
