<template>
  <div class="full-container">
    <!-- 系统状态概览 -->
    <el-row :gutter="20">
      <el-col v-for="(metric, index) in systemMetrics" :key="index" :span="6">
        <el-card class="status-card">
          <div class="metric-item">
            <h4>{{ metric.label }}</h4>
            <el-progress type="circle" :percentage="Math.round(metric.value)" :color="metric.color" :stroke-width="16"
              :width="120" />
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
            <span>网络接口信息</span>
            <el-button type="text" style="float: right; padding: 3px 0" @click="openDrawer('network')">更多</el-button>
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

    <!-- 网络进程信息 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <div slot="header" class="card-header">
            <span>进程信息</span>
            <el-button type="text" style="float: right; padding: 3px 0" @click="openDrawer('process')">更多</el-button>
          </div>
          <el-table :data="processesSlice" border>
            <!-- PID列 -->
            <el-table-column prop="pid" label="PID" />
            <el-table-column prop="name" label="进程名称" />
            <el-table-column prop="status" label="运行状态">
              <template #default="{ row }">
                <el-tag :type="row.status === 'running' ? 'success' : 'danger'">
                  {{ row.status === 'running' ? '运行中' : '已停止' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="cpu" label="CPU%" />
            <el-table-column prop="memory" label="内存(MB)" />
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
      <el-col :span="24">
        <el-card>
          <div slot="header" class="card-header">
            <span>服务状态</span>
            <el-button type="text" style="float: right; padding: 3px 0" @click="openDrawer('service')">更多</el-button>
          </div>
          <el-table :data="servicesSlice" border>
            <el-table-column prop="display_name" label="服务名称" />
            <el-table-column prop="status" label="状态">
              <template #default="{ row }">
                <el-tag :type="row.status === 'running' ? 'success' : 'warning'">
                  {{ row.status === 'running' ? '运行中' : '已停止' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="path" label="执行路径" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 网络服务信息 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="full-height-card">
          <div slot="header" class="card-header">
            <span>网络服务信息</span>
            <el-button type="text" style="float: right; padding: 3px 0"
              @click="openDrawer('networkService')">更多</el-button>
          </div>
          <el-table :data="processInfoSlice" border>
            <el-table-column prop="name" label="进程名称" />
            <el-table-column prop="pid" label="PID" />
            <el-table-column prop="exe_path" label="执行路径" />
            <el-table-column label="协议类型">
              <template #default="{ row }">
                {{row.protocols.map(p => formatProtocol(p)).join(', ')}}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 防火墙规则 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="full-height-card">
          <div slot="header" class="card-header">
            <span>防火墙规则</span>
            <el-button type="text" style="float: right; padding: 3px 0" @click="openDrawer('firewall')">更多</el-button>
          </div>
          <el-table :data="firewallRulesSlice" border>
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="enabled" label="已启用" />
            <el-table-column prop="direction" label="方向" />
            <el-table-column prop="profile" label="配置文件" />
            <el-table-column prop="group" label="分组" />
            <el-table-column prop="localIp" label="本地 IP" />
            <el-table-column prop="remoteIp" label="远程 IP" />
            <el-table-column prop="protocol" label="协议" />
            <el-table-column prop="localPort" label="本地端口" />
            <el-table-column prop="remotePort" label="远程端口" />
            <el-table-column prop="edgeTraversal" label="边缘遍历" />
            <el-table-column prop="action" label="操作" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 安装程序 -->
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <div slot="header" class="card-header">
            <span>已安装程序</span>
            <el-button type="text" style="float: right; padding: 3px 0" @click="openDrawer('app')">更多</el-button>
          </div>
          <el-table :data="installedAppsSlice" border>
            <el-table-column prop="name" label="程序名称" />
            <el-table-column prop="version" label="版本" />
            <el-table-column prop="installDate" label="安装日期" />
          </el-table>
        </el-card>
      </el-col>
      <!-- 网络数据统计 -->
      <el-col :span="12">
        <el-card>
          <div slot="header" class="card-header">
            <span>网络数据统计</span>
            <el-button type="text" style="float: right; padding: 3px 0"
              @click="openDrawer('networkStats')">更多</el-button>
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

    <!-- 网络连接抽屉 -->
    <el-drawer v-model="drawers.network.visible" title="网络连接状态" direction="rtl" size="50%">
      <el-table :data="networkTableData" border style="margin: 20px;">
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
      <el-pagination layout="prev, pager, next" :total="networkInterfaces.length" :page-size="drawers.network.pageSize"
        :current-page="drawers.network.currentPage" @current-change="handleDrawerNetworkPageChange"
        style="margin: 20px;" />
    </el-drawer>

    <!-- 进程信息抽屉 -->
    <el-drawer v-model="drawers.process.visible" title="运行进程信息" direction="rtl" size="50%">
      <el-table :data="processTableData" border style="margin: 20px;">
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
      <el-pagination layout="prev, pager, next" :total="processes.length" :page-size="drawers.process.pageSize"
        :current-page="drawers.process.currentPage" @current-change="handleDrawerProcessPageChange"
        style="margin: 20px;" />
    </el-drawer>

    <!-- 服务信息抽屉 -->
    <el-drawer v-model="drawers.service.visible" title="服务状态" direction="rtl" size="50%">
      <el-table :data="serviceTableData" border style="margin: 20px;">
        <el-table-column prop="display_name" label="服务名称" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.status === 'running' ? 'success' : 'warning'">
              {{ row.status === 'running' ? '运行中' : '已停止' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="path" label="执行路径" />
      </el-table>
      <el-pagination layout="prev, pager, next" :total="services.length" :page-size="drawers.service.pageSize"
        :current-page="drawers.service.currentPage" @current-change="handleDrawerServicePageChange"
        style="margin: 20px;" />
    </el-drawer>

    <!-- 网络服务信息抽屉 -->
    <el-drawer v-model="drawers.networkService.visible" title="网络服务信息" direction="rtl" size="50%">
      <el-table :data="networkServiceTableData" border style="margin: 20px;">
        <el-table-column prop="name" label="服务名称" />
        <el-table-column prop="pid" label="PID" />
        <el-table-column prop="exe_path" label="执行路径" />
        <el-table-column label="协议类型">
          <template #default="{ row }">
            {{row.protocols.map(p => formatProtocol(p)).join(', ')}}
          </template>
        </el-table-column>
      </el-table>
      <el-pagination layout="prev, pager, next" :total="networkStats.length" :page-size="drawers.networkStats.pageSize"
        :current-page="drawers.networkStats.currentPage" @current-change="handleDrawerNetworkServicePageChange"
        style="margin: 20px;" />
    </el-drawer>

    <!-- 防火墙抽屉 -->
    <el-drawer v-model="drawers.firewall.visible" title="防火墙规则" direction="rtl" size="50%">
      <el-table :data="firewallTableData" border>
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="enabled" label="已启用" />
        <el-table-column prop="direction" label="方向" />
        <el-table-column prop="profile" label="配置文件" />
        <el-table-column prop="group" label="分组" />
        <el-table-column prop="localIp" label="本地 IP" />
        <el-table-column prop="remoteIp" label="远程 IP" />
        <el-table-column prop="protocol" label="协议" />
        <el-table-column prop="localPort" label="本地端口" />
        <el-table-column prop="remotePort" label="远程端口" />
        <el-table-column prop="edgeTraversal" label="边缘遍历" />
        <el-table-column prop="action" label="操作" />
      </el-table>
      <el-pagination layout="prev, pager, next" :total="firewallRules.length" :page-size="drawers.firewall.pageSize"
        :current-page="drawers.firewall.currentPage" @current-change="handleDrawerFirewallPageChange"
        style="margin: 20px;" />
    </el-drawer>

    <!-- 已安全程序抽屉 -->
    <el-drawer v-model="drawers.app.visible" title="已安装程序" direction="rtl" size="50%">
      <el-table :data="appTableData" border style="margin: 20px;">
        <el-table-column prop="name" label="程序名称" />
        <el-table-column prop="version" label="版本" />
        <el-table-column prop="installDate" label="安装日期" />
      </el-table>
      <el-pagination layout="prev, pager, next" :total="installedApps.length" :page-size="drawers.app.pageSize"
        :current-page="drawers.app.currentPage" @current-change="handleDrawerAppPageChange" style="margin: 20px;" />
    </el-drawer>

    <!-- 网格统计抽屉 -->
    <el-drawer v-model="drawers.networkStats.visible" title="网络数据统计" direction="rtl" size="50%">
      <div style="margin: 20px;">
        <h4>数据统计</h4>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="发送数据量">{{ networkStats.sent }} MB</el-descriptions-item>
          <el-descriptions-item label="接收数据量">{{ networkStats.received }} MB</el-descriptions-item>
        </el-descriptions>
        <h4 style="margin-top: 20px;">开放端口</h4>
        <el-row :gutter="10">
          <el-col v-for="port in openPorts" :key="port" :span="6">
            <el-tag type="info" style="margin: 5px;">{{ port }}</el-tag>
          </el-col>
        </el-row>
        <el-pagination layout="prev, pager, next" :total="openPorts.length" :page-size="drawers.port.pageSize"
          :current-page="drawers.port.currentPage" @current-change="handleDrawerPortPageChange"
          style="margin-top: 15px;" />
      </div>
    </el-drawer>

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
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import * as echarts from 'echarts'

// 系统状态指标
const systemMetrics = ref([
  { label: '系统负载', value: 0, target: 0, color: '#67c23a' },
  { label: 'CPU使用率', value: 0, target: 0, color: '#f56c6c' },
  { label: '内存使用率', value: 0, target: 0, color: '#e69c17' },
  { label: '磁盘使用率', value: 0, target: 0, color: '#409eff' }
])

// 网络接口信息
const networkInterfaces = ref([])

// 网络数据统计
const networkStats = ref({
  sent: 0,
  received: 0
})

// 防火墙规则
const firewallRules = ref([])

// 服务信息
const processInfo = ref([])

// 开放端口
const openPorts = ref([])

// 进程信息
const processes = ref([])


// 服务信息
const services = ref([])



// 已安装程序
const installedApps = ref([])

// 抽屉配置
const drawers = ref({
  network: {
    visible: false,
    currentPage: 1,
    pageSize: 10
  },
  process: {
    visible: false,
    currentPage: 1,
    pageSize: 10
  },
  service: {
    visible: false,
    currentPage: 1,
    pageSize: 10
  },
  firewall: {
    visible: false,
    currentPage: 1,
    pageSize: 10
  },
  app: {
    visible: false,
    currentPage: 1,
    pageSize: 10
  },
  networkStats: {
    visible: false
  },
  port: {
    visible: false,
    currentPage: 1,
    pageSize: 10
  },
  processInfo: {
    visible: false,
    currentPage: 1,
    pageSize: 10
  },
  networkService: {
    visible: false,
    currentPage: 1,
    pageSize: 10
  }
})

// 抽屉分页方法
const handleDrawerNetworkPageChange = (val) => {
  drawers.value.network.currentPage = val
}
const handleDrawerProcessPageChange = (val) => {
  drawers.value.process.currentPage = val
}
const handleDrawerServicePageChange = (val) => {
  drawers.value.service.currentPage = val
}
const handleDrawerFirewallPageChange = (val) => {
  drawers.value.firewall.currentPage = val
}
const handleDrawerAppPageChange = (val) => {
  drawers.value.app.currentPage = val
}
const handleDrawerPortPageChange = (val) => {
  drawers.value.port.currentPage = val
}

const handleDrawerNetworkServicePageChange = (val) => {
  drawers.value.networkService.currentPage = val
}


// 抽屉计算属性
const networkTableData = computed(() => {
  const start = (drawers.value.network.currentPage - 1) * drawers.value.network.pageSize
  return networkInterfaces.value.slice(start, start + drawers.value.network.pageSize)
})

const processTableData = computed(() => {
  const start = (drawers.value.process.currentPage - 1) * drawers.value.process.pageSize
  return processes.value.slice(start, start + drawers.value.process.pageSize)
})

const serviceTableData = computed(() => {
  const start = (drawers.value.service.currentPage - 1) * drawers.value.service.pageSize
  return services.value.slice(start, start + drawers.value.service.pageSize)
})

const firewallTableData = computed(() => {
  const start = (drawers.value.firewall.currentPage - 1) * drawers.value.firewall.pageSize
  return firewallRules.value.slice(start, start + drawers.value.firewall.pageSize)
})

const appTableData = computed(() => {
  const start = (drawers.value.app.currentPage - 1) * drawers.value.app.pageSize
  return installedApps.value.slice(start, start + drawers.value.app.pageSize)
})

const processInfoTableData = computed(() => {
  const start = (drawers.value.processInfo.currentPage - 1) * drawers.value.processInfo.pageSize
  return processInfo.value.slice(start, start + drawers.value.processInfo.pageSize)
})

const networkServiceTableData = computed(() => {
  const start = (drawers.value.processInfo.currentPage - 1) * drawers.value.processInfo.pageSize
  return processInfo.value.slice(start, start + drawers.value.processInfo.pageSize)
})



const processInfoSlice = computed(() => {
  return processInfo.value.slice(0, 3)
})

const servicesSlice = computed(() => {
  return services.value.slice(0, 3)
})

const installedAppsSlice = computed(() => {
  return installedApps.value.slice(0, 5)
})

const firewallRulesSlice = computed(() => {
  return firewallRules.value.slice(0, 3)
})

const processesSlice = computed(() => {
  return processes.value.slice(0, 3)
})


// 协议转换函数
const formatProtocol = (protocol) => {
  switch (protocol) {
    case 'SOCK_STREAM':
      return 'TCP'
    case 'SOCK_DGRAM':
      return 'UDP'
    default:
      return protocol
  }
}

// 打开抽屉
const openDrawer = (type) => {
  drawers.value[type].visible = true
}

// 网络流量监控图表
const networkChart = ref(null)
let chartInstance = null

// 解析速度字符串
function parseSpeed(speedStr) {
  const match = speedStr.match(/\b(\d+\.?\d*)\s+KB\/s/);
  return match ? parseFloat(match[1]) : 0;
}

// 修改后的网络流量数据
const trafficData = {
  times: [],
  sent: [],
  received: []
}



// 获取流量更新
async function updateNetworkChart() {
  if (!chartInstance) return

  try {
    const response = await fetch('http://127.0.0.1:8000/system_traffic')
    if (!response.ok) throw new Error('请求失败')

    const data = await response.json()

    const now = new Date()
    const timeStr = `${now.getHours()}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`

    const uploadSpeed = parseSpeed(data.network.realtime_speed.upload)
    const downloadSpeed = parseSpeed(data.network.realtime_speed.download)

    // 更新数据
    trafficData.times.push(timeStr)
    trafficData.sent.push(uploadSpeed)
    trafficData.received.push(downloadSpeed)

    // 保持固定长度
    if (trafficData.times.length > 10) {
      trafficData.times.shift()
      trafficData.sent.shift()
      trafficData.received.shift()
    }

    // 更新图表
    chartInstance.setOption({
      xAxis: { data: trafficData.times },
      series: [
        { data: trafficData.sent },
        { data: trafficData.received }
      ]
    })

  } catch (error) {
    console.error('获取网络流量数据失败:', error)
  }
}

// 获取系统状态数据
async function fetchSystemStatus() {
  try {
    const response = await fetch('http://localhost:8000/system_status')
    if (!response.ok) throw new Error('请求失败')
    const data = await response.json()
    systemMetrics.value.forEach((metric, index) => {
      let newValue = 0
      switch (index) {
        case 0:
          newValue = parseFloat(data.system_load)
          break
        case 1:
          newValue = parseFloat(data.cpu_usage)
          break
        case 2:
          newValue = parseFloat(data.memory.percent)
          break
        case 3:
          newValue = parseFloat(data.disk_total.percent)
          break
      }
      // 更新target值
      metric.target = Math.round(newValue)
      // 启动动画
      animate(index)
    })
  } catch (error) {
    console.error('获取系统状态失败:', error)
  }
}

async function fetchNetworkData() {
  try {
    const response = await fetch('http://127.0.0.1:8000/system_network')
    if (!response.ok) throw new Error('网络数据请求失败')
    const data = await response.json()

    // 处理网络接口信息
    const interfaces = []
    for (const [name, info] of Object.entries(data.network_interfaces)) {
      interfaces.push({
        interface: name,
        ip: info.ip_address?.[0] || '-',
        mask: info.netmask?.[0] || '255.255.255.0',
        gateway: info.gateways?.[0] || '-',
        status: info.ip_address?.length > 0 ? 'connected' : 'disconnected'
      })
    }
    networkInterfaces.value = interfaces

    // 处理网络统计
    networkStats.value.sent = Math.round(data.data_usage.sent_MB * 100) / 100
    networkStats.value.received = Math.round(data.data_usage.recv_MB * 100) / 100

    // 处理开放端口
    const ports = new Set()
    data.open_ports.forEach(port => {
      if (port.local_address.includes(':')) {
        const portNum = port.local_address.split(':')[1]
        if (portNum) ports.add(portNum)
      }
    })
    openPorts.value = Array.from(ports).sort((a, b) => a - b)

    // 处理防火墙规则
    firewallRules.value = data.firewall_rules.map(rule => ({
      name: rule.name,
      enabled: rule["已启用"],
      direction: rule["方向"],
      profile: rule["配置文件"],
      group: rule["分组"],
      localIp: rule["本地 IP"],
      remoteIp: rule["远程 IP"],
      protocol: rule["协议"],
      localPort: rule["本地端口"] || "-",
      remotePort: rule["远程端口"] || "-",
      edgeTraversal: rule["边缘遍历"],
      action: rule["操作"]
    }))

    // 处理网络服务
    processInfo.value = data.network_services.map(service => ({
      name: service.name,
      pid: service.pid,
      exe_path: service.exe_path || '-',
      protocols: service.protocols || []
    }))
  } catch (error) {
    console.error('获取网络数据失败:', error)
  }
}

// 获取系统服务数据
async function fetchSystemServices() {
  try {
    const response = await fetch('http://127.0.0.1:8000/system_process')
    if (!response.ok) throw new Error('系统服务数据请求失败')
    const data = await response.json()

    // 处理服务数据
    services.value = data.critical_services.map(service => ({
      display_name: service.display_name,
      status: service.state === '运行中' ? 'running' : 'stopped',
      path: service.executable_path || '-'
    }))

    // 处理已安装程序数据
    installedApps.value = data.installed_programs.map(app => ({
      name: app.name,
      version: app.version,
      installDate: app.install_date || 'N/A'
    }))
  } catch (error) {
    console.error('获取系统服务数据失败:', error)
  }
}

async function fetchSystemProcess() {
  try {
    const response = await fetch('http://127.0.0.1:8000/system_running');
    if (!response.ok) throw new Error('系统运行数据请求失败');
    const data = await response.json();

    // 处理进程数据（applications）
    processes.value = data.applications.map(app => ({
      pid: app.pid,
      name: app.name,
      status: app.status,
      cpu: parseFloat(app.cpu_usage), // 提取 CPU 使用率数值
      memory: parseFloat(app.memory_mb), // 提取内存使用数值（MB）
      path: app.exe_path || '-',
      user: app.user || 'N/A',
      permission: app.privilege_level || '未知'
    }));
  } catch (error) {
    console.error('获取系统运行数据失败:', error);
  }
}


// 动画逻辑
const animationTimers = ref([])

// 定义动画函数
function animate(index) {
  const metric = systemMetrics.value[index]
  const difference = metric.target - metric.value
  if (Math.abs(difference) < 1) {
    metric.value = metric.target
    return
  }
  // 每次向目标值靠近 10% 的差值
  metric.value += difference * 0.1
  // 继续下一帧动画
  animationTimers.value[index] = requestAnimationFrame(() => animate(index))
}



onMounted(() => {
  // 初始化获取数据
  fetchSystemStatus()
  fetchNetworkData()
  fetchSystemServices()
  fetchSystemProcess()

  // 启动定时器
  const fetchInterval = setInterval(fetchSystemStatus, 5000)
  const networkInterval = setInterval(fetchNetworkData, 10000)
  const processInterval = setInterval(fetchSystemServices, 30000)
  const processInterval1 = setInterval(fetchSystemProcess, 30000)



  // 启动初始动画
  systemMetrics.value.forEach((_, index) => {
    animate(index)
  })

  // 初始化网络流量图表
  chartInstance = echarts.init(networkChart.value)
  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['发送数据', '接收数据'] },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: trafficData.times,
      name: '时间'
    },
    yAxis: {
      type: 'value',
      name: 'KB/s',
      axisLabel: {
        formatter: '{value} KB/s'
      }
    },
    series: [
      {
        name: '发送数据',
        type: 'line',
        data: trafficData.sent,
        smooth: true,
        itemStyle: { color: '#67c23a' }
      },
      {
        name: '接收数据',
        type: 'line',
        data: trafficData.received,
        smooth: true,
        itemStyle: { color: '#409eff' }
      }
    ]
  }
  chartInstance.setOption(option)

  updateNetworkChart()
  // 启动网络图表更新
  const chartInterval = setInterval(updateNetworkChart, 5000)

  // 清理函数
  onBeforeUnmount(() => {
    clearInterval(fetchInterval)
    clearInterval(chartInterval)
    clearInterval(networkInterval)
    clearInterval(processInterval)
    clearInterval(processInterval1)
    animationTimers.value.forEach(timer => cancelAnimationFrame(timer))
    if (chartInstance) {
      chartInstance.dispose()
    }
  })
})
</script>

<style scoped src="../../../src/assets/css/Home_Host.css"></style>