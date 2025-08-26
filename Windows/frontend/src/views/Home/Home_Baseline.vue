<template>
  <div class="full-container">
    <!-- 状态概览 -->
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="status-card">
          <div class="card-content">
            <i class="el-icon-success" style="color: #409EFF;"></i>
            <div class="info">
              <p>总检查项</p>
              <h3 style="color: #409EFF;">{{ total }}</h3>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="status-card">
          <div class="card-content">
            <i class="el-icon-warning" style="color: #67c23a;"></i>
            <div class="info">
              <p>通过</p>
              <h3 style="color: #67c23a;">{{ compliant }}</h3>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="status-card">
          <div class="card-content">
            <i class="el-icon-error" style="color: #e6a23c;"></i>
            <div class="info">
              <p>警告</p>
              <h3 style="color: #e6a23c;">{{ warning }}</h3>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="status-card">
          <div class="card-content">
            <i class="el-icon-s-promotion" style="color: #f56c6c;"></i>
            <div class="info">
              <p>失败</p>
              <h3 style="color: #f56c6c;">{{ failed }}</h3>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 主要内容区域 -->
    <el-row :gutter="20" class="main-content">
      <el-col :span="12">
        <el-card>
          <div slot="header" style="text-align: left;">
            <span>告警级别占比</span>
          </div>
          <div ref="pieChart" class="chart"></div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <div slot="header" class="main-content"
            style="display: flex; justify-content: space-between; align-items: center;">
            <span>动态基线状态</span>
            <div>
              <el-select v-model="selectedBaseline" placeholder="选择基线" size="small" @change="handleBaselineChange">
                <el-option v-for="baseline in baselineOptions" :key="baseline.metric_name" :label="baseline.metric_name"
                  :value="baseline.metric_name" />
              </el-select>
            </div>
          </div>
          <div ref="lineChart" class="chart"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 检测记录列表 -->
    <el-row :gutter="20" class="main-content">
      <el-col :span="24">
        <el-card>
          <div slot="header" class="card-header">
            <span>最近检测记录</span>
          </div>
          <el-table :data="recentScans.slice(0, 3)" border style="width: 100%">
            <el-table-column prop="id" label="检测ID" width="400" />
            <el-table-column prop="total" label="总项数" />
            <el-table-column prop="compliant" label="合规数" />
            <el-table-column prop="time" label="检测时间" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

// 状态概览数据
const total = ref(0)
const compliant = ref(0)
const warning = ref(0)
const failed = ref(0)

// 图表引用
const pieChart = ref(null)
const lineChart = ref(null)

// 检测记录数据
const recentScans = ref([])

// 定时器和图表实例
const baselineTimer = ref(null)
const baselineChart = ref(null)

// 基线选择相关数据
const selectedBaseline = ref('cpu_usage')
const baselineOptions = ref([])

// 时间格式化函数
function formatTime(isoString) {
  const date = new Date(isoString)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}`
}

// 获取基线配置列表
async function fetchBaselineConfigs() {
  try {
    const res = await fetch('http://127.0.0.1:8000/baseline/configs')
    if (!res.ok) throw new Error('获取基线配置失败')
    const data = await res.json()
    baselineOptions.value = data.data || []
  } catch (error) {
    console.error('获取基线配置异常:', error)
  }
}

// 处理基线选择变化
async function handleBaselineChange(metricName) {
  await fetchBaselineData(metricName)
}

// 获取基线数据并更新图表
async function fetchBaselineData(metricName) {
  try {
    // 获取基线数据
    const baselineRes = await fetch(`http://localhost:8000/baseline/latest/${metricName}`)
    if (!baselineRes.ok) throw new Error(`获取${metricName}基线数据失败`)
    const baselineData = await baselineRes.json()

    // 处理基线数据
    const processedData = baselineData.data.map(item => ({
      timestamp: formatTime(item.timestamp),
      actual: parseFloat(item.value.toFixed(1)),
      baseline: parseFloat(item.baseline.toFixed(1))
    }))

    // 提取日期数组和数值数组
    const dates = processedData.map(item => item.timestamp)
    const actualValues = processedData.map(item => item.actual)
    const baselineValues = processedData.map(item => item.baseline)

    // 如果图表实例不存在则创建
    if (!baselineChart.value && lineChart.value) {
      baselineChart.value = echarts.init(lineChart.value)
    }

    // 创建图表配置
    const baselineOption = {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'line' },
        formatter: (params) => {
          return `${params[0].axisValue}<br/>` +
            `实际值: ${params[0].value}<br/>` +
            `基线值: ${params[1].value}`
        }
      },
      legend: {
        data: ['实际值', '基线值'],
        top: 20
      },
      grid: {
        left: '8%',
        right: '8%',
        bottom: '10%',
        top: '25%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        name: '时间',
        data: dates
      },
      yAxis: {
        type: 'value',
        name: metricName === 'cpu_usage' ? 'CPU使用率 (%)' :
          metricName === 'memory_usage' ? '内存使用率 (%)' :
            '使用率 (%)'
      },
      series: [
        {
          name: '实际值',
          type: 'line',
          data: actualValues,
          itemStyle: { color: '#67c23a' },
          lineStyle: { width: 2 },
          showSymbol: true,
          symbolSize: 6
        },
        {
          name: '基线值',
          type: 'line',
          data: baselineValues,
          itemStyle: { color: '#409EFF' },
          lineStyle: { width: 2, type: 'dashed' },
          showSymbol: true,
          symbolSize: 6
        }
      ],
    }

    // 更新图表
    baselineChart.value.setOption(baselineOption, true)

  } catch (error) {
    console.error(`${metricName}基线数据获取异常:`, error)
  }
}

onMounted(async () => {
  try {
    // 获取最近任务ID和状态概览数据
    const lastRes = await fetch('http://127.0.0.1:8000/last')
    if (!lastRes.ok) throw new Error('获取任务ID失败')
    const lastData = await lastRes.json()
    const taskId = lastData.task_id

    // 获取进度数据
    const progressRes = await fetch(`http://127.0.0.1:8000/scan/${taskId}/progress`)
    if (!progressRes.ok) throw new Error('获取进度数据失败')
    const progressData = await progressRes.json()

    // 更新状态概览数据
    total.value = progressData.total || 0
    compliant.value = progressData.compliant_count || 0
    warning.value = progressData.non_compliant_count || 0
    failed.value = total.value - compliant.value - warning.value

    // 获取非合规规则数据
    const nonCompliantRes = await fetch(`http://127.0.0.1:8000/non-compliant-rules?task_id=${taskId}`)
    if (!nonCompliantRes.ok) throw new Error('获取非合规规则失败')
    const nonCompliantData = await nonCompliantRes.json()

    // 提取风险统计数据
    const highRisk = nonCompliantData.statistics.high_risk.count || 0
    const mediumRisk = nonCompliantData.statistics.medium_risk.count || 0
    const lowRisk = nonCompliantData.statistics.low_risk.count || 0

    // 初始化漏洞级别占比饼图
    const pieInstance = echarts.init(pieChart.value)
    const pieOption = {
      tooltip: { trigger: 'item' },
      legend: { orient: 'vertical', right: 10 },
      series: [
        {
          type: 'pie',
          radius: '70%',
          center: ['50%', '50%'],
          data: [
            { value: highRisk, name: '高危' },
            { value: mediumRisk, name: '中危' },
            { value: lowRisk, name: '低危' }
          ],
          emphasis: {
            itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.5)' }
          }
        }
      ]
    }
    pieInstance.setOption(pieOption)

    // 获取基线配置
    await fetchBaselineConfigs()

    // 首次获取基线数据
    await fetchBaselineData(selectedBaseline.value)

    // 设置定时器（每60秒执行一次）
    baselineTimer.value = setInterval(() => {
      fetchBaselineData(selectedBaseline.value)
    }, 10000)

    // 获取最近三个任务数据
    const lastThreeRes = await fetch('http://127.0.0.1:8000/last-three')
    if (!lastThreeRes.ok) throw new Error('获取最近任务失败')
    const lastThreeTasks = await lastThreeRes.json()

    // 处理每个任务以获取合规数据
    const scanRecords = []
    for (const task of lastThreeTasks) {
      // 获取任务进度
      const progressRes = await fetch(`http://127.0.0.1:8000/scan/${task.task_id}/progress`)
      if (!progressRes.ok) continue
      const progressData = await progressRes.json()

      scanRecords.push({
        id: task.task_id,
        total: progressData.total || 0,
        compliant: progressData.compliant_count || 0,
        time: formatTime(task.created_at)
      })
    }

    // 更新检测记录
    recentScans.value = scanRecords

  } catch (error) {
    console.error('数据获取异常:', error)
  }
})

// 组件卸载时的清理工作
onUnmounted(() => {
  // 清除定时器
  if (baselineTimer.value) {
    clearInterval(baselineTimer.value)
    baselineTimer.value = null
  }

  // 销毁图表实例
  if (baselineChart.value) {
    baselineChart.value.dispose()
    baselineChart.value = null
  }
})
</script>

<style scoped src="../../assets/css/Home_Baseline.css"></style>