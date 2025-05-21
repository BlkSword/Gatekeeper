<template>
  <div class="login-container">
    <el-card class="login-card">
      <div class="login-header">
        <div class="login-title-left">登录</div>
        <div class="login-title-right">Gatekeeper</div>
      </div>
      <el-form
        ref="loginForm"
        :model="form"
        :rules="rules"
        label-width="0px"
        class="login-form"
      >
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" autocomplete="off" />
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
          <el-button type="primary" style="width: 100%;" @click="validateForm">
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

const validateForm = async () => {
  try {
    await loginForm.value.validate();
    handleLogin();
  } catch (err) {
    console.warn('表单验证失败，无法提交');
  }
};

const handleLogin = () => {
  if (form.value.username === 'admin' && form.value.password === '123456') {
    localStorage.setItem('token', 'mock-token');
    ElMessage.success({
      message: '登录成功',
      duration: 2000,
      position: 'top' 
    });
    router.push('/');
  } else {
    ElMessage.error({
      message: '用户名或密码错误',
      duration: 2000,
      position: 'top' 
    });
  }
};
</script>

<style scoped src="../assets/css/Login.css"></style>