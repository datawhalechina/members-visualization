<script setup>
import { ref } from 'vue';
import ProjectBaseChart from './ProjectBaseChart.vue';

const extraConfg = ref({
    grid: {
        left: 0,
        right: 100,
        bottom: 30,
        top: 100,
        containLabel: true
    },
})

const loadChartData = async () => {
    const basePath = import.meta.env.BASE_URL || '/'
    const commitsPath = `${basePath}data/datawhalechina/organization_datasource.json`.replace(/\/+/g, '/')
    const response = await fetch(commitsPath)
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
    }
    const responseJSON = await response.json()
    return responseJSON.newProjectAddTop3Info
}
</script>

<template>
    <ProjectBaseChart :extra-config="extraConfg" :load-chart-data="loadChartData" />
</template>
