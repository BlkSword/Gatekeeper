<script setup>
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';


const router = useRouter();
const route = useRoute();

const currentRoute = computed(() => route.path);

const handleMenuSelect = (index) => {
  
  router.push(index);
};
</script>

<template>
  <div class="common-layout">
    <el-container>
      <el-aside width="250px">
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
          <el-menu-item index="/"><el-icon><House /></el-icon>首页</el-menu-item>
          <el-menu-item index="/check"><el-icon><Aim /></el-icon>检测</el-menu-item>
          <el-menu-item index="/settings"><el-icon><Setting /></el-icon>设置</el-menu-item>
        </el-menu>
      </el-aside>

      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

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
.el-container {
  height: 100%;
}

/* 侧边栏样式 */
.el-aside {
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
  border-bottom: 1px solid #e4e7ed;
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
.el-menu {
  border-right: none;
  flex-grow: 1;
  background-color: transparent;
  overflow: hidden;
  padding: 10px 10px 10px 10px;
}

/* 菜单项基础样式 */
.el-menu-item {
  color: #000;
  font-size: 16px;
  padding: 0 20px;
  border-radius: 8px;
  transition: all 0.3s ease;
  margin: 10px 10px 0 10px;
}

/* 激活菜单项样式 */
.el-menu-item.is-active {
  background-color: #409EFF;
  color: #fff;
  position: relative;
  border-radius: 8px;
}


/* 菜单项悬停效果 */
.el-menu-item:hover {
  background-color: #ecf5ff;
  color: #409EFF;
  border-radius: 8px;
}

/* 主内容区域样式 */
.el-main {
  /* background-color: #E9EEF3; */
  /* color: #333; */
  text-align: center;
  line-height: 160px;
}
</style>