<template>
  <div class="settings-card">
    <h2>账户信息</h2>
    <el-form label-position="right" label-width="120px" :model="accountInfo">
      <el-form-item label="用户名">
        <el-input v-model="accountInfo.username" disabled />
      </el-form-item>
      <el-form-item label="邮箱">
        <el-input v-model="accountInfo.email" />
      </el-form-item>
      <el-form-item label="手机号">
        <el-input v-model="accountInfo.phone" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="saveAccountInfo">保存更新</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { ElMessage } from 'element-plus'

const accountInfo = reactive({
  username: 'admin',
  email: 'admin@example.com',
  phone: '13800138000'
})

function saveAccountInfo() {
  ElMessage.success('账户信息保存成功')
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