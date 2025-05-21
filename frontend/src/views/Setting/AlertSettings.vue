<template>
  <div class="settings-card">
    <h2>告警设置</h2>
    <el-form label-position="right" label-width="120px" :model="alertSettings">
      <el-form-item label="启用告警">
        <el-switch v-model="alertSettings.enabled" />
      </el-form-item>
      <el-form-item label="告警方式">
        <el-checkbox-group v-model="alertSettings.methods">
          <el-checkbox label="email">邮箱</el-checkbox>
          <el-checkbox label="sms">短信</el-checkbox>
          <el-checkbox label="push">推送通知</el-checkbox>
        </el-checkbox-group>
      </el-form-item>
      <el-form-item label="告警阈值">
        <el-slider v-model="alertSettings.threshold" :min="1" :max="10" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="saveAlertSettings">保存设置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { ElMessage } from 'element-plus'

const alertSettings = reactive({
  enabled: true,
  methods: ['email', 'push'],
  threshold: 5
})

function saveAlertSettings() {
  ElMessage.success('告警设置保存成功')
}
</script>

<style scoped>
.settings-card {
  background: #fff;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}
</style>