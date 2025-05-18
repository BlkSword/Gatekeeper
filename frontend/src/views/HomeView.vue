<template>
  <div class="full-container">
    <!-- 状态概览 -->
    <el-row :gutter="20" class="overview">
      <el-col :span="6">
        <el-card class="status-card" style="background: #f0f9eb;"> 
          <div class="card-content">
            <i class="el-icon-success" style="color: #67c23a;"></i>
            <div class="info">
              <p>通过项</p>
              <h3 style="color: #67c23a;">85/100</h3>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="status-card" style="background: #fdf6ec;"> 
          <div class="card-content">
            <i class="el-icon-warning" style="color: #e6a23c;"></i>
            <div class="info">
              <p>警告项</p>
              <h3 style="color: #e6a23c;">10</h3>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="status-card" style="background: #fef0f0;"> 
          <div class="card-content">
            <i class="el-icon-error" style="color: #f56c6c;"></i>
            <div class="info">
              <p>失败项</p>
              <h3 style="color: #f56c6c;">5</h3>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="status-card" style="background: #f4f8fd;"> 
          <div class="card-content">
            <i class="el-icon-s-promotion" style="color: #409EFF;"></i>
            <div class="info">
              <p>待处理</p>
              <h3 style="color: #409EFF;">3</h3>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 主要内容区域 -->
    <el-row :gutter="20" class="main-content">
      <el-col :span="12">
        <el-card>
          <div slot="header">
            <span>漏洞级别占比</span>
          </div>
          <div ref="pieChart" class="chart"></div>
        </el-card>
      </el-col>
    
      <el-col :span="12">
        <el-card>
          <div slot="header">
            <span>系统资源监控</span>
          </div>
          <div ref="chart" class="chart"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 检测结果列表 -->
    <el-row :gutter="20" class="main-content">
      <el-col :span="24">
        <el-card>
          <div slot="header">
            <span>最新检测结果</span>
          </div>
          <el-table :data="recentScans" border>
            <el-table-column prop="time" label="检测时间" width="150" />
            <el-table-column prop="status" label="状态">
              <template #default="{ row }">
                <el-tag :type="row.status === 'success' ? 'success' : row.status === 'warning' ? 'warning' : 'danger'">
                  {{ row.status === 'success' ? '通过' : row.status === 'warning' ? '警告' : '失败' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="action" label="操作">
              <template #default="{ row }">
                <el-button type="text" @click="viewDetails(row)">查看详情</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 底部信息 -->
    <el-row class="footer">
      <el-col :span="24">
        <div class="safety-tips">
          <p>© 2025 Password By XiaoHei</p>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

// 模拟数据
const recentScans = ref([
  { time: '2023-09-15 14:30', status: 'success' },
  { time: '2023-09-14 09:15', status: 'warning' },
  { time: '2023-09-13 16:45', status: 'danger' },
  { time: '2023-09-12 11:20', status: 'success' },
  { time: '2023-09-11 15:50', status: 'warning' }
])

const chart = ref(null)
const pieChart = ref(null)


onMounted(() => {
  const lineChart = echarts.init(chart.value)
  const lineOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    legend: { data: ['CPU使用率', '内存使用', '磁盘占用'] },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: ['08:00', '10:00', '12:00', '14:00', '16:00', '18:00'] },
    yAxis: { type: 'value' },
    series: [
      { name: 'CPU使用率', type: 'line', data: [12, 15, 8, 10, 18, 20] },
      { name: '内存使用', type: 'line', data: [20, 32, 18, 34, 50, 30] },
      { name: '磁盘占用', type: 'line', data: [15, 25, 10, 20, 35, 25] }
    ]
  }
  lineChart.setOption(lineOption)
})

onMounted(() => {
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
          { value: 5, name: '高危' },
          { value: 10, name: '中危' },
          { value: 20, name: '低危' }
        ],
        emphasis: {
          itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.5)' }
        }
      }
    ]
  }
  pieInstance.setOption(pieOption)
})

// 操作方法（未修改部分保持不变）
const handleScan = () => {
  ElMessage.success('开始执行基线检测...')
  // 实际检测逻辑
}

const showReport = () => {
  ElMessageBox.alert('报告生成功能开发中...', '提示', { type: 'info' })
}

const viewDetails = (row) => {
  ElMessageBox.alert(`检测时间：${row.time}\n状态：${row.status}`, '检测详情', { type: 'info' })
}
</script>

<style scoped>
.full-container {
  height: 100vh;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.overview {
  margin-bottom: 20px;
}

.status-card {
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.card-content .info p { margin: 0; color: #000000; margin-bottom: 20px;}
.card-content h3 { margin: 0; font-size: 30px; }

.main-content {
  display: flex;
  flex-wrap: nowrap;
  gap: 6px;
}

.chart {
  height: 350px;
}

.footer {
  margin-top: 20px;
}

.safety-tips {
  background: #fff;
  padding: 15px;
  border-radius: 4px;
  text-align: center; 
}
</style>