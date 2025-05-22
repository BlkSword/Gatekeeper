<template>
  <div class="container">
    <el-scrollbar>
      <!-- 头部导航 -->
      <div class="header">
        <el-row type="flex" justify="space-between" align="middle" :gutter="20">
          <!-- 左侧按钮组 -->
          <el-col :span="6">
            <el-button-group class="tab-buttons">
              <el-button :class="{ active: currentTab === 'baseline' }" @click="switchTab('baseline')">
                基线状态
              </el-button>
              <el-button :class="{ active: currentTab === 'host' }" @click="switchTab('host')">
                主机状态
              </el-button>
            </el-button-group>
          </el-col>

          <!-- 退出登录按钮 -->
          <el-col :span="18">
            <div class="logout-container">
              <el-button type="danger" @click="logout">退出登录</el-button>
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

<script setup>
import { ref, shallowRef, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'
import HomeBaseline from './Home/Home_Baseline.vue'
import HomeHost from './Home/Home_Host.vue'

const router = useRouter()
const authStore = useAuthStore()

const currentTab = ref('baseline')
const currentComponent = shallowRef(HomeBaseline)

const isAdmin = computed(() => authStore.isAdmin)
const switchTab = (tab) => {
  currentTab.value = tab
  currentComponent.value = tab === 'baseline' ? HomeBaseline : HomeHost
}

const logout = () => {
  authStore.clearAuth()
  router.push('/login')
}
</script>

<style scoped src="../assets/css/HomeView.css"></style>