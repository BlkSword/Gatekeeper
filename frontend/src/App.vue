<template>
  <div class="common-layout">
    <el-container>
      <el-aside v-if="isLoggedIn" width="250px">
        <!-- 顶部导航栏区域 -->
        <div class="top-bar">
          <div class="left-section">
            <img src="/src/assets/Gatekeeper.svg" alt="Logo" class="logo" />
            <span class="safe-text">Gatekeeper</span>
          </div>
          <div class="notifications">0</div>
        </div>

        <!-- 左侧菜单导航 -->
        <el-menu 
          :default-active="currentRoute"  
          @select="handleMenuSelect"       
        >
          <el-menu-item index="/">
            <el-icon><House /></el-icon>
            <span class="icon-text-gap"></span>
            首页
          </el-menu-item>
          <el-menu-item index="/check">
            <el-icon><Aim /></el-icon>
            <span class="icon-text-gap"></span>
            检测
          </el-menu-item>
          <el-menu-item index="/settings">
            <el-icon><Setting /></el-icon>
            <span class="icon-text-gap"></span>
            设置
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();

// 计算属性：判断是否已登录
const isLoggedIn = computed(() => {
  return localStorage.getItem('token') !== null;
});

const currentRoute = computed(() => route.path);

const handleMenuSelect = (index) => {
  router.push(index);
};
</script>

<style scoped>
/* 全局布局容器 */
.common-layout {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
}

/* element-ui 容器全屏设置 */
:deep(.el-container) {
  height: 100%;
}

/* 侧边栏样式 */
:deep(.el-aside) {
  background-color: transparent;
  color: #333;
  text-align: left;
  display: flex;
  flex-direction: column;
}

/* 顶部导航栏样式 */
.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 27px;
}

/* Logo和系统名称容器 */
.left-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* Logo图片尺寸控制 */
.logo {
  width: 30px;
  height: 30px;
}

/* 系统名称文本样式 */
.safe-text {
  font-size: 18px;
  color: #333;
  font-weight: 600;
}

/* 通知消息样式 */
.notifications {
  background-color: #bc2626;
  color: #fff;
  padding: 5px 5px;
  border-radius: 4px;
  font-size: 14px;
  min-width: 24px;
  text-align: center;
}

/* 菜单样式 */
:deep(.el-menu) {
  border-right: none;
  flex-grow: 1;
  background-color: transparent;
  overflow: hidden;
  padding: 10px 10px 10px 10px;
}

/* 菜单项基础样式 */
:deep(.el-menu-item) {
  color: #000;
  font-size: 16px;
  padding: 0 20px;
  border-radius: 8px;
  transition: all 0.3s ease;
  margin: 10px 10px 0 10px;
}

/* 活跃菜单项样式 */
:deep(.el-menu-item.is-active) {
  background-color: #409EFF;
  color: #fff;
  position: relative;
  border-radius: 8px;
  box-shadow: 0 12px 8px -3px rgba(204, 240, 255, 0.5);
}

/* 菜单项悬停效果 */
:deep(.el-menu-item:hover) {
  background-color: #ecf5ff;
  color: #409EFF;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

/* 主内容区域样式 */
:deep(.el-main) {
  text-align: center;
  line-height: 100%;
}

/* 图标与文字间距 */
.icon-text-gap {
  margin-left: 8px;
}

html,
body {
  height: 100%;
  margin: 0;
}

#app {
  height: 100%;
  display: flex;
  flex-direction: column;
}
</style>