<template>
  <div class="full-container">
    <!-- 系统状态概览 -->
    <el-row :gutter="20">
      <el-col v-for="(metric, index) in systemMetrics" :key="index" :span="6">
        <el-card class="status-card">
          <div class="metric-item">
            <h4>{{ metric.label }}</h4>
            <el-progress 
              type="circle" 
              :percentage="metric.value" 
              :color="metric.color" 
              :stroke-width="16"
              :width="120"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 网卡流量监控 -->
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <div slot="header" class="card-header">
            <span>实时网卡流量监控</span>
          </div>
          <div ref="networkChart" class="chart"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <div slot="header" class="card-header">
            <span>网络连接状态</span>
          </div>
          <div class="network-info">
            <el-table :data="networkInterfaces" border>
              <el-table-column prop="interface" label="接口" />
              <el-table-column prop="ip" label="IP地址" />
              <el-table-column prop="mask" label="子网掩码" />
              <el-table-column prop="gateway" label="网关" />
              <el-table-column prop="status" label="状态">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'connected' ? 'success' : 'danger'">
                    {{ row.status === 'connected' ? '已连接' : '断开' }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 进程信息 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <div slot="header" class="card-header">
            <span>运行进程信息</span>
          </div>
          <el-table :data="processes" border>
            <el-table-column prop="name" label="进程名称" />
            <el-table-column prop="pid" label="PID" />
            <el-table-column prop="cpu" label="CPU%" />
            <el-table-column prop="memory" label="内存%" />
            <el-table-column prop="path" label="路径" />
            <el-table-column prop="user" label="启动用户" />
            <el-table-column prop="permission" label="权限等级">
              <template #default="{ row }">
                <el-tag :type="row.permission === '管理员' ? 'danger' : 'primary'">
                  {{ row.permission }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 服务与网络信息 -->
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <div slot="header" class="card-header">
            <span>服务状态</span>
          </div>
          <el-table :data="services" border>
            <el-table-column prop="name" label="服务名称" />
            <el-table-column prop="status" label="状态">
              <template #default="{ row }">
                <el-tag :type="row.status === 'running' ? 'success' : 'warning'">
                  {{ row.status === 'running' ? '运行中' : '已停止' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="pid" label="PID" />
            <el-table-column prop="path" label="执行路径" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="full-height-card">
          <div slot="header" class="card-header">
            <span>防火墙规则</span>
          </div>
          <el-table :data="firewallRules" border>
            <el-table-column prop="ruleName" label="规则名称" />
            <el-table-column prop="protocol" label="协议" />
            <el-table-column prop="direction" label="方向" />
            <el-table-column prop="action" label="操作" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 安装程序与网络数据 -->
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <div slot="header" class="card-header">
            <span>已安装程序</span>
          </div>
          <el-table :data="installedApps" border>
            <el-table-column prop="name" label="程序名称" />
            <el-table-column prop="version" label="版本" />
            <el-table-column prop="installDate" label="安装日期" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <div slot="header" class="card-header">
            <span>网络数据统计</span>
          </div>
          <div class="network-stats">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="发送数据量">{{ networkStats.sent }} MB</el-descriptions-item>
              <el-descriptions-item label="接收数据量">{{ networkStats.received }} MB</el-descriptions-item>
              <el-descriptions-item label="开放端口">
                <el-tag v-for="port in openPorts" :key="port" type="info">{{ port }}</el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 底部信息 -->
    <el-row>
      <el-col :span="24">
        <div class="safety-tips">
          <p>© 2025 System Monitor By XiaoHei</p>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'

// 系统状态指标
const systemMetrics = ref([
  {
    label: '系统负载',
    target: 75,    // 目标值
    value: 0,      // 初始值设为0
    color: '#67c23a'
  },
  {
    label: 'CPU使用率',
    target: 65,
    value: 0,
    color: '#f56c6c'
  },
  {
    label: '内存使用率',
    target: 72,
    value: 0,
    color: '#e69c17'
  },
  {
    label: '磁盘使用率',
    target: 88,
    value: 0,
    color: '#409eff'
  }
])

// 网络接口信息
const networkInterfaces = ref([
  { interface: 'eth0', ip: '192.168.1.100', mask: '255.255.255.0', gateway: '192.168.1.1', status: 'connected' },
  { interface: 'lo', ip: '127.0.0.1', mask: '255.0.0.0', gateway: '-', status: 'connected' }
])

// 网络数据统计
const networkStats = ref({
  sent: 123456, // 发送数据量（MB）
  received: 654321 // 接收数据量（MB）
})

// 开放端口
const openPorts = ref(['22', '80', '443', '3389'])

// 进程信息
const processes = ref([
  { name: 'System Idle Process', pid: '0', cpu: '0.5', memory: '0.1', path: 'System', user: 'SYSTEM', permission: '管理员' },
  { name: 'chrome.exe', pid: '1234', cpu: '15.2', memory: '25.3', path: 'C:\\Program Files\\Google\\Chrome', user: 'XiaoHei', permission: '用户' }
])

// 服务信息
const services = ref([
  { name: 'Windows Update', status: 'running', pid: '456', path: 'C:\\Windows\\system32\\svchost.exe' },
  { name: 'Print Spooler', status: 'stopped', pid: '-', path: '-' }
])

// 防火墙规则
const firewallRules = ref([
  { ruleName: 'Allow HTTP', protocol: 'TCP', direction: 'Inbound', action: 'Allow' },
  { ruleName: 'Block FTP', protocol: 'FTP', direction: 'Outbound', action: 'Block' }
])

// 已安装程序
const installedApps = ref([
  { name: 'Google Chrome', version: '120.0.6099.71', installDate: '2023-05-15' },
  { name: 'Visual Studio Code', version: '1.75.1', installDate: '2023-04-01' }
])

// 网络流量监控图表
const networkChart = ref(null)
let chartInstance = null
let intervalId = null

// 模拟网络流量数据
const trafficData = {
  times: ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00'],
  sent: [120, 180, 220, 150, 230, 210, 260],
  received: [80, 120, 100, 140, 90, 110, 130]
}

function updateNetworkChart() {
  if (!chartInstance) return
  
  // 时间点
  const now = new Date()
  const timeStr = `${now.getHours()}:${String(now.getMinutes()).padStart(2, '0')}`
  trafficData.times.push(timeStr)
  
  if (trafficData.times.length > 10) {
    trafficData.times.shift()
    trafficData.sent.shift()
    trafficData.received.shift()
  }
  
  // 模拟新数据
  trafficData.sent.push(Math.floor(Math.random() * 300))
  trafficData.received.push(Math.floor(Math.random() * 300))
  
  chartInstance.setOption({
    xAxis: { data: trafficData.times },
    series: [
      { data: trafficData.sent },
      { data: trafficData.received }
    ]
  })
}

// 动画逻辑
const animationTimers = ref([])

onMounted(() => {
  // 系统指标动画
  systemMetrics.value.forEach((metric, index) => {
    const duration = 2000 
    const startTime = Date.now()
    
    const animate = () => {
      const progress = Math.min(1, (Date.now() - startTime) / duration)
      metric.value = Math.floor(progress * metric.target)
      
      if (progress < 1) {
        animationTimers.value[index] = requestAnimationFrame(animate)
      }
    }
    
    animationTimers.value[index] = requestAnimationFrame(animate)
  })
  
  // 初始化网络流量图表
  chartInstance = echarts.init(networkChart.value)
  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['发送数据', '接收数据'] },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: trafficData.times },
    yAxis: { type: 'value', name: 'MB/s' },
    series: [
      { 
        name: '发送数据', 
        type: 'line', 
        data: trafficData.sent,
        smooth: true
      },
      { 
        name: '接收数据', 
        type: 'line', 
        data: trafficData.received,
        smooth: true
      }
    ]
  }
  chartInstance.setOption(option)
  
  // 启动数据更新
  intervalId = setInterval(updateNetworkChart, 5000)
})

onBeforeUnmount(() => {
  if (intervalId) clearInterval(intervalId)
})
</script>

<style scoped src="../../assets/css/Home_Host.css"></style>