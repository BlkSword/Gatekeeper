<template>
    <div class="login-container">
      <el-card class="login-card">
        <div class="login-header">
          <div class="login-title">登录</div>
          <div class="login-subtitle">Gatekeeper</div>
        </div>
        <el-form 
          ref="loginForm" 
          :model="form" 
          :rules="rules" 
          label-width="0px"
          class="login-form"
        >
          <el-form-item prop="username">
            <el-input 
              v-model="form.username" 
              placeholder="用户名" 
              autocomplete="off"
            />
          </el-form-item>
          <el-form-item prop="password">
            <el-input 
              type="password" 
              v-model="form.password" 
              placeholder="密码" 
              autocomplete="off"
            />
          </el-form-item>
          <el-form-item>
            <el-button 
              type="primary" 
              style="width: 100%;" 
              @click="handleLogin"
            >
              登录
            </el-button>
          </el-form-item>
          <div class="login-links">
            <a href="#" class="link-right">忘记密码？</a>
          </div>
        </el-form>
      </el-card>
    </div>
  </template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';

const router = useRouter();
const loginForm = ref(null);

const form = ref({
  username: '',
  password: ''
});

const rules = ref({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
});

const handleLogin = () => {
  if (form.value.username === 'admin' && form.value.password === '123456') {
    localStorage.setItem('token', 'mock-token');
    ElMessage.success({
      message: '登录成功',
      duration: 2000
    });
    router.push('/');
  } else {
    ElMessage.error({
      message: '用户名或密码错误',
      duration: 2000
    });
  }
};
</script>

<style scoped>
.login-container {
    height: 90vh;
    display: flex;
    justify-content: center;
    align-items: center;
}

.login-card {
    width: 30%;
    padding: 20px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    background-color: #fff;
    text-align: center;
    display: flex;
    flex-direction: column;
    justify-content: center;
    height: 70%;
}

.login-header {
    margin-bottom: 30px;
}

.login-title {
    font-size: 24px;
    color: #333;
    margin-bottom: 8px;
}

.login-subtitle {
    font-size: 14px;
    color: #999;
}

.login-form .el-form-item {
    margin-bottom: 20px;
}

.login-form .el-input {
    width: 100%;
}

.login-links {
    margin-top: 10px;
    font-size: 12px;
    text-align: right;
}

.link-right {
    color: #409eff;
    text-decoration: none;
}

.link-right:hover {
    text-decoration: underline;
}
</style>