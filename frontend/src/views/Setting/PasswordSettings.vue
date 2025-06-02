<template>
  <div class="settings-card">
    <h2>修改密码</h2>
    <el-form ref="passwordFormRef" label-position="right" label-width="120px" :model="passwordForm"
      :rules="passwordRules">
      <el-form-item label="当前密码" prop="oldPassword">
        <el-input v-model="passwordForm.oldPassword" type="password" show-password />
      </el-form-item>
      <el-form-item label="新密码" prop="newPassword">
        <el-input v-model="passwordForm.newPassword" type="password" show-password />
      </el-form-item>
      <el-form-item label="确认新密码" prop="confirmPassword">
        <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
      </el-form-item>
      <el-form-item>
        <!-- 新增字段完整性校验 -->
        <el-button type="primary" @click="submitPassword" :disabled="hasEmptyFields">修改密码</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { reactive, ref, computed } from 'vue'
import { ElMessage } from 'element-plus'

// 表单数据
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 表单引用
const passwordFormRef = ref()

// 新增字段完整性校验
const hasEmptyFields = computed(() => {
  return !passwordForm.oldPassword ||
    !passwordForm.newPassword ||
    !passwordForm.confirmPassword
})

// 增强密码验证规则
const passwordRules = {
  oldPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在6到20个字符', trigger: 'blur' },
    {
      pattern: /^(?=.*[A-Za-z])(?=.*\d).{6,20}$/,
      message: '密码必须包含字母和数字',
      trigger: 'blur'
    }
  ],
  confirmPassword: [
    { validator: validateConfirmPass, trigger: 'blur' }
  ]
}

// 确认密码验证函数
function validateConfirmPass(rule, value, callback) {
  if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

// 提交表单
async function submitPassword() {
  try {
    // 严格验证表单
    const valid = await passwordFormRef.value.validate()
    if (!valid) return

    // 发送请求
    const response = await fetch('http://localhost:8000/update_password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        old_password: passwordForm.oldPassword,
        new_password: passwordForm.newPassword
      }),
    })

    const data = await response.json()

    if (response.ok) {
      ElMessage.success('密码修改成功')
      // 清空表单
      passwordForm.oldPassword = ''
      passwordForm.newPassword = ''
      passwordForm.confirmPassword = ''
    } else {
      // 错误处理
      switch (response.status) {
        case 401:
          ElMessage.error('原密码验证失败')
          break
        case 500:
          ElMessage.error(data.detail || '密码更新失败')
          break
        default:
          ElMessage.error('未知错误')
      }
    }
  } catch (error) {
    ElMessage.error('网络错误，请检查服务器是否运行')
    console.error('Error:', error)
  }
}
</script>

<style scoped>
.settings-card {
  background: #fff;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}
</style>