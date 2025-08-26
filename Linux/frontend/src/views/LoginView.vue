<template>
  <div class="login-container">
    <el-card class="login-card">
      <div class="login-header">
        <div class="login-title-left">登录</div>
        <div class="login-title-right">Gatekeeper</div>
      </div>
      <el-form ref="loginForm" :model="form" :rules="rules" label-width="0px" class="login-form">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" autocomplete="off" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input type="password" v-model="form.password" placeholder="密码" autocomplete="off" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" style="width: 100%;" @click="validateForm">
            登录
          </el-button>
        </el-form-item>
        <div class="login-links">
          <el-popover placement="bottom" :width="375" trigger="hover">
            <template #default>
              <div class="popover-content">在@/backend/database/config.json中修改账号密码</div>
            </template>
            <template #reference>
              <a href="#" class="link-right">忘记密码？</a>
            </template>
          </el-popover>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/authStore.ts'

const authStore = useAuthStore()
const router = useRouter()
const loginForm = ref(null)
const loginAttempts = ref(0);
const lockoutTime = ref(null);

const form = ref({
  username: '',
  password: ''
})

const rules = ref({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
})

const validateForm = async () => {
  const now = Date.now();
  if (lockoutTime.value && now < lockoutTime.value) {
    ElMessage.warning({
      message: `登录已被锁定，请于 ${Math.ceil((lockoutTime.value - now) / 1000)} 秒后重试`,
      duration: 2000,
      position: 'top'
    });
    return;
  }

  try {
    await loginForm.value.validate();
    handleLogin();
  } catch (err) {
    console.warn('表单验证失败，无法提交');
  }
};

const handleLogin = async () => {
  try {
    const response = await fetch('http://127.0.0.1:8000/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username: form.value.username,
        password: form.value.password
      })
    });

    const data = await response.json();

    if (response.status === 200) {
      authStore.setAuth(data.token, true);
      ElMessage.success({
        message: '登录成功',
        duration: 2000,
        position: 'top'
      });
      router.push('/home');
      loginAttempts.value = 0;
    } else if (response.status === 401) {
      ElMessage.error({
        message: '用户名或密码错误',
        duration: 2000,
        position: 'top'
      });
      loginAttempts.value += 1;
      if (loginAttempts.value >= 5) {
        lockoutTime.value = Date.now() + 180000; // 3分钟封禁
        ElMessage.error({
          message: '连续5次失败，登录已锁定3分钟',
          duration: 2000,
          position: 'top'
        });
      }
    } else {
      ElMessage.error({
        message: data.detail || '登录失败',
        duration: 2000,
        position: 'top'
      });
      loginAttempts.value += 1;
      if (loginAttempts.value >= 5) {
        lockoutTime.value = Date.now() + 180000;
        ElMessage.error({
          message: '连续5次失败，登录已锁定3分钟',
          duration: 2000,
          position: 'top'
        });
      }
    }
  } catch (error) {
    ElMessage.error({
      message: '请求失败，请检查网络',
      duration: 2000,
      position: 'top'
    });
    console.error('登录错误:', error);
    loginAttempts.value += 1;
    if (loginAttempts.value >= 5) {
      lockoutTime.value = Date.now() + 180000;
      ElMessage.error({
        message: '连续5次失败，登录已锁定3分钟',
        duration: 2000,
        position: 'top'
      });
    }
  }
};
</script>

<style scoped src="../assets/css/Login.css"></style>