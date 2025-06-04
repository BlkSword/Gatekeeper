<template>
  <div class="settings-card">
    <el-form label-position="right" label-width="120px" :model="formData">
      <!-- 告警设置 -->
      <el-form-item label="启用告警">
        <el-switch v-model="formData.alertSettings.enabled" @change="handleAlertSwitchChange" />
      </el-form-item>
      <el-form-item label="告警阈值">
        <el-slider v-model="formData.alertSettings.threshold" :min="1" :max="10" />
      </el-form-item>

      <!-- 邮件配置 -->
      <el-divider content-position="left">邮件通知配置</el-divider>
      <el-form-item label="SMTP服务器">
        <el-input v-model="formData.emailConfig.host_server" placeholder="smtp.example.com" />
      </el-form-item>
      <el-form-item label="发件人邮箱">
        <el-input v-model="formData.emailConfig.sender_qq" placeholder="your@email.com" />
      </el-form-item>
      <el-form-item label="SMTP密码">
        <el-input v-model="formData.emailConfig.pwd" type="password" show-password placeholder="授权码/密码" />
      </el-form-item>
      <el-form-item label="收件人邮箱">
        <el-input v-model="formData.emailConfig.receiver" placeholder="多个邮箱用逗号分隔" />
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="saveSettings">保存设置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { ElMessage, ElMessageBox, ElDivider } from 'element-plus'
import axios from 'axios'

// 创建axios实例
const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
})

// 统一表单数据结构
const formData = reactive({
  alertSettings: {
    enabled: true,
    threshold: 5
  },
  emailConfig: {
    host_server: '',
    sender_qq: '',
    pwd: '',
    receiver: ''
  }
})

// 处理告警开关变化
async function handleAlertSwitchChange(value) {
  const action = value ? 'enable' : 'disable'
  const confirmText = value ? '确定要启用告警吗？' : '确定要禁用告警吗？'

  try {
    const result = await ElMessageBox.confirm(confirmText, '告警控制', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    if (result === 'confirm') {
      const response = await apiClient.get(`/anomaly-monitor-control?action=${action}`)
      ElMessage({ message: `告警功能已${value ? '启用' : '禁用'}`, type: 'success', duration: 2500 })
    }
  } catch (error) {
    formData.alertSettings.enabled = !value
    ElMessage({ message: `操作失败: ${error.message}`, type: 'error', duration: 3000 })
    console.error(`${action}失败:`, error)
  }
}

// 保存所有设置
async function saveSettings() {
  try {
    const confirmResult = await ElMessageBox.confirm('确定要保存所有设置吗？', '配置确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })

    if (confirmResult === 'confirm') {
      // 1. 保存阈值设置（GET请求）
      await apiClient.get(`/threshold?threshold=${formData.alertSettings.threshold}`)

      // 2. 保存邮件配置（POST请求）
      const formattedConfig = {
        ...formData.emailConfig,
        receiver: formData.emailConfig.receiver.split(',').map(email => email.trim())
      }

      await apiClient.post('/update_alert_config', formattedConfig)

      ElMessage({ message: '设置保存成功', type: 'success', duration: 2000 })
    }
  } catch (error) {
    ElMessage({
      message: `保存失败: ${error.response?.data?.error || error.message}`,
      type: 'error',
      duration: 3000
    })
    console.error('保存配置失败:', error)
  }
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