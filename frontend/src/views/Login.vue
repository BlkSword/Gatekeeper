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

<style scoped>
/* 登录页面整体容器样式 */
.login-container {
  height: 95vh;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 登录卡片主体样式 */
.login-card {
  width: 25%;
  padding: 30px;
  box-shadow: 0 2px 15px rgba(0, 0, 0, 0.1);
  background-color: #fff;
  text-align: center;
  display: flex;
  flex-direction: column;
  justify-content: center;
  height: auto;
}

/* 头部标题区域布局 */
.login-header {
  margin-bottom: 50px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 左侧标题样式 */
.login-title-left {
  font-size: 20px;
  color: #626161;
}

/* 右侧产品名称样式 */
.login-title-right {
  font-size: 20px;
  color: #409EFF;
  font-weight: bold;
}

/* 表单区域样式 */
.login-form .el-form-item {
  margin-bottom: 20px;
}

.login-form .el-input {
  width: 100%;
}

/* 底部链接区域样式 */
.login-links {
  margin-top: 10px;
  font-size: 12px;
  text-align: right;
}

/* 链接文本样式 */
.link-right {
  color: #409eff;
  text-decoration: none;
}

/* 链接悬停效果 */
.link-right:hover {
  text-decoration: underline;
}
</style>