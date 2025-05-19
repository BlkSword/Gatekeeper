<template>
  <div class="full-container">
    <!-- 系统状态概览 -->
    <el-row :gutter="20" class="overview">
      <!-- 系统启动时间 -->
      <el-col :span="12">
        <el-card class="status-card">
          <div class="metric-item">
            <h4>系统启动时间</h4>
            <p>{{ systemInfo.bootTime }}</p>
          </div>
        </el-card>
      </el-col>
      <!-- 当前时间 -->
      <el-col :span="12">
        <el-card class="status-card">
          <div class="metric-item">
            <h4>当前时间</h4>
            <p>{{ currentTime }}</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 系统资源监控 -->
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <div slot="header" class="card-header">
            <span>实时资源监控</span>
          </div>
          <div ref="realTimeChart" class="chart"></div>
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
    <el-row class="footer">
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

// 系统状态数据
const systemInfo = ref({
  bootTime: '2025-03-20 08:00:00'
})

// 网络接口信息
const networkInterfaces = ref([
  { interface: 'eth0', ip: '192.168.1.100', mask: '255.255.255.0', gateway: '192.168.1.1', status: 'connected' },
  { interface: 'lo', ip: '127.0.0.1', mask: '255.0.0.0', gateway: '-', status: 'connected' }
])

// 进程信息
const processes = ref([
  { name: 'System Idle Process', pid: 0, cpu: 1.2, memory: 0.5, path: 'C:\\Windows\\System32', user: 'SYSTEM', permission: '管理员' },
  { name: 'explorer.exe', pid: 1234, cpu: 5.3, memory: 15.2, path: 'C:\\Windows\\Explorer.EXE', user: 'Administrator', permission: '管理员' },
  { name: 'chrome.exe', pid: 5678, cpu: 12.7, memory: 30.4, path: 'C:\\Program Files\\Google\\Chrome', user: 'User', permission: '标准用户' }
])

// 服务状态信息
const services = ref([
  { name: 'Windows Update', status: 'running', pid: 456, path: 'C:\\Windows\\System32\\svchost.exe' },
  { name: 'Print Spooler', status: 'stopped', pid: '-', path: 'C:\\Windows\\System32\\spoolsv.exe' }
])

// 防火墙规则
const firewallRules = ref([
  { ruleName: '允许HTTP', protocol: 'TCP', direction: 'Inbound', action: 'Allow' },
  { ruleName: '阻止SSH', protocol: 'TCP', direction: 'Outbound', action: 'Block' }
])

// 已安装程序
const installedApps = ref([
  { name: 'Google Chrome', version: '120.0.0.0', installDate: '2025-01-15' },
  { name: 'Notepad++', version: '8.5.1', installDate: '2025-02-01' }
])

// 网络数据统计
const networkStats = ref({
  sent: 1250,
  received: 3420
})
const openPorts = ref(['80', '443', '3389', '8080'])

// 实时资源监控图表
const realTimeChart = ref(null)

// 当前时间数据
const currentTime = ref(formatTime(new Date()))

// 定时更新时间
let timeInterval = null

function formatTime(date) {
  return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}:${String(date.getSeconds()).padStart(2, '0')}`
}

onMounted(() => {
  const chartInstance = echarts.init(realTimeChart.value)
  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['CPU', '内存', '磁盘'] },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: ['08:00', '10:00', '12:00', '14:00', '16:00', '18:00'] },
    yAxis: { type: 'value' },
    series: [
      { name: 'CPU', type: 'line', data: [15, 22, 18, 25, 30, 28] },
      { name: '内存', type: 'line', data: [45, 55, 60, 65, 70, 68] },
      { name: '磁盘', type: 'line', data: [30, 35, 40, 45, 50, 48] }
    ]
  }
  chartInstance.setOption(option)

  timeInterval = setInterval(() => {
    currentTime.value = formatTime(new Date())
  }, 1000)
})

onBeforeUnmount(() => {
  if (timeInterval) clearInterval(timeInterval)
})
</script>

<style scoped>
.full-container {
  height: 100vh;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.full-height-card {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.overview {
  margin-bottom: 20px;
}

.status-card {
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.metric-item {
  text-align: center;
}

/* 卡片标题样式 */
.card-header {
  text-align: left;
  margin-bottom: 20px;
}

.network-info {
  height: 350px;
  overflow-y: auto;
}

.network-stats {
  height: 100%;
  display: flex;
  align-items: center;
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