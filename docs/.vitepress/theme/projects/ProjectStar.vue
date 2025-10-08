<script setup>
import { ref } from 'vue';
import ProjectBaseChart from './ProjectBaseChart.vue';

const extraConfg = ref({
    dataZoom: [
        {
            type: 'slider',
            show: true,
            yAxisIndex: [0],
            start: 0,
            end: 100
        }
    ],
    grid: {
        left: 0,
        right: 150,
        bottom: 30,
        top: 100,
        containLabel: true
    },
})
</script>

<template>
    <ProjectBaseChart type="projectInfo" :extra-config="extraConfg" />
</template>
