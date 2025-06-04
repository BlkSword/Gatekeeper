<template>
  <div class="full-container">
    <el-scrollbar style="height: 100vh;">
      <!-- 页眉区域 -->
      <header class="header">
        <div class="button-group">
          <button class="blue-button" @click="showRuleDialog = true">自定义规则</button>
        </div>
        <!-- 自定义规则弹窗 -->
        <div v-if="showRuleDialog" class="custom-modal">
          <div class="modal-content" style="width: 800px;">
            <div class="modal-header">
              <span class="modal-title">新建规则</span>
              <span class="modal-close" @click="closeRuleDialog">&times;</span>
            </div>
            <div class="modal-body">
              <el-form ref="ruleFormRef" :model="ruleForm" label-width="120px" :rules="rules" label-position="right"
                @submit.prevent>
                <!-- 步骤条 -->
                <el-steps :active="activeStep" finish-status="success" simple style="margin-bottom: 20px">
                  <el-step title="基础信息"></el-step>
                  <el-step title="参数设置"></el-step>
                  <el-step title="基线信息"></el-step>
                </el-steps>
                <!-- 步骤内容 -->
                <div class="step-content">
                  <!-- 步骤一：基础信息 -->
                  <div v-if="activeStep === 0" class="step-pane">
                    <div class="form-section">
                      <h3>基础信息</h3>
                      <el-form-item label="规则名称" prop="name">
                        <el-input v-model="ruleForm.name" />
                      </el-form-item>
                      <el-form-item label="描述" prop="description">
                        <el-input v-model="ruleForm.description" type="textarea" :rows="2" />
                      </el-form-item>
                      <el-form-item label="规则类型" prop="rule_type">
                        <el-select v-model="ruleForm.rule_type" placeholder="请选择规则类型" @change="handleRuleTypeChange">
                          <el-option label="命令规则" value="command" />
                          <el-option label="注册表规则" value="service" />
                          <el-option label="文件规则" value="file" />
                          <el-option label="脚本检测" value="python_script" />
                        </el-select>
                      </el-form-item>
                      <el-form-item label="严重等级" prop="severity_level">
                        <el-select v-model="ruleForm.severity_level" placeholder="请选择严重等级">
                          <el-option label="高危" value="high" />
                          <el-option label="中危" value="medium" />
                          <el-option label="低危" value="low" />
                        </el-select>
                      </el-form-item>
                    </div>
                  </div>
                  <!-- 步骤二：参数设置 -->
                  <div v-if="activeStep === 1 && ruleForm.rule_type" class="step-pane">
                    <div class="form-section">
                      <h3>参数设置</h3>
                      <!-- 命令规则参数 -->
                      <div v-if="ruleForm.rule_type === 'command'">
                        <el-form-item label="命令" prop="params.command">
                          <el-input v-model="ruleForm.params.command" />
                        </el-form-item>
                        <el-form-item label="必须包含" prop="expected_result.must_contain">
                          <el-input v-model="ruleForm.expected_result.must_contain" />
                        </el-form-item>
                        <el-form-item label="禁止包含" prop="expected_result.must_not_contain">
                          <el-input v-model="ruleForm.expected_result.must_not_contain" />
                        </el-form-item>
                      </div>
                      <!-- 注册表规则参数 -->
                      <div v-else-if="ruleForm.rule_type === 'service'">
                        <el-form-item label="注册表项" prop="params.hive">
                          <el-select v-model="ruleForm.params.hive" placeholder="请选择注册表项">
                            <el-option label="HKEY_LOCAL_MACHINE" value="HKEY_LOCAL_MACHINE" />
                            <el-option label="HKEY_CURRENT_USER" value="HKEY_CURRENT_USER" />
                          </el-select>
                        </el-form-item>
                        <el-form-item label="键路径" prop="params.key">
                          <el-input v-model="ruleForm.params.key" />
                        </el-form-item>
                        <el-form-item label="值名称" prop="params.value_name">
                          <el-input v-model="ruleForm.params.value_name" />
                        </el-form-item>
                        <el-form-item label="预期值" prop="expected_result.expected_value">
                          <el-input v-model="ruleForm.expected_result.expected_value" />
                        </el-form-item>
                      </div>
                      <!-- 文件规则参数 -->
                      <div v-else-if="ruleForm.rule_type === 'file'">
                        <el-form-item label="文件路径" prop="params.path">
                          <el-input v-model="ruleForm.params.path" />
                        </el-form-item>
                        <el-form-item label="哈希类型" prop="params.hash_type">
                          <el-select v-model="ruleForm.params.hash_type" placeholder="请选择哈希类型">
                            <el-option label="MD5" value="md5" />
                            <el-option label="SHA1" value="sha1" />
                            <el-option label="SHA256" value="sha256" />
                          </el-select>
                        </el-form-item>
                        <el-form-item label="预期哈希" prop="expected_result.expected_hash">
                          <el-input v-model="ruleForm.expected_result.expected_hash" />
                        </el-form-item>
                      </div>
                      <!-- 脚本检测参数 -->
                      <div v-else-if="ruleForm.rule_type === 'python_script'">
                        <el-form-item label="脚本路径" prop="params.script_path">
                          <el-input v-model="ruleForm.params.script_path" />
                        </el-form-item>
                        <el-form-item label="预期状态" prop="expected_result.status">
                          <el-select v-model="ruleForm.expected_result.status" placeholder="请选择预期状态">
                            <el-option label="成功" :value="true" />
                            <el-option label="失败" :value="false" />
                          </el-select>
                        </el-form-item>
                        <el-form-item label="预期消息" prop="expected_result.message">
                          <el-input v-model="ruleForm.expected_result.message" />
                        </el-form-item>
                      </div>
                    </div>
                  </div>
                  <!-- 步骤三：基线信息 -->
                  <div v-if="activeStep === 2" class="step-pane">
                    <div class="form-section">
                      <h3>基线信息</h3>
                      <el-form-item label="基线标准" prop="baseline_standard">
                        <el-input v-model="ruleForm.baseline_standard" type="textarea" :rows="2" />
                      </el-form-item>
                      <el-form-item label="风险描述" prop="risk_description">
                        <el-input v-model="ruleForm.risk_description" type="textarea" :rows="3" />
                      </el-form-item>
                      <el-form-item label="解决方案" prop="solution">
                        <el-input v-model="ruleForm.solution" type="textarea" :rows="3" />
                      </el-form-item>
                      <el-form-item label="温馨提示" prop="tip">
                        <el-input v-model="ruleForm.tip" type="textarea" :rows="2" />
                      </el-form-item>
                    </div>
                  </div>
                </div>
                <!-- 步骤按钮 -->
                <div class="modal-footer">
                  <button v-if="activeStep > 0" class="gray-button" @click="prevStep">上一步</button>
                  <button v-if="activeStep < 2" class="blue-button" @click="nextStep">下一步</button>
                  <button v-else class="blue-button" @click="submitRule">提交规则</button>
                  <button class="gray-button" @click="closeRuleDialog">取消</button>
                </div>
              </el-form>
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
            <button class="scan-button" @click="startScan" :disabled="isLoading">
              {{ isLoading ? '扫描中...' : '立即检查' }}
            </button>
          </div>
        </div>
        <!-- 风险列表 -->
        <div class="risk-list" ref="riskListContainer">
          <div class="risk-header">
            <!-- 移除了全选复选框 -->
          </div>
          <!-- 空状态提示 -->
          <div v-if="risks.length === 0 && !isLoading" class="empty-state">
            暂无风险数据，请先进行安全检查
          </div>
          <!-- 加载中状态 -->
          <div v-else-if="isLoading" class="empty-state">
            <!-- 区域加载动画 -->
            <el-loading :visible="isLoading" :text="'正在扫描中...'" :spinner="'el-icon-loading'"
              :background="'rgba(255, 255, 255, 0.7)'" />
          </div>
          <!-- 风险项 -->
          <transition-group name="fade">
            <div v-for="(risk, index) in risks" :key="risk.title" class="risk-item" v-show="!risk.ignored">
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
import { ElMessage, ElLoading } from 'element-plus';
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
      // 新增步骤状态
      activeStep: 0,
      // 新增规则表单数据
      ruleForm: {
        name: '',
        description: '',
        rule_type: '',
        severity_level: 'high',
        params: {},
        expected_result: {},
        baseline_standard: '',
        risk_description: '',
        solution: '',
        tip: ''
      },
      // 表单验证规则
      rules: {
        name: [{ required: true, message: '请输入规则名称', trigger: 'blur' }],
        description: [{ required: true, message: '请输入描述', trigger: 'blur' }],
        rule_type: [{ required: true, message: '请选择规则类型', trigger: 'change' }],
        severity_level: [{ required: true, message: '请选择严重等级', trigger: 'change' }],
        'params.command': [{ required: true, message: '请输入命令', trigger: 'blur' }],
        'expected_result.must_contain': [{ required: true, message: '请输入必须包含的内容', trigger: 'blur' }],
        'params.hive': [{ required: true, message: '请选择注册表项', trigger: 'change' }],
        'params.key': [{ required: true, message: '请输入键路径', trigger: 'blur' }],
        'params.value_name': [{ required: true, message: '请输入值名称', trigger: 'blur' }],
        'expected_result.expected_value': [{ required: true, message: '请输入预期值', trigger: 'blur' }],
        'params.path': [{ required: true, message: '请输入文件路径', trigger: 'blur' }],
        'params.hash_type': [{ required: true, message: '请选择哈希类型', trigger: 'change' }],
        'expected_result.expected_hash': [{ required: true, message: '请输入预期哈希值', trigger: 'blur' }],
        'params.script_path': [{ required: true, message: '请输入脚本路径', trigger: 'blur' }],
        'expected_result.status': [{ required: true, message: '请选择预期状态', trigger: 'change' }],
        'expected_result.message': [{ required: true, message: '请输入预期消息', trigger: 'blur' }],
        baseline_standard: [{ required: true, message: '请输入基线标准', trigger: 'blur' }],
        risk_description: [{ required: true, message: '请输入风险描述', trigger: 'blur' }],
        solution: [{ required: true, message: '请输入解决方案', trigger: 'blur' }],
        tip: [{ required: true, message: '请输入温馨提示', trigger: 'blur' }]
      },
      loadingInstance: null
    };
  },
  computed: {
    scanStatusText() {
      return this.isScanned
        ? `已完成安全检查，已检测到${this.riskCount}个风险`
        : '尚未进行安全检查';
    },
    scanTimeText() {
      return this.isScanned
        ? `上次检查时间：${this.lastScanTime}`
        : '点击右侧按钮开始首次检查';
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
    if (this.loadingInstance) {
      this.loadingInstance.close();
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
      // 创建区域加载动画
      this.loadingInstance = this.$loading({
        target: this.$refs.riskListContainer,
        text: '正在扫描中...',
        spinner: 'el-icon-loading',
        background: 'rgba(255, 255, 255, 0.7)',
        lock: true
      });
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
              this.loadingInstance.close();
              this.loadingInstance = null;
            }
          } catch (error) {
            console.error('轮询进度失败:', error);
            this.handleError('扫描过程中发生错误');
            this.loadingInstance.close();
            this.loadingInstance = null;
          }
        }, 2000); // 每2秒轮询一次
      } catch (error) {
        console.error('启动扫描任务失败:', error);
        this.handleError('无法启动扫描任务');
        this.loadingInstance.close();
        this.loadingInstance = null;
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
    handleAction(riskIndex, action) {
      const risk = this.risks[riskIndex];
      if (action === '详情') {
        this.showDetails = true;
        this.selectedRisk = { ...risk };
      } else if (action === '忽略') {
        risk.ignored = true;
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
      ElMessage.error({
        message: message,
        duration: 3000,
        center: true
      });
      if (this.loadingInstance) {
        this.loadingInstance.close();
        this.loadingInstance = null;
      }
    },
    // 规则类型切换处理
    handleRuleTypeChange(val) {
      // 清空参数和预期结果
      this.ruleForm.params = {};
      this.ruleForm.expected_result = {};
      // 初始化特定规则参数
      if (val === 'command') {
        this.ruleForm.params.command = '';
        this.ruleForm.expected_result.must_contain = '';
        this.ruleForm.expected_result.must_not_contain = '';
      } else if (val === 'service') {
        this.ruleForm.params.hive = 'HKEY_LOCAL_MACHINE';
        this.ruleForm.params.key = '';
        this.ruleForm.params.value_name = '';
        this.ruleForm.expected_result.expected_value = '';
      } else if (val === 'file') {
        this.ruleForm.params.path = '';
        this.ruleForm.params.hash_type = 'md5';
        this.ruleForm.expected_result.expected_hash = '';
      } else if (val === 'python_script') {
        this.ruleForm.params.script_path = '';
        this.ruleForm.expected_result.status = true;
        this.ruleForm.expected_result.message = '';
      }
    },
    // 关闭规则弹窗
    closeRuleDialog() {
      this.showRuleDialog = false;
      this.activeStep = 0;
      this.$refs.ruleFormRef.resetFields();
    },
    // 上一步
    prevStep() {
      if (this.activeStep > 0) {
        this.activeStep--;
      }
    },
    // 下一步
    nextStep() {
      if (this.activeStep === 0) {
        this.$refs.ruleFormRef.validateField(['name', 'description', 'rule_type'], (valid, invalidFields) => {
          if (valid) {
            this.activeStep++;
          } else {
            // 添加错误提示并保持弹窗打开
            Object.values(invalidFields).forEach(errors => {
              errors.forEach(error => {
                this.$message.error(error.message);
              });
            });
          }
        });
      } else if (this.activeStep === 1) {
        // 根据rule_type验证参数字段
        let fieldsToValidate = [];
        if (this.ruleForm.rule_type === 'command') {
          fieldsToValidate = ['params.command', 'expected_result.must_contain', 'expected_result.must_not_contain'];
        } else if (this.ruleForm.rule_type === 'service') {
          fieldsToValidate = ['params.hive', 'params.key', 'params.value_name', 'expected_result.expected_value'];
        } else if (this.ruleForm.rule_type === 'file') {
          fieldsToValidate = ['params.path', 'params.hash_type', 'expected_result.expected_hash'];
        } else if (this.ruleForm.rule_type === 'python_script') {
          fieldsToValidate = ['params.script_path', 'expected_result.status', 'expected_result.message'];
        }
        this.$refs.ruleFormRef.validateField(fieldsToValidate, (valid) => {
          if (valid) {
            this.activeStep++;
          }
        });
      }
    },
    // 提交规则
    async submitRule() {
      try {
        await this.$refs.ruleFormRef.validate();
        // 提交规则到后端
        const response = await axios.post('http://127.0.0.1:8000/rules', this.ruleForm);
        if (response.status === 200) {
          this.$message.success('规则创建成功');
          this.closeRuleDialog();
        }
      } catch (error) {
        this.$message.error('规则创建失败');
        console.error('创建规则失败:', error);
      }
    }
  },
  watch: {
    score(newVal, oldVal) {
      if (this.chartInstance && newVal !== oldVal) {
        this.updateChartColor();
      }
    },
    isLoading(newVal) {
      if (!newVal && this.loadingInstance) {
        this.loadingInstance.close();
        this.loadingInstance = null;
      }
    }
  }
};
</script>

<style scoped src="../../src/assets/css/CheckView.css"></style>