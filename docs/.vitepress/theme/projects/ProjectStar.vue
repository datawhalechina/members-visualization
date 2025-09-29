<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

const chartRef = ref(null);
const loading = ref(false)
const error = ref(null)

const loadChartData = async () => {
    const basePath = import.meta.env.BASE_URL || '/'
    const commitsPath = `${basePath}data/datawhalechina/organization_datasource.json`.replace(/\/+/g, '/')
    const response = await fetch(commitsPath)
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
    }
    const source = await response.json()
    return source.projectInfo
}

const generateSeriesList = async () => {
    const seriesList = [];
    const source = await loadChartData()
    source.forEach((item) => {
        const data = Object.keys(item.monthly_total_stars).map((month) => item.monthly_total_stars[month] || 0);
        if (data.some((value, index) => index > 0 && value === 0 && data[index - 1] !== 0)) {
            return
        }
        seriesList.push({
            name: item.name,
            type: 'line',
            smooth: true,
            endLabel: {
                show: true,
                formatter: (params) => {
                    const name = params.seriesName;
                    return name.length > 10 ? name.substring(0, 10) + '...' : name;
                },
                distance: 20,
            },
            data: data,
            source: item
        });
    });
    return { seriesList, source };
};

onMounted(async () => {
    try {
        loading.value = true
        error.value = null
        const { seriesList, source } = await generateSeriesList()
        const myChart = echarts.init(chartRef.value);
        const option = {
            tooltip: {
                trigger: 'item'
            },
            dataZoom: [
                {
                    type: 'slider',
                    show: true,
                    yAxisIndex: [0],
                    start: 0,
                    end: 100
                }
            ],
            legend: {
                type: 'scroll',
                orient: 'horizontal',
                data: source.map((item) => item.name),
                left: 0,
                top: 30,
            },
            grid: {
                left: 0,
                right: 150,
                bottom: 30,
                top: 100,
                containLabel: true
            },
            toolbox: {
                feature: {
                    saveAsImage: {}
                }
            },
            xAxis: {
                type: 'category',
                boundaryGap: false,
                data: Object.keys(source[0].monthly_total_stars)
            },
            yAxis: {
                type: 'value',
            },
            series: seriesList
        };
        option && myChart.setOption(option);
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

        <div ref="chartRef" class="chart"></div>
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
.error {
    text-align: center;
    padding: 60px;
    font-size: 18px;
    border-radius: 12px;
    margin: 20px 0;
}

.error {
    color: #e74c3c;
    background: #fdf2f2;
    border: 1px solid #fecaca;
}

.loading {
    color: #3498db;
    background: #f0f9ff;
    border: 1px solid #bae6fd;
}
</style>
