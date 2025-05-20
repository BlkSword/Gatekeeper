<template>
  <div class="full-container">
    <!-- 页眉区域 -->
    <header class="header">
      <div class="button-group">
        <button class="blue-button">基线配置</button>
        <button class="blue-button">查看报告</button>
        <button class="blue-button">自定义规则</button>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <main class="main-content">
      <!-- 安全评分区域 -->
      <div class="score-card">
        <div class="score-circle" ref="chartContainer">
          <!-- 图表容器 -->
        </div>
        <div class="scan-info">
          <p style="font-size: 1.5rem;">已完成安全扫描，已检测到 <span class="risk-highlight">{{ riskCount }}</span> 个风险</p>
          <p style="color:dimgray">上次扫描时间：{{ lastScanTime }}</p>
        </div>
        <div style="margin-left: auto; align-self: center;">
          <button class="scan-button" @click="startScan">立即扫描</button>
        </div>
      </div>

      <!-- 风险列表 -->
      <div class="risk-list">
        <div class="risk-header">
          <label>
            <input type="checkbox" v-model="selectAll" @change="toggleAllSelection">
            全选
          </label>
        </div>
        <div 
          v-for="(risk, index) in risks" 
          :key="index" 
          class="risk-item"
        >
          <div class="risk-checkbox">
            <input type="checkbox" v-model="risk.selected">
          </div>
          <div class="risk-details">
            <div class="risk-header">
              <span class="risk-level">{{ risk.level }}</span>
              <span class="risk-title">{{ risk.title }}</span>
            </div>
            <div class="risk-description">
              {{ risk.description }}
            </div>
            <div class="risk-actions">
              <button 
                v-for="action in risk.actions" 
                :key="action" 
                class="risk-button"
                @click="handleAction(index, action)"
              >
                {{ action }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  data() {
    return {
      score: 50,
      riskCount: 13,
      lastScanTime: '2025-05-20 22:24:07',
      selectAll: false,
      chartInstance: null,
      risks: [
        { 
          title: '检测是否开启系统防火墙', 
          description: '检测到防火墙未正确配置', 
          actions: ['修复', '忽略', '详情'], 
          level: '中危',
          selected: false 
        },
        { 
          title: '检测是否使用安全的套接字层加密...', 
          description: 'SSL/TLS协议版本过低', 
          actions: ['修复', '忽略', '详情'], 
          level: '中危',
          selected: false 
        },
        { 
          title: '检查是否设置无操作超时退出', 
          description: '未设置会话超时时间', 
          actions: ['修复', '忽略', '详情'], 
          level: '中危',
          selected: false 
        },
        { 
          title: '是否限制核心转储', 
          description: '核心转储文件未限制大小', 
          actions: ['修复', '忽略', '详情'], 
          level: '中危',
          selected: false 
        },
        { 
          title: 'SSH 登录超时配置检测', 
          description: 'SSH登录超时时间过长', 
          actions: ['修复', '忽略', '详情'], 
          level: '中危',
          selected: false 
        },
        { 
          title: '检查SSH密码修改最小间隔', 
          description: '密码修改间隔不符合安全策略', 
          actions: ['修复', '忽略', '详情'], 
          level: '中危',
          selected: false 
        }
      ]
    }
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
    handleAction(riskIndex, action) {
      console.log(`处理风险 ${riskIndex} 的操作：${action}`);
    },
    toggleAllSelection() {
      this.risks.forEach(risk => {
        risk.selected = this.selectAll;
      });
    },
    // 初始化图表
    initChart() {
      const chartDom = this.$refs.chartContainer;
      this.chartInstance = echarts.init(chartDom);
      
      // 动态颜色计算函数
      const getScoreColor = (score) => {
        // 分数越高越绿，越低越红
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
    // 颜色更新函数
    updateChartColor() {
      const option = this.chartInstance.getOption();
      const newColor = this.getScoreColor(this.score);
      
      option.series[0].data[0].itemStyle.color = newColor;
      option.graphic.elements[0].style.fill = newColor;
      option.graphic.elements[0].style.text = this.score;
      
      this.chartInstance.setOption(option);
    },
    // 动态颜色计算函数
    getScoreColor(score) {
      const r = Math.round(255 * (1 - score/100));
      const g = Math.round(255 * (score/100));
      return `rgb(${r},${g},0)`;
    },
    // 窗口大小变化处理
    resizeHandler() {
      if (this.chartInstance) {
        this.chartInstance.resize();
      }
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

<style scoped>
.full-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
  box-sizing: border-box;
}

/* 页眉样式 */
.header {
  height: 60px;
  padding: 0 2rem;
  background-color: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  border-bottom: 1px solid #e4e7ed;
}

/* 按钮组样式 */
.button-group {
  display: flex;
  gap: 1rem;
}

/* 按钮基础样式 */
.blue-button {
  background-color: #409EFF;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

/* 按钮悬停效果 */
.blue-button:hover {
  background-color: #367fd1;
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

/* 主要内容区域 */
.main-content {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
}

/* 安全评分卡片 */
.score-card {
  display: flex;
  gap: 1rem; 
  margin-bottom: 2rem;
  background: #ffffff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

/* 评分圆环容器 */
.score-circle {
  flex: 0 0 200px; 
  height: 200px;
  position: relative;
}

/* 扫描信息 */
.scan-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  gap: 1.7rem;
}

.scan-info p {
  margin: 0;
  font-size: 1rem;
  color: #333;
}

.risk-highlight {
  color: red;
  font-weight: bold;
}

.scan-button {
  background-color: #409EFF;
  color: white;
  padding: 0.6rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.scan-button:hover {
  background-color: #367fd1;
}

/* 风险列表 */
.risk-list {
  background: #ffffff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.risk-header {
  margin-bottom: 1rem;
  font-weight: bold;
  text-align: left;
}

.risk-item {
  display: flex;
  align-items: center;
  border-bottom: 1px solid #e4e7ed;
  padding: 1.2rem 0;
}

.risk-checkbox {
  margin-right: 1rem;
}

.risk-details {
  flex: 1;
}

.risk-level {
  background: #f0f6ff;
  color: #3399ff;
  padding: 0.3rem 0.8rem;
  border-radius: 4px;
  font-size: 0.85rem;
  margin-right: 0.5rem;
}

.risk-title {
  font-size: 1.1rem;
  font-weight: 500;
  color: #1a1a1a;
}

.risk-description {
  color: #666;
  font-size: 0.95rem;
  margin: 0.5rem 0;
}

.risk-actions {
  display: flex;
  gap: 0.8rem;
}

.risk-button {
  padding: 0.4rem 1rem;
  border: 1px solid #409EFF;
  border-radius: 4px;
  background: none;
  color: #409EFF;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.3s ease;
}

.risk-button:hover {
  background-color: #ecf5ff;
}
</style>