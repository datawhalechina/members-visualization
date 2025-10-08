<script setup>
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
    extraConfig: {
        type: Object,
        required: true,
    },
    loadChartData: {
        type: Function,
        required: true,
    },
})

let chartInstance = null;
const chartRef = ref(null)
const chartDataSource = ref(null)
const loading = ref(false)
const error = ref(null)
const isDark = ref(false)

const checkDarkMode = () => {
    if (typeof window !== 'undefined') {
        isDark.value = document.documentElement.classList.contains('dark')
    }
}

const getEChartsTheme = () => {
    return isDark.value ? 'dark' : 'light'
}


const generateSeriesList = async (dataSource) => {
    const seriesList = [];
    dataSource.forEach((item) => {
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
    return { seriesList };
};

const getChartOption = async (dataSource) => {
    const { seriesList } = await generateSeriesList(dataSource)
    const option = {
        tooltip: {
            trigger: 'item'
        },
        legend: {
            type: 'scroll',
            orient: 'horizontal',
            data: dataSource.map((item) => item.name),
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
            data: Object.keys(dataSource[0].monthly_total_stars)
        },
        yAxis: {
            type: 'value',
        },
        series: seriesList,
        ...props.extraConfig,
    };
    return option
}

const initChart = async () => {
    try {
        loading.value = true
        error.value = null
        chartDataSource.value = await props.loadChartData()
        const chartOption = await getChartOption(chartDataSource.value)
        chartInstance = echarts.init(chartRef.value, getEChartsTheme())
        chartInstance.setOption(chartOption)
    } catch (err) {
        error.value = err.message
    } finally {
        loading.value = false
    }
}

const refreshChart = async (theme) => {
    chartInstance.dispose()
    const chartOption = await getChartOption(chartDataSource.value)
    chartInstance = echarts.init(chartRef.value, getEChartsTheme())
    chartInstance.setOption(chartOption)
}

// 监听主题变化
const observeThemeChange = () => {
    if (typeof window !== 'undefined') {
        const observer = new MutationObserver(() => {
            const newIsDark = document.documentElement.classList.contains('dark')
            if (newIsDark !== isDark.value) {
                isDark.value = newIsDark
                refreshChart()
            }
        })
        observer.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ['class']
        })
    }
}

onMounted(async () => {
    checkDarkMode()
    observeThemeChange()

    await nextTick()
    await initChart()
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
