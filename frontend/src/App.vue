<template>
  <div class="common-layout layout-container">
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

import './assets/css/Layout.css'


const router = useRouter();
const route = useRoute();

const currentRoute = computed(() => route.path);

const handleMenuSelect = (index) => {
  router.push(index);
};
</script>