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
          <!-- 右侧按钮 -->
          <el-col :span="18">
            <div class="logout-container">
              <el-button type="primary" @click="openRuleDrawer">规则总览</el-button>
              <el-button type="primary" @click="goToCheck">立即检测</el-button>
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
    <el-drawer v-model="isDrawerVisible" title="规则总览" direction="rtl" size="60%" :append-to-body="true">
      <div class="rule-content">
        <div v-if="loadingRules" class="loading-container">
          <el-skeleton :rows="6" animated />
        </div>
        <div v-else>
          <el-collapse v-model="activeRule" accordion>
            <el-collapse-item v-for="rule in rules" :key="rule.id" :name="rule.id">
              <template #title>
                <div class="rule-header">
                  <span class="rule-name">{{ rule.name }}</span>
                  <el-tag :type="getRuleTypeTag(rule.rule_type)" size="small">
                    {{ rule.rule_type }}
                  </el-tag>
                  <el-tag :type="getSeverityTag(rule.severity_level)" size="small">
                    {{ rule.severity_level }}
                  </el-tag>
                </div>
              </template>
              <div class="rule-details">
                <div class="rule-field">
                  <label>描述：</label>
                  <span>{{ rule.description }}</span>
                </div>
                <div class="rule-field">
                  <label>检测标准：</label>
                  <span>{{ rule.baseline_standard }}</span>
                </div>
                <div class="rule-field">
                  <label>风险描述：</label>
                  <span>{{ rule.risk_description }}</span>
                </div>
                <div class="rule-field">
                  <label>解决方案：</label>
                  <span v-html="formatSolution(rule.solution)"></span>
                </div>
                <div class="rule-field">
                  <label>提示：</label>
                  <span>{{ rule.tip }}</span>
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, shallowRef, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'
import axios from 'axios'
import HomeBaseline from './Home/Home_Baseline.vue'
import HomeHost from './Home/Home_Host.vue'

const router = useRouter()
const authStore = useAuthStore()

// 当前激活标签页
const currentTab = ref('baseline')
const currentComponent = shallowRef(HomeBaseline)

// 抽屉相关状态
const isDrawerVisible = ref(false)
const loadingRules = ref(false)
const rules = ref([])
const activeRule = ref('')
const fetchError = ref(null)

// 获取规则数据
const fetchRules = async () => {
  loadingRules.value = true
  fetchError.value = null

  try {
    const response = await axios.get('http://127.0.0.1:8000/rules')
    rules.value = response.data
  } catch (error) {
    fetchError.value = '规则加载失败，请稍后重试'
    console.error('获取规则失败:', error)
  } finally {
    loadingRules.value = false
  }
}

// 打开抽屉时获取规则数据
const openRuleDrawer = () => {
  isDrawerVisible.value = true
  if (!rules.value.length || !isDrawerVisible.value) {
    fetchRules()
  }
}

// 路由跳转方法
const goToCheck = () => {
  router.push('/check')
}

// 标签切换逻辑
const switchTab = (tab) => {
  currentTab.value = tab
  currentComponent.value = tab === 'baseline' ? HomeBaseline : HomeHost
}

// 登出逻辑
const logout = () => {
  authStore.clearAuth()
  router.push('/login')
}

// 辅助方法：获取标签类型
const getRuleTypeTag = (type) => {
  switch (type) {
    case 'python_script': return 'success'
    case 'system_check': return 'primary'
    default: return 'info'
  }
}

// 辅助方法：获取严重等级标签
const getSeverityTag = (level) => {
  switch (level) {
    case 'high': return 'danger'
    case 'medium': return 'warning'
    case 'low': return 'primary'
    default: return 'info'
  }
}

// 格式化解决方案中的换行
const formatSolution = (solution) => {
  return solution.replace(/\n/g, '<br>')
}
</script>

<style scoped src="../assets/css/HomeView.css"></style>

<style scoped>
.rule-content {
  padding: 20px;
}

.loading-container {
  padding: 20px;
}

.rule-header {
  display: flex;
  align-items: center;
  width: 100%;
  padding-right: 20px;
}

.rule-name {
  flex: 1;
  font-weight: bold;
  margin-right: 10px;
}

.rule-details {
  padding: 0 20px 20px;
}

.rule-field {
  margin-bottom: 15px;
}

.rule-field label {
  font-weight: bold;
  color: #666;
  display: block;
  margin-bottom: 5px;
}

.rule-field span {
  line-height: 1.6;
}

/* 折叠面板样式优化 */
:deep(.el-collapse-item__header) {
  background-color: #f9f9f9;
  border-bottom: 1px solid #eee;
}

:deep(.el-collapse-item__wrap) {
  border-bottom: none;
}
</style>