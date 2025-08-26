<template>
  <div class="settings-card">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>动态基线设置</span>
        </div>
      </template>

      <!-- 动态基线开关 -->
      <el-form label-position="right" label-width="150px">
        <el-form-item label="动态基线启用">
          <el-switch v-model="dynamicBaselineEnabled" @change="handleSwitchChange" />
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="box-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>基线配置管理</span>
          <el-button type="primary" @click="resetForm" size="small">新增基线</el-button>
        </div>
      </template>

      <!-- 基线列表 -->
      <div class="baseline-list">
        <el-table :data="baselineConfigs" style="width: 100%" v-loading="loading">
          <el-table-column prop="metric_name" label="指标名称" width="180" />
          <el-table-column prop="window_size" label="窗口大小(小时)" width="120" />
          <el-table-column prop="threshold_sigma" label="阈值倍数" width="120" />
          <el-table-column label="启用状态" width="100">
            <template #default="scope">
              <el-switch v-model="scope.row.enabled" @change="updateConfigStatus(scope.row)" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="scope">
              <el-button size="small" @click="editConfig(scope.row)">编辑</el-button>
              <el-button size="small" type="danger" @click="deleteConfig(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 添加/编辑基线配置表单 -->
      <div class="baseline-form" style="margin-top: 30px;">
        <el-form :model="form" label-position="right" label-width="150px">
          <el-form-item label="指标名称" required>
            <el-input v-model="form.metric_name" :disabled="isEditing" placeholder="请输入指标名称，如：cpu_usage" />
          </el-form-item>
          <el-form-item label="窗口大小（小时）" required>
            <el-input-number v-model="form.window_size" :min="1" placeholder="请输入窗口大小" />
          </el-form-item>
          <el-form-item label="异常检测阈值倍数" required>
            <el-input-number v-model="form.threshold_sigma" :min="0.1" :step="0.1" placeholder="请输入阈值倍数" />
          </el-form-item>
          <el-form-item>
            <el-button v-if="!isEditing" type="primary" @click="createConfig">添加基线</el-button>
            <el-button v-else type="primary" @click="updateConfig">更新配置</el-button>
            <el-button @click="resetForm">取消</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

// 创建axios实例
const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
})

// 响应式数据
const dynamicBaselineEnabled = ref(false)
const baselineConfigs = ref([])
const loading = ref(false)
const isEditing = ref(false)

// 表单数据
const form = reactive({
  metric_name: '',
  window_size: 24,
  threshold_sigma: 3.0,
  enabled: true
})

// 初始化获取状态
onMounted(async () => {
  try {
    const response = await apiClient.get('/metrics-task-control')
    dynamicBaselineEnabled.value = response.data.status === 'Task is running'
    await loadBaselineConfigs()
  } catch (error) {
    ElMessage.error('无法获取当前状态，请检查服务是否正常')
    console.error('获取状态失败:', error)
  }
})

// 加载所有基线配置
async function loadBaselineConfigs() {
  loading.value = true
  try {
    const response = await apiClient.get('/baseline/configs')
    baselineConfigs.value = response.data.data
  } catch (error) {
    ElMessage.error('加载基线配置失败')
    console.error('加载基线配置失败:', error)
  } finally {
    loading.value = false
  }
}

// 处理开关变化
async function handleSwitchChange(value) {
  const action = value ? 'start' : 'stop'
  const confirmText = value ? '确定要启动动态基线吗？' : '确定要关闭动态基线吗？'

  try {
    const result = await ElMessageBox.confirm(confirmText, '确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })

    if (result === 'confirm') {
      const response = await apiClient.get(`/metrics-task-control?action=${action}`)

      // 根据接口响应更新实际状态
      const currentStatus = await apiClient.get('/metrics-task-control')
      dynamicBaselineEnabled.value = currentStatus.data.status === 'Task is running'
    }
  } catch (error) {
    ElMessage.error(action === 'start' ? '启动失败' : '关闭失败')
    dynamicBaselineEnabled.value = !value // 回滚状态
    console.error(`${action}失败:`, error)
  }
}

// 创建新基线配置
async function createConfig() {
  if (!form.metric_name) {
    ElMessage.warning('请输入指标名称')
    return
  }

  try {
    const configData = {
      metric_name: form.metric_name,
      window_size: form.window_size,
      threshold_sigma: form.threshold_sigma,
      enabled: form.enabled
    }

    await apiClient.post('/baseline/config', configData)
    ElMessage.success('基线配置创建成功')
    resetForm()
    await loadBaselineConfigs()
  } catch (error) {
    ElMessage.error('创建基线配置失败: ' + (error.response?.data?.detail || error.message))
    console.error('创建基线配置失败:', error)
  }
}

// 编辑基线配置
function editConfig(config) {
  isEditing.value = true
  Object.assign(form, {
    metric_name: config.metric_name,
    window_size: config.window_size,
    threshold_sigma: config.threshold_sigma,
    enabled: config.enabled
  })
}

// 更新基线配置
async function updateConfig() {
  try {
    const updateData = {
      window_size: form.window_size,
      threshold_sigma: form.threshold_sigma,
      enabled: form.enabled
    }

    await apiClient.put(`/baseline/config/${form.metric_name}`, updateData)
    ElMessage.success('基线配置更新成功')
    resetForm()
    await loadBaselineConfigs()
  } catch (error) {
    ElMessage.error('更新基线配置失败: ' + (error.response?.data?.detail || error.message))
    console.error('更新基线配置失败:', error)
  }
}

// 更新基线启用状态
async function updateConfigStatus(config) {
  try {
    await apiClient.put(`/baseline/config/${config.metric_name}`, {
      enabled: config.enabled
    })
    ElMessage.success('状态更新成功')
    await loadBaselineConfigs()
  } catch (error) {
    ElMessage.error('状态更新失败: ' + (error.response?.data?.detail || error.message))
    // 回滚状态
    config.enabled = !config.enabled
    console.error('状态更新失败:', error)
  }
}

// 删除基线配置
async function deleteConfig(config) {
  try {
    await ElMessageBox.confirm(`确定要删除基线 "${config.metric_name}" 吗？`, '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await apiClient.delete(`/baseline/config/${config.metric_name}`)
    ElMessage.success('基线配置删除成功')
    await loadBaselineConfigs()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除基线配置失败: ' + (error.response?.data?.detail || error.message))
      console.error('删除基线配置失败:', error)
    }
  }
}

// 重置表单
function resetForm() {
  Object.assign(form, {
    metric_name: '',
    window_size: 24,
    threshold_sigma: 3.0,
    enabled: true
  })
  isEditing.value = false
}
</script>

<style scoped>
.settings-card {
  background: #f5f5f5;
  min-height: 100vh;
  padding: 20px;
}

.box-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: 500;
}

.baseline-list {
  margin-bottom: 20px;
}
</style>