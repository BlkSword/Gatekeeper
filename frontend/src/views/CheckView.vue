<template>
  <div class="full-container">
    <!-- 页眉区域 -->
    <el-scrollbar style="height: 100vh;">
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
            <p style="font-size: 1.5rem;">已完成安全扫描，已检测到 <span class="risk-highlight">{{ riskCount }}</span> 个风险</p>
            <p style="color:dimgray">上次扫描时间：{{ lastScanTime }}</p>
          </div>
          <div style="margin-right: 3rem; align-self: center;">
            <span 
              class="fix-link" 
              @click="handleFixSelected"
              :class="{ 'disabled': !hasSelected }"
              v-show="selectedCount > 0"
            >修复选中项</span>
            <button class="scan-button" @click="startScan">立即扫描</button>
          </div>
        </div>

        <!-- 风险列表 -->
          <div class="risk-list">
            <div class="risk-header">
              <label>
                <input type="checkbox" v-model="selectAll" @change="toggleAllSelection">
                <span class="cleckbox-label">全选</span>
              </label>
            </div>
            <div v-for="(risk, index) in risks" :key="index" class="risk-item">
              <div class="risk-checkbox">
                <input type="checkbox" v-model="risk.selected">
              </div>
              <div class="risk-details">
                <div class="risk-header">
                  <span class="risk-level" 
                    :style="{
                      backgroundColor: riskColors[risk.level]?.bg || '#f5f5f5',
                      color: riskColors[risk.level]?.text || '#8c8c8c'
                    }"
                  >{{ risk.level }}</span>
                  <span class="risk-title">{{ risk.title }}</span>
                </div>
              </div>
              <div class="risk-actions">
                <button class="risk-button" @click="handleAction(index, '修复')">修复</button>
                <button class="risk-button" @click="handleAction(index, '忽略')">忽略</button>
                <button class="risk-button" @click="handleAction(index, '详情')">详情</button>
              </div>
            </div>
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

export default {
  data() {
    return {
      score: 66,
      riskCount: 13,
      lastScanTime: '2025-05-20 22:24:07',
      selectAll: false,
      showReportDialog: false,    
      showRuleDialog: false,     
      chartInstance: null,
      riskColors: {
        高危: { bg: '#fff0f0', text: '#ff4d4f' },    
        中危: { bg: '#fff7e6', text: '#ffa940' },  
        低危: { bg: '#edefd0', text: '#b8bf40' }      
      },
      showDetails: false,
      selectedRisk: {},
      risks: [
        { 
          title: '检测是否开启系统防火墙', 
          level: '高危',
          description: '系统未启用防火墙可能导致网络攻击风险',
          solution: '请执行ufw enable命令启用防火墙',
          tip: '建议定期检查防火墙规则有效性',
          selected: false 
        },
        { 
          title: '检测是否使用安全的套接字层加密', 
          level: '中危',
          description: '未使用SSL/TLS加密可能导致数据泄露',
          solution: '配置服务器强制使用TLS 1.2及以上版本',
          tip: '定期更新SSL证书',
          selected: false 
        },
        { 
          title: '检查是否设置无操作超时退出', 
          level: '低危',
          description: '会话超时设置过长可能导致安全风险',
          solution: '建议设置超时时间为15分钟',
          tip: '需结合业务需求调整',
          selected: false 
        },
        { 
          title: '是否限制核心转储', 
          level: '中危',
          description: '核心转储可能包含敏感信息',
          solution: '通过ulimit -c 0禁用核心转储',
          tip: '需确认应用程序调试需求',
          selected: false 
        },
        { 
          title: 'SSH 登录超时配置检测', 
          level: '高危',
          description: 'SSH登录超时设置过长可能导致暴力破解',
          solution: '在sshd_config中设置LoginGraceTime为60',
          tip: '建议配合fail2ban使用',
          selected: false 
        },
        { 
          title: '检查SSH密码修改最小间隔', 
          level: '中危',
          description: '密码修改间隔过短可能导致密码策略失效',
          solution: '设置PASS_MIN_DAYS为7',
          tip: '需结合企业安全策略',
          selected: false 
        }
      ]
    }
  },
  computed: {
    selectedCount() {
      return this.risks.filter(risk => risk.selected).length;
    }
  },
  hasSelected() {
    return this.selectedCount > 0;
  },
  mounted() {
    this.initChart();
    window.addEventListener('resize', this.resizeHandler);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.resizeHandler);
    if (this.chartInstance) {
      this.chartInstance.dispose();
    }
  },
  methods: {
    startScan() {
      console.log('开始新的安全扫描');
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
      if (action === '详情') {
        this.showDetails = true;
        this.selectedRisk = this.risks[riskIndex];
      } else {
        console.log(`处理风险 ${riskIndex} 的操作：${action}`);
      }
    },
    toggleAllSelection() {
      this.risks.forEach(risk => {
        risk.selected = this.selectAll;
      });
    },
    initChart() {
      const chartDom = this.$refs.chartContainer;
      this.chartInstance = echarts.init(chartDom);
      
      const getScoreColor = (score) => {
        const r = Math.round(255 * (1 - score/100));
        const g = Math.round(255 * (score/100));
        return `rgb(${r},${g},0)`;
      };
      
      const option = {
        graphic: {
          elements: [{
            type: 'text',
            key: 'scoreText',
            style: {
              text: `${this.score}`,
              fontSize: 40,
              fontWeight: 'bold',
              fill: getScoreColor(this.score),
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
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          },
          data: [{
            value: this.score,
            name: '得分',
            itemStyle: {
              color: getScoreColor(this.score)
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
      const option = this.chartInstance.getOption();
      const newColor = this.getScoreColor(this.score);
      
      option.series[0].data[0].itemStyle.color = newColor;
      option.graphic.elements[0].style.fill = newColor;
      option.graphic.elements[0].style.text = this.score;
      
      this.chartInstance.setOption(option);
    },
    getScoreColor(score) {
      const r = Math.round(255 * (1 - score/100));
      const g = Math.round(255 * (score/100));
      return `rgb(${r},${g},0)`;
    },
    resizeHandler() {
      if (this.chartInstance) {
        this.chartInstance.resize();
      }
    },
    closeModal() {
      this.showDetails = false;
    }
  },
  watch: {
    score(newVal, oldVal) {
      if (this.chartInstance && newVal !== oldVal) {
        this.updateChartColor();
      }
    }
  }
}
</script>

<style scoped src="../assets/css/CheckView.css"></style>