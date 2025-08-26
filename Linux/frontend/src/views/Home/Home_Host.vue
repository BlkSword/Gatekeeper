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
            <el-table-column prop="cpu" label="CPU(%)" />
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
            <el-table-column prop="num" label="规则编号" />
            <el-table-column prop="target" label="目标操作" />
            <el-table-column prop="prot" label="协议类型">
              <template #default="{ row }">
                <el-tag :type="getProtocolType(row.prot)">
                  {{ formatProtocol(row.prot) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="source" label="源地址" />
            <el-table-column prop="destination" label="目标地址" />
            <el-table-column prop="pkts" label="数据包数" />
            <el-table-column prop="bytes" label="字节数" />
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
      <div style="margin: 20px;">
        <el-input v-model="searchQueries.network" placeholder="搜索网络接口..." clearable style="margin-bottom: 20px;">
          <template #prefix>
            <el-icon>
              <Search />
            </el-icon>
          </template>
        </el-input>
      </div>
      <el-table :data="filteredNetworkTableData" border style="margin: 20px;">
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
      <el-pagination layout="prev, pager, next" :total="filteredNetworkInterfaces.length"
        :page-size="drawers.network.pageSize" :current-page="drawers.network.currentPage"
        @current-change="handleDrawerNetworkPageChange" style="margin: 20px;" />
    </el-drawer>

    <!-- 进程信息抽屉 -->
    <el-drawer v-model="drawers.process.visible" title="运行进程信息" direction="rtl" size="50%">
      <div style="margin: 20px;">
        <el-input v-model="searchQueries.process" placeholder="搜索进程..." clearable style="margin-bottom: 20px;">
          <template #prefix>
            <el-icon>
              <Search />
            </el-icon>
          </template>
        </el-input>
      </div>
      <el-table :data="filteredProcessTableData" border style="margin: 20px;">
        <el-table-column prop="name" label="进程名称" />
        <el-table-column prop="pid" label="PID" />
        <el-table-column prop="cpu" label="CPU(%)" />
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
      <el-pagination layout="prev, pager, next" :total="filteredProcesses.length" :page-size="drawers.process.pageSize"
        :current-page="drawers.process.currentPage" @current-change="handleDrawerProcessPageChange"
        style="margin: 20px;" />
    </el-drawer>

    <!-- 服务信息抽屉 -->
    <el-drawer v-model="drawers.service.visible" title="服务状态" direction="rtl" size="50%">
      <div style="margin: 20px;">
        <el-input v-model="searchQueries.service" placeholder="搜索服务..." clearable style="margin-bottom: 20px;">
          <template #prefix>
            <el-icon>
              <Search />
            </el-icon>
          </template>
        </el-input>
      </div>
      <el-table :data="filteredServiceTableData" border style="margin: 20px;">
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
      <el-pagination layout="prev, pager, next" :total="filteredServices.length" :page-size="drawers.service.pageSize"
        :current-page="drawers.service.currentPage" @current-change="handleDrawerServicePageChange"
        style="margin: 20px;" />
    </el-drawer>

    <!-- 网络服务信息抽屉 -->
    <el-drawer v-model="drawers.networkService.visible" title="网络服务信息" direction="rtl" size="50%">
      <div style="margin: 20px;">
        <el-input v-model="searchQueries.networkService" placeholder="搜索网络服务..." clearable style="margin-bottom: 20px;">
          <template #prefix>
            <el-icon>
              <Search />
            </el-icon>
          </template>
        </el-input>
      </div>
      <el-table :data="filteredNetworkServiceTableData" border style="margin: 20px;">
        <el-table-column prop="name" label="服务名称" />
        <el-table-column prop="pid" label="PID" />
        <el-table-column prop="exe_path" label="执行路径" />
        <el-table-column label="协议类型">
          <template #default="{ row }">
            {{row.protocols.map(p => formatProtocol(p)).join(', ')}}
          </template>
        </el-table-column>
      </el-table>
      <el-pagination layout="prev, pager, next" :total="filteredNetworkServices.length"
        :page-size="drawers.networkService.pageSize" :current-page="drawers.networkService.currentPage"
        @current-change="handleDrawerNetworkServicePageChange" style="margin: 20px;" />
    </el-drawer>

    <!-- 防火墙抽屉 -->
    <el-drawer v-model="drawers.firewall.visible" title="防火墙规则" direction="rtl" size="50%">
      <div style="margin: 20px;">
        <el-input v-model="searchQueries.firewall" placeholder="搜索防火墙规则..." clearable style="margin-bottom: 20px;">
          <template #prefix>
            <el-icon>
              <Search />
            </el-icon>
          </template>
        </el-input>
      </div>
      <el-table :data="filteredFirewallTableData" border>
        <el-table-column prop="num" label="规则编号" />
        <el-table-column prop="target" label="目标操作" />
        <el-table-column prop="prot" label="协议类型">
          <template #default="{ row }">
            <el-tag :type="getProtocolType(row.prot)">
              {{ formatProtocol(row.prot) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="source" label="源地址" />
        <el-table-column prop="destination" label="目标地址" />
        <el-table-column prop="pkts" label="数据包数" />
        <el-table-column prop="bytes" label="字节数" />
      </el-table>
      <el-pagination layout="prev, pager, next" :total="filteredFirewallRules.length"
        :page-size="drawers.firewall.pageSize" :current-page="drawers.firewall.currentPage"
        @current-change="handleDrawerFirewallPageChange" style="margin: 20px;" />
    </el-drawer>

    <!-- 已安装程序抽屉 -->
    <el-drawer v-model="drawers.app.visible" title="已安装程序" direction="rtl" size="50%">
      <div style="margin: 20px;">
        <el-input v-model="searchQueries.app" placeholder="搜索已安装程序..." clearable style="margin-bottom: 20px;">
          <template #prefix>
            <el-icon>
              <Search />
            </el-icon>
          </template>
        </el-input>
      </div>
      <el-table :data="filteredAppTableData" border style="margin: 20px;">
        <el-table-column prop="name" label="程序名称" />
        <el-table-column prop="version" label="版本" />
        <el-table-column prop="installDate" label="安装日期" />
      </el-table>
      <el-pagination layout="prev, pager, next" :total="filteredInstalledApps.length" :page-size="drawers.app.pageSize"
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
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import * as echarts from 'echarts'
import { Search } from '@element-plus/icons-vue'

// 缓存键名
const CACHE_KEYS = {
  SYSTEM_METRICS: 'system_metrics',
  NETWORK_INTERFACES: 'network_interfaces',
  NETWORK_STATS: 'network_stats',
  FIREWALL_RULES: 'firewall_rules',
  PROCESS_INFO: 'process_info',
  OPEN_PORTS: 'open_ports',
  PROCESSES: 'processes',
  SERVICES: 'services',
  INSTALLED_APPS: 'installed_apps',
}

// 缓存有效期（毫秒）
const CACHE_TTL = 5 * 60 * 1000 // 5分钟

// 读取缓存
function getCache(key) {
  const cached = localStorage.getItem(key)
  if (!cached) return null
  try {
    const data = JSON.parse(cached)
    if (Date.now() - data.timestamp < CACHE_TTL) {
      return data.value
    }
  } catch (e) {
    console.error('缓存解析失败:', e)
  }
  return null
}

// 设置缓存
function setCache(key, value) {
  localStorage.setItem(key, JSON.stringify({
    timestamp: Date.now(),
    value: value
  }))
}

// 初始化数据
const systemMetrics = ref([
  { label: '系统负载', value: 0, target: 0, color: '#67c23a' },
  { label: 'CPU使用率', value: 0, target: 0, color: '#f56c6c' },
  { label: '内存使用率', value: 0, target: 0, color: '#e69c17' },
  { label: '磁盘使用率', value: 0, target: 0, color: '#409eff' }
])

const networkInterfaces = ref([])
const networkStats = ref({ sent: 0, received: 0 })
const firewallRules = ref([])
const processInfo = ref([])
const openPorts = ref([])
const processes = ref([])
const services = ref([])
const installedApps = ref([])

// 搜索查询
const searchQueries = ref({
  network: '',
  process: '',
  service: '',
  networkService: '',
  firewall: '',
  app: ''
})

// 从缓存加载数据
function loadFromCache() {
  const metrics = getCache(CACHE_KEYS.SYSTEM_METRICS)
  if (metrics) systemMetrics.value = metrics
  const interfaces = getCache(CACHE_KEYS.NETWORK_INTERFACES)
  if (interfaces) networkInterfaces.value = interfaces
  const stats = getCache(CACHE_KEYS.NETWORK_STATS)
  if (stats) networkStats.value = stats
  const rules = getCache(CACHE_KEYS.FIREWALL_RULES)
  if (rules) firewallRules.value = rules
  const ports = getCache(CACHE_KEYS.OPEN_PORTS)
  if (ports) openPorts.value = ports
  const info = getCache(CACHE_KEYS.PROCESS_INFO)
  if (info) processInfo.value = info
  const procs = getCache(CACHE_KEYS.PROCESSES)
  if (procs) processes.value = procs
  const svc = getCache(CACHE_KEYS.SERVICES)
  if (svc) services.value = svc
  const apps = getCache(CACHE_KEYS.INSTALLED_APPS)
  if (apps) installedApps.value = apps
}

// 获取系统状态数据（带缓存更新）
async function fetchSystemStatus() {
  try {
    const response = await fetch('http://127.0.0.1:8000/system_status')
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
      metric.target = Math.round(newValue)
      animate(index)
    })
    setCache(CACHE_KEYS.SYSTEM_METRICS, systemMetrics.value)
  } catch (error) {
    console.error('获取系统状态失败:', error)
  }
}

// 获取网络数据（带缓存更新）
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
    setCache(CACHE_KEYS.NETWORK_INTERFACES, interfaces)

    // 处理网络统计
    networkStats.value.sent = Math.round(data.data_usage.sent_MB * 100) / 100
    networkStats.value.received = Math.round(data.data_usage.recv_MB * 100) / 100
    setCache(CACHE_KEYS.NETWORK_STATS, networkStats.value)

    // 处理防火墙规则
    firewallRules.value = data.firewall_rules.map(rule => ({
      num: rule.num,
      target: rule.target,
      prot: rule.prot,
      source: rule.source,
      destination: rule.destination,
      pkts: rule.pkts,
      bytes: rule.bytes
    }))
    setCache(CACHE_KEYS.FIREWALL_RULES, firewallRules.value)

    // 处理开放端口
    const ports = new Set()
    data.open_ports.forEach(port => {
      if (port.local_address.includes(':')) {
        const portNum = port.local_address.split(':')[1]
        if (portNum) ports.add(portNum)
      }
    })
    openPorts.value = Array.from(ports).sort((a, b) => a - b)
    setCache(CACHE_KEYS.OPEN_PORTS, openPorts.value)

    // 处理网络服务
    processInfo.value = data.network_services.map(service => ({
      name: service.name,
      pid: service.pid,
      exe_path: service.exe_path || '-',
      protocols: service.protocols || []
    }))
    setCache(CACHE_KEYS.PROCESS_INFO, processInfo.value)
  } catch (error) {
    console.error('获取网络数据失败:', error)
  }
}

// 获取系统服务数据（带缓存更新）
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
    setCache(CACHE_KEYS.SERVICES, services.value)

    // 处理已安装程序数据
    installedApps.value = data.installed_programs.map(app => ({
      name: app.name,
      version: app.version,
      installDate: app.install_date || 'N/A'
    }))
    setCache(CACHE_KEYS.INSTALLED_APPS, installedApps.value)
  } catch (error) {
    console.error('获取系统服务数据失败:', error)
  }
}

// 获取系统运行数据（带缓存更新）
async function fetchSystemProcess() {
  try {
    const response = await fetch('http://127.0.0.1:8000/system_running')
    if (!response.ok) throw new Error('系统运行数据请求失败')
    const data = await response.json()

    // 处理进程数据（applications）
    processes.value = data.applications.map(app => ({
      pid: app.pid,
      name: app.name,
      status: app.status,
      cpu: parseFloat(app.cpu_usage),
      memory: parseFloat(app.memory_mb),
      path: app.exe_path || '-',
      user: app.user || 'N/A',
      permission: app.privilege_level || '未知'
    }))
    setCache(CACHE_KEYS.PROCESSES, processes.value)
  } catch (error) {
    console.error('获取系统运行数据失败:', error)
  }
}

// 动画逻辑
const animationTimers = ref([])
function animate(index) {
  const metric = systemMetrics.value[index]
  const difference = metric.target - metric.value
  if (Math.abs(difference) < 1) {
    metric.value = metric.target
    return
  }
  metric.value += difference * 0.1
  animationTimers.value[index] = requestAnimationFrame(() => animate(index))
}

// 初始化图表
const networkChart = ref(null)
let chartInstance = null
const trafficData = {
  times: [],
  sent: [],
  received: []
}

// 更新网络流量图表
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
    trafficData.times.push(timeStr)
    trafficData.sent.push(uploadSpeed)
    trafficData.received.push(downloadSpeed)
    if (trafficData.times.length > 10) {
      trafficData.times.shift()
      trafficData.sent.shift()
      trafficData.received.shift()
    }
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

// 解析速度字符串
function parseSpeed(speedStr) {
  const match = speedStr.match(/\b(\d+\.?\d*)\s+KB\/s/)
  return match ? parseFloat(match[1]) : 0
}

// 协议格式化
function formatProtocol(protocol) {
  switch (protocol) {
    case '0':
      return 'ALL'
    case '6':
      return 'TCP'
    case '17':
      return 'UDP'
    default:
      return protocol
  }
}

// 协议类型颜色
function getProtocolType(protocol) {
  switch (protocol) {
    case '0':
      return 'info'
    case '6':
      return 'success'
    case '17':
      return 'warning'
    default:
      return 'info'
  }
}

// 抽屉相关逻辑
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

// 打开抽屉
function openDrawer(type) {
  drawers.value[type].visible = true
}

// 分页逻辑
function handleDrawerNetworkPageChange(val) {
  drawers.value.network.currentPage = val
}

function handleDrawerProcessPageChange(val) {
  drawers.value.process.currentPage = val
}

function handleDrawerServicePageChange(val) {
  drawers.value.service.currentPage = val
}

function handleDrawerFirewallPageChange(val) {
  drawers.value.firewall.currentPage = val
}

function handleDrawerAppPageChange(val) {
  drawers.value.app.currentPage = val
}

function handleDrawerPortPageChange(val) {
  drawers.value.port.currentPage = val
}

function handleDrawerNetworkServicePageChange(val) {
  drawers.value.networkService.currentPage = val
}

// 搜索过滤逻辑
const filteredNetworkInterfaces = computed(() => {
  const query = searchQueries.value.network.toLowerCase().trim()
  if (!query) return networkInterfaces.value
  return networkInterfaces.value.filter(item =>
    item.interface.toLowerCase().includes(query) ||
    item.ip.toLowerCase().includes(query) ||
    item.mask.toLowerCase().includes(query) ||
    item.gateway.toLowerCase().includes(query) ||
    item.status.toLowerCase().includes(query)
  )
})

const filteredProcesses = computed(() => {
  const query = searchQueries.value.process.toLowerCase().trim()
  if (!query) return processes.value
  return processes.value.filter(item =>
    item.name.toLowerCase().includes(query) ||
    item.pid.toString().includes(query) ||
    item.path.toLowerCase().includes(query) ||
    item.user.toLowerCase().includes(query) ||
    item.permission.toLowerCase().includes(query)
  )
})

const filteredServices = computed(() => {
  const query = searchQueries.value.service.toLowerCase().trim()
  if (!query) return services.value
  return services.value.filter(item =>
    item.display_name.toLowerCase().includes(query) ||
    item.status.toLowerCase().includes(query) ||
    item.path.toLowerCase().includes(query)
  )
})

const filteredNetworkServices = computed(() => {
  const query = searchQueries.value.networkService.toLowerCase().trim()
  if (!query) return processInfo.value
  return processInfo.value.filter(item =>
    item.name.toLowerCase().includes(query) ||
    item.pid.toString().includes(query) ||
    item.exe_path.toLowerCase().includes(query) ||
    item.protocols.some(p => p.toLowerCase().includes(query))
  )
})

const filteredFirewallRules = computed(() => {
  const query = searchQueries.value.firewall.toLowerCase().trim()
  if (!query) return firewallRules.value
  return firewallRules.value.filter(item =>
    item.num.toString().includes(query) ||
    item.target.toLowerCase().includes(query) ||
    item.prot.toLowerCase().includes(query) ||
    item.source.toLowerCase().includes(query) ||
    item.destination.toLowerCase().includes(query) ||
    item.pkts.toString().includes(query) ||
    item.bytes.toString().includes(query)
  )
})

const filteredInstalledApps = computed(() => {
  const query = searchQueries.value.app.toLowerCase().trim()
  if (!query) return installedApps.value
  return installedApps.value.filter(item =>
    item.name.toLowerCase().includes(query) ||
    item.version.toLowerCase().includes(query) ||
    item.installDate.toLowerCase().includes(query)
  )
})

// 计算属性 - 分页数据
const filteredNetworkTableData = computed(() => {
  const start = (drawers.value.network.currentPage - 1) * drawers.value.network.pageSize
  return filteredNetworkInterfaces.value.slice(start, start + drawers.value.network.pageSize)
})

const filteredProcessTableData = computed(() => {
  const start = (drawers.value.process.currentPage - 1) * drawers.value.process.pageSize
  return filteredProcesses.value.slice(start, start + drawers.value.process.pageSize)
})

const filteredServiceTableData = computed(() => {
  const start = (drawers.value.service.currentPage - 1) * drawers.value.service.pageSize
  return filteredServices.value.slice(start, start + drawers.value.service.pageSize)
})

const filteredNetworkServiceTableData = computed(() => {
  const start = (drawers.value.networkService.currentPage - 1) * drawers.value.networkService.pageSize
  return filteredNetworkServices.value.slice(start, start + drawers.value.networkService.pageSize)
})

const filteredFirewallTableData = computed(() => {
  const start = (drawers.value.firewall.currentPage - 1) * drawers.value.firewall.pageSize
  return filteredFirewallRules.value.slice(start, start + drawers.value.firewall.pageSize)
})

const filteredAppTableData = computed(() => {
  const start = (drawers.value.app.currentPage - 1) * drawers.value.app.pageSize
  return filteredInstalledApps.value.slice(start, start + drawers.value.app.pageSize)
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
  return firewallRules.value.slice(0, 5)
})

const processesSlice = computed(() => {
  return processes.value.slice(0, 3)
})

onMounted(() => {
  loadFromCache() // 先加载缓存数据
  fetchSystemStatus()
  fetchNetworkData()
  fetchSystemServices()
  fetchSystemProcess()

  // 启动定时器
  const fetchInterval = setInterval(fetchSystemStatus, 5000)
  const networkInterval = setInterval(fetchNetworkData, 10000)
  const processInterval = setInterval(fetchSystemServices, 30000)
  const processInterval1 = setInterval(fetchSystemProcess, 30000)
  const chartInterval = setInterval(updateNetworkChart, 5000)

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