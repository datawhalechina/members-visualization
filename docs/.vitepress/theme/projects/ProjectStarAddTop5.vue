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
</script>

<template>
    <ProjectBaseChart type="projectAddTop5Info" :extra-config="extraConfg" />
</template>
