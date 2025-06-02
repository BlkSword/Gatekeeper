<template>
  <div class="full-container">
    <el-scrollbar style="height: 100vh;">
      <!-- 页眉区域保持不变 -->
      <header class="header">
        <div class="button-group">
          <button class="blue-button" @click="showReportDialog = true">查看报告</button>
          <button class="blue-button" @click="showRuleDialog = true">自定义规则</button>
        </div>
        <!-- 查看报告弹窗 -->
        <div v-if="showReportDialog" class="custom-modal">
          <div class="modal-content">
            <div class="modal-header">
              <span class="modal-title">查看报告</span>
              <span class="modal-close" @click="showReportDialog = false">&times;</span>
            </div>
            <div class="modal-body">
              <div class="svg-container"></div>
              <p class="no-content">暂无内容</p>
            </div>
          </div>
        </div>
        <!-- 自定义规则弹窗 -->
        <div v-if="showRuleDialog" class="custom-modal">
          <div class="modal-content">
            <div class="modal-header">
              <span class="modal-title">自定义规则</span>
              <span class="modal-close" @click="showRuleDialog = false">&times;</span>
            </div>
            <div class="modal-body">
              <div class="svg-container"></div>
              <p class="no-content">暂无内容</p>
            </div>
          </div>
        </div>
      </header>
      <!-- 主要内容区域 -->
      <main class="main-content">
        <!-- 安全评分区域 -->
        <div class="score-card">
          <div class="score-circle" ref="chartContainer" style="margin-left: 3rem;"></div>
          <div class="scan-info" style="margin-left: 3rem;">
            <p style="font-size: 1.5rem;">
              {{ scanStatusText }}
            </p>
            <p style="color:dimgray">{{ scanTimeText }}</p>
          </div>
          <div style="margin-right: 3rem; align-self: center;">
            <span class="fix-link" @click="handleFixSelected" :class="{ 'disabled': selectedCount === 0 }"
              v-show="selectedCount > 0">修复选中项</span>
            <button class="scan-button" @click="startScan" :disabled="isLoading">
              {{ isLoading ? '扫描中...' : '立即检查' }}
            </button>
          </div>
        </div>
        <!-- 风险列表 -->
        <div class="risk-list">
          <div class="risk-header">
            <label>
              <input type="checkbox" v-model="selectAll">
              <span class="cleckbox-label">全选</span>
            </label>
          </div>
          <!-- 空状态提示 -->
          <div v-if="risks.length === 0 && !isLoading" class="empty-state">
            暂无风险数据，请先进行安全检查
          </div>
          <div v-else-if="isLoading" class="empty-state">
            <div class="loading-spinner"></div>
            正在扫描中...
          </div>
          <!-- 使用 transition 包裹风险项 -->
          <transition-group name="fade">
            <div v-for="(risk, index) in risks" :key="risk.title" class="risk-item" v-show="!risk.ignored">
              <div class="risk-checkbox">
                <input type="checkbox" v-model="risk.selected" :disabled="!isScanned">
              </div>
              <div class="risk-details">
                <div class="risk-header">
                  <span class="risk-level" :style="{
                    backgroundColor: riskColors[risk.level]?.bg || '#f5f5f5',
                    color: riskColors[risk.level]?.text || '#8c8c8c'
                  }">{{ risk.level }}</span>
                  <span class="risk-title">{{ risk.title }}</span>
                </div>
              </div>
              <div class="risk-actions">
                <button class="risk-button" @click="handleAction(index, '修复')" :disabled="!isScanned">修复</button>
                <button class="risk-button" @click="handleAction(index, '忽略')" :disabled="!isScanned">忽略</button>
                <button class="risk-button" @click="handleAction(index, '详情')" :disabled="!isScanned">详情</button>
              </div>
            </div>
          </transition-group>
        </div>
      </main>
      <!-- 风险详情弹窗 -->
      <div v-if="showDetails" class="details-modal">
        <div class="modal-content">
          <div class="modal-header">
            <span class="modal-title">风险详情</span>
            <span class="modal-close" @click="closeModal">&times;</span>
          </div>
          <div class="modal-body">
            <div class="detail-section">
              <label>风险描述</label>
              <div class="detail-content">{{ selectedRisk.description }}</div>
            </div>
            <div class="detail-section">
              <label>解决方案</label>
              <div class="detail-content">{{ selectedRisk.solution }}</div>
            </div>
            <div class="detail-section">
              <label>温馨提示</label>
              <div class="detail-content">{{ selectedRisk.tip }}</div>
            </div>
          </div>
        </div>
      </div>
    </el-scrollbar>
  </div>
</template>
<script>
import * as echarts from 'echarts';
import axios from 'axios';

// 缓存键名
const SCAN_CACHE_KEY = 'security_scan_cache';
// 缓存有效期（毫秒），设置为24小时
const CACHE_EXPIRATION = 24 * 60 * 60 * 1000;

export default {
  data() {
    return {
      score: 0,
      riskCount: 0,
      lastScanTime: '',
      showReportDialog: false,
      showRuleDialog: false,
      chartInstance: null,
      isScanned: false,
      isLoading: false,
      taskId: null,
      pollingInterval: null,
      riskColors: {
        高危: { bg: '#fff0f0', text: '#ff4d4f' },
        中危: { bg: '#fff7e6', text: '#ffa940' },
        低危: { bg: '#edefd0', text: '#b8bf40' },
        未检测: { bg: '#f5f5f5', text: '#8c8c8c' }
      },
      showDetails: false,
      selectedRisk: {},
      risks: [],
      rules: [],
      totalItems: 0,
      compliantCount: 0,
      nonCompliantCount: 0,
      // 添加缓存相关数据
      hasCachedData: false
    };
  },
  computed: {
    selectedCount() {
      return this.risks.filter(risk => risk.selected).length;
    },
    scanStatusText() {
      return this.isScanned
        ? `已完成安全检查，已检测到${this.riskCount} 个风险`
        : '尚未进行安全检查';
    },
    scanTimeText() {
      return this.isScanned
        ? `上次检查时间：${this.lastScanTime}`
        : '点击右侧按钮开始首次检查';
    },
    selectAll: {
      get() {
        if (this.risks.length === 0) return false;
        return this.risks.every(risk => risk.selected);
      },
      set(newSelection) {
        this.risks.forEach(risk => {
          risk.selected = newSelection;
        });
      }
    }
  },
  mounted() {
    this.loadCachedData(); // 优先加载缓存数据
    this.initChart();
    window.addEventListener('resize', this.resizeHandler);
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.resizeHandler);
    if (this.chartInstance) {
      this.chartInstance.dispose();
      this.chartInstance = null;
    }
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
    }
  },
  methods: {
    // 加载缓存数据
    loadCachedData() {
      try {
        const cache = localStorage.getItem(SCAN_CACHE_KEY);
        if (cache) {
          const { timestamp, data } = JSON.parse(cache);
          // 检查缓存是否过期
          if (Date.now() - timestamp < CACHE_EXPIRATION) {
            this.applyCachedData(data);
            this.hasCachedData = true;
            return true;
          }
        }
      } catch (error) {
        console.error('加载缓存失败:', error);
      }
      return false;
    },
    // 应用缓存数据
    applyCachedData(data) {
      this.score = data.score || 0;
      this.riskCount = data.riskCount || 0;
      this.risks = data.risks || [];
      this.lastScanTime = data.lastScanTime || '';
      this.isScanned = true;
      this.$nextTick(() => {
        this.initChart();
      });
    },
    // 保存缓存数据
    saveCachedData() {
      const cacheData = {
        score: this.score,
        riskCount: this.riskCount,
        risks: this.risks,
        lastScanTime: this.lastScanTime
      };
      localStorage.setItem(SCAN_CACHE_KEY, JSON.stringify({
        timestamp: Date.now(),
        data: cacheData
      }));
    },
    async startScan() {
      if (this.isLoading) return;

      // 如果已有缓存数据且不是强制刷新，直接使用缓存
      if (this.hasCachedData && !confirm('是否重新扫描以获取最新数据？')) {
        return;
      }

      this.isLoading = true;
      this.isScanned = false;
      this.risks = [];
      this.hasCachedData = false;

      try {
        // 清除旧缓存
        localStorage.removeItem(SCAN_CACHE_KEY);

        // 启动扫描任务
        const taskResponse = await axios.post('http://127.0.0.1:8000/scan');
        this.taskId = taskResponse.data.task_id;

        // 获取规则列表
        const rulesResponse = await axios.get('http://127.0.0.1:8000/rules');
        this.rules = rulesResponse.data;

        // 开始轮询进度
        this.pollingInterval = setInterval(async () => {
          try {
            const progressResponse = await axios.get(`http://127.0.0.1:8000/scan/${this.taskId}/progress`);
            if (progressResponse.data.status === 'completed') {
              clearInterval(this.pollingInterval);
              this.pollingInterval = null;

              // 更新进度数据
              this.totalItems = progressResponse.data.total;
              this.compliantCount = progressResponse.data.compliant_count;
              this.nonCompliantCount = progressResponse.data.non_compliant_count;

              // 计算得分
              this.score = Math.round((this.compliantCount / this.totalItems) * 100);

              // 获取扫描结果
              const resultsResponse = await axios.get(`http://127.0.0.1:8000/scan/${this.taskId}/results`);

              // 处理非合规结果
              const nonCompliantResults = resultsResponse.data.filter(item => !item.compliant);

              // 匹配规则信息生成风险列表
              this.risks = nonCompliantResults.map(result => {
                const rule = this.rules.find(r => r.name === result.rule_name);
                return {
                  title: rule?.description || result.rule_name,
                  level: this.formatSeverityLevel(rule?.severity_level),
                  description: rule?.risk_description || '暂无描述',
                  solution: rule?.solution || '暂无解决方案',
                  tip: rule?.tip || '暂无提示',
                  selected: false,
                  ignored: false
                };
              });

              this.riskCount = this.risks.length;
              this.lastScanTime = new Date().toLocaleString();
              this.isScanned = true;
              this.isLoading = false;

              // 保存缓存
              this.saveCachedData();

              this.$nextTick(() => {
                this.initChart();
              });
            }
          } catch (error) {
            console.error('轮询进度失败:', error);
            this.handleError('扫描过程中发生错误');
          }
        }, 2000); // 每2秒轮询一次
      } catch (error) {
        console.error('启动扫描任务失败:', error);
        this.handleError('无法启动扫描任务');
      }
    },
    formatSeverityLevel(level) {
      switch (level) {
        case 'high': return '高危';
        case 'medium': return '中危';
        case 'low': return '低危';
        default: return '未检测';
      }
    },
    handleFixSelected() {
      if (this.selectedCount) {
        this.risks
          .filter(risk => risk.selected)
          .forEach((risk, index) => {
            this.handleAction(index, '修复');
          });
      }
    },
    handleAction(riskIndex, action) {
      const risk = this.risks[riskIndex];
      if (action === '详情') {
        this.showDetails = true;
        this.selectedRisk = { ...risk };
      } else if (action === '忽略') {
        risk.ignored = true;
      } else {
        console.log(`处理风险 ${riskIndex} 的操作：${action}`);
      }
    },
    initChart() {
      const chartDom = this.$refs.chartContainer;
      if (!chartDom) return;
      if (this.chartInstance) {
        this.chartInstance.dispose();
      }
      this.chartInstance = echarts.init(chartDom);
      const option = {
        graphic: {
          elements: [{
            type: 'text',
            key: 'scoreText',
            style: {
              text: this.isScanned ? `${this.score}` : '0',
              fontSize: 40,
              fontWeight: 'bold',
              fill: this.getScoreColor(this.score),
              textAlign: 'center',
              textVerticalAlign: 'middle'
            },
            left: 'center',
            top: 'middle'
          }]
        },
        series: [{
          type: 'pie',
          radius: ['80%', '90%'],
          itemStyle: {
            borderRadius: 5,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: false
          },
          data: [{
            value: this.score,
            name: '得分',
            itemStyle: {
              color: this.getScoreColor(this.score)
            }
          }, {
            value: 100 - this.score,
            name: '剩余',
            itemStyle: {
              color: '#e6e6e6'
            }
          }]
        }]
      };
      this.chartInstance.setOption(option);
    },
    updateChartColor() {
      if (!this.chartInstance) return;
      const newColor = this.getScoreColor(this.score);
      const option = {
        graphic: {
          elements: [{
            style: {
              fill: newColor,
              text: `${this.score}`
            }
          }]
        },
        series: [{
          data: [{
            itemStyle: {
              color: newColor
            }
          }]
        }]
      };
      this.chartInstance.setOption(option);
    },
    getScoreColor(score) {
      const r = Math.round(255 * (1 - score / 100));
      const g = Math.round(255 * (score / 100));
      return `rgb(${r},${g},0)`;
    },
    resizeHandler() {
      if (this.chartInstance) {
        this.chartInstance.resize();
      }
    },
    closeModal() {
      this.showDetails = false;
    },
    handleError(message) {
      this.isLoading = false;
      this.isScanned = false;
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
      alert(message);
    }
  },
  watch: {
    score(newVal, oldVal) {
      if (this.chartInstance && newVal !== oldVal) {
        this.updateChartColor();
      }
    }
  }
};
</script>
<style scoped src="../assets/css/CheckView.css"></style>
<!-- 添加的动画样式 -->
<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease, transform 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

.loading-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid #fff;
  border-radius: 50%;
  border-top-color: transparent;
  animation: spin 1s linear infinite;
  margin-right: 8px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>