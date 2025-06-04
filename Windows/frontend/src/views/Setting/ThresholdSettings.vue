<template>
  <div class="settings-card">
    <el-form label-position="right" label-width="150px">
      <!-- 动态基线开关 -->
      <el-form-item label="动态基线启用">
        <el-switch v-model="dynamicBaselineEnabled" @change="handleSwitchChange" />
      </el-form-item>

      <!-- 配置表单 -->
      <el-form-item label="窗口大小（天）">
        <el-input-number v-model="form.windowSize" :min="1" />
      </el-form-item>
      <el-form-item label="异常检测阈值倍数">
        <el-input-number v-model="form.thresholdMultiplier" :min="0.1" :step="0.1" />
      </el-form-item>

      <!-- 操作按钮 -->
      <el-form-item>
        <el-button type="primary" @click="saveConfig">更新配置</el-button>
      </el-form-item>
    </el-form>
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

// 动态基线开关状态
const dynamicBaselineEnabled = ref(false)

// 表单数据
const form = reactive({
  windowSize: 7,      // 窗口大小（天）
  thresholdMultiplier: 3.0  // 异常检测阈值倍数
})

// 初始化获取状态
onMounted(async () => {
  try {
    const response = await apiClient.get('/metrics-task-control')
    dynamicBaselineEnabled.value = response.data.status === 'Task is running'
  } catch (error) {
    ElMessage.error('无法获取当前状态，请检查服务是否正常')
    console.error('获取状态失败:', error)
  }
})

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

// 保存配置
function saveConfig() {
  ElMessageBox.confirm('确定要更新配置吗？', '确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'info'
  }).then(() => {
    // 这里可以添加实际的保存逻辑
    ElMessage.success('配置更新成功')
  }).catch(() => {
    // 取消操作
  })
}
</script>

<style scoped>
.settings-card {
  background: #fff;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  margin-top: 220px;
}
</style>