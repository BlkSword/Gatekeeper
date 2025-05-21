<template>
  <div class="full-container">
    <!-- 状态概览 -->
    <el-row :gutter="20">
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
          <div slot="header" style="text-align: left;">
            <span>告警级别占比</span>
          </div>
          <div ref="pieChart" class="chart"></div>
        </el-card>
      </el-col>
    
      <el-col :span="12">
        <el-card>
          <div slot="header" class="main-content">
            <span>动态基线状态</span>
          </div>
          <div ref="chart" class="chart"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 检测结果列表 -->
    <el-row :gutter="20" class="main-content">
      <el-col :span="24">
        <el-card>
          <div slot="header" class="card-header">
            <span>安全动态</span>
            <el-button type="text" style="float: right; padding: 3px 0" @click="openDrawer">更多</el-button>
          </div>
          <el-table :data="limitedRecentScans" border>
            <el-table-column prop="name" label="检测名称" />
            <el-table-column prop="category" label="检测类别">
              <template #default="{ row }">
                <span>{{ row.category }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="level" label="等级">
              <template #default="{ row }">
                <el-tag :type="row.level === '高危' ? 'danger' : row.level === '中危' ? 'warning' : 'primary'">
                  {{ row.level }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="time" label="检测时间" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 抽屉组件 -->
    <el-drawer
      v-model="drawerVisible"
      title="全部检测结果"
      direction="rtl"
      size="60%"
    >
      <el-table :data="paginatedData" border style="margin: 0 20px">
        <el-table-column prop="name" label="检测名称" />
        <el-table-column prop="category" label="检测类别">
          <template #default="{ row }">
            <span>{{ row.category }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="level" label="等级">
          <template #default="{ row }">
            <el-tag :type="row.level === '高危' ? 'danger' : row.level === '中危' ? 'warning' : 'primary'">
              {{ row.level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="time" label="检测时间" />
      </el-table>
      
      <el-pagination
        layout="prev, pager, next"
        :total="recentScans.length"
        :page-size="pagination.pageSize"
        :current-page="pagination.currentPage"
        @current-change="handlePageChange"
        style="text-align: center; margin-top: 20px"
      />
    </el-drawer>

    <!-- 底部信息 -->
    <el-row>
      <el-col :span="24">
        <div class="safety-tips">
          <p>© 2025 Password By XiaoHei</p>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import * as echarts from 'echarts'
import { ElMessageBox } from 'element-plus'

// 模拟数据
const recentScans = ref([
  { name: '检测事件1', category: '静态规则', level: '高危', time: '2023-09-15 14:30' },
  { name: '动态检测2', category: '动态基线', level: '中危', time: '2023-09-14 09:15' },
  { name: '安全扫描3', category: '静态规则', level: '低危', time: '2023-09-13 16:45' },
  { name: '合规检查4', category: '动态基线', level: '低危', time: '2023-09-12 11:20' },
  { name: '漏洞扫描5', category: '静态规则', level: '中危', time: '2023-09-11 15:50' },
  { name: '配置审计6', category: '静态规则', level: '高危', time: '2023-09-10 10:00' },
  { name: '权限检测7', category: '动态基线', level: '低危', time: '2023-09-09 14:30' },
  { name: '日志分析8', category: '动态基线', level: '中危', time: '2023-09-08 16:45' }
])

// 计算属性
const limitedRecentScans = computed(() => {
  return recentScans.value.slice(0, 3)
})

// 分页相关状态
const drawerVisible = ref(false)
const pagination = ref({
  currentPage: 1,
  pageSize: 10
})

// 分页数据计算
const paginatedData = computed(() => {
  const start = (pagination.value.currentPage - 1) * pagination.value.pageSize
  const end = start + pagination.value.pageSize
  return recentScans.value.slice(start, end)
})

// 分页事件处理
const handlePageChange = (page) => {
  pagination.value.currentPage = page
}

// 打开抽屉方法
const openDrawer = () => {
  drawerVisible.value = true
  // 重置到第一页
  pagination.value.currentPage = 1
}

// 操作方法
const viewDetails = (row) => {
  ElMessageBox.alert(
    `检测名称：${row.name}\n检测类别：${row.category}\n等级：${row.level}\n检测时间：${row.time}`, 
    '检测详情', 
    { type: 'info' }
  )
}

// 图表初始化逻辑
const chart = ref(null)
const pieChart = ref(null)

onMounted(() => {
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

  // 初始化动态基线状态折线图
  const baselineChart = echarts.init(chart.value)
  const baselineOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    legend: { data: ['通过项', '警告项', '失败项'] },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { 
      type: 'category', 
      data: ['2023-09-15', '2023-09-14', '2023-09-13', '2023-09-12', '2023-09-11'] 
    },
    yAxis: { 
      type: 'value',
      name: '数量'
    },
    series: [
      { 
        name: '通过项', 
        type: 'line', 
        data: [85, 80, 78, 82, 83],
        itemStyle: { color: '#67c23a' }
      },
      { 
        name: '警告项', 
        type: 'line', 
        data: [10, 12, 15, 10, 11],
        itemStyle: { color: '#e6a23c' }
      },
      { 
        name: '失败项', 
        type: 'line', 
        data: [5, 8, 7, 8, 6],
        itemStyle: { color: '#f56c6c' }
      }
    ]
  }
  baselineChart.setOption(baselineOption)
})
</script>

<style scoped src="../../assets/css/Home_Baseline.css"></style>