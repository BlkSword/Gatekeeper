<template>
  <div class="common-layout">
    <el-container>
      <!-- 响应式侧边栏 -->
      <el-aside v-if="isLoggedIn" width="250px">
        <!-- 顶部导航栏 -->
        <div class="top-bar">
          <div class="left-section">
            <img src="/src/assets/Gatekeeper.svg" alt="Logo" class="logo" />
            <span class="safe-text">Gatekeeper</span>
          </div>
        </div>

        <!-- 导航菜单 -->
        <el-menu :default-active="currentRoute" @select="handleMenuSelect" unique-opened>
          <el-menu-item index="/home">
            <el-icon>
              <House />
            </el-icon>
            <span class="icon-text-gap"></span>首页
          </el-menu-item>

          <el-menu-item index="/check">
            <el-icon>
              <Aim />
            </el-icon>
            <span class="icon-text-gap"></span>检测
          </el-menu-item>

          <el-sub-menu index="/settings" popper-append-to-body>
            <template #title>
              <el-icon>
                <Setting />
              </el-icon>
              <span class="icon-text-gap"></span>设置
            </template>
            <el-menu-item index="/settings/threshold">阈值设置</el-menu-item>
            <el-menu-item index="/settings/password">密码修改</el-menu-item>
            <el-menu-item index="/settings/alert">告警设置</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-aside>

      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { House, Aim, Setting } from '@element-plus/icons-vue'
import { useAuthStore } from './stores/authStore'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const isLoggedIn = computed(() => authStore.token !== null)

const currentRoute = computed(() => route.path)
const handleMenuSelect = (index) => router.push(index)
</script>

<style scoped src="./assets/css/App.css"></style>