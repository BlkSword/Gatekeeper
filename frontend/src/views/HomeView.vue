<template>
  <div class="container">
    <el-scrollbar>
      <!-- 头部导航 -->
      <div class="header">
        <el-row type="flex" justify="space-between" align="middle" :gutter="20">
          <!-- 左侧按钮组 -->
          <el-col :span="6">
            <el-button-group class="tab-buttons">
              <el-button 
                :class="{ active: currentTab === 'baseline' }" 
                @click="switchTab('baseline')">
                基线状态
              </el-button>
              <el-button 
                :class="{ active: currentTab === 'host' }" 
                @click="switchTab('host')">
                主机状态
              </el-button>
            </el-button-group>
          </el-col>
          
          <!-- 右侧身份信息 -->
          <el-col :span="18">
            <div class="admin-status">
              当前身份：
              <el-tag type="success" v-if="isAdmin">管理员</el-tag>
              <el-tag type="info" v-else>普通用户</el-tag>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 动态内容区域 -->
      <div class="content-container">
        <component :is="currentComponent" />
      </div>
    </el-scrollbar>
  </div>
</template>

<style scoped>
.container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.el-scrollbar {
  flex: 1;
}

.content-container {
  padding: 20px;
  flex-grow: 1;
}
</style>

<script setup>
import { ref, shallowRef } from 'vue'
import HomeBaseline from './Home/Home_Baseline.vue'
import HomeHost from './Home/Home_Host.vue'

const currentTab = ref('baseline')
const currentComponent = shallowRef(HomeBaseline)
const isAdmin = ref(true)

const switchTab = (tab) => {
  currentTab.value = tab
  currentComponent.value = tab === 'baseline' ? HomeBaseline : HomeHost
}
</script>

<style scoped src="../assets/css/HomeView.css"></style>