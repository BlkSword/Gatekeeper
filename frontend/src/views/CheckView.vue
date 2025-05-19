<template>
  <div class="full-container">
    <!-- 页眉区域 -->
    <header class="header">
      <div class="button-group">
        <button class="blue-button">一键检测</button>
        <button class="blue-button">一键加固</button>
        <button class="blue-button">报告导出</button>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <main class="main-content">
      <!-- 检查项列表 -->
      <div 
        v-for="(item, index) in checkList" 
        :key="index" 
        class="check-item"
      >
        <div class="item-info">
          <div class="name-time-group">
            <small>检查名称</small>
            <span class="check-name">{{ item.name }}</span>
          </div>
          <div class="name-time-group">
            <small>最后执行时间</small>
            <span class="exec-time">{{ item.lastExecuted }}</span>
          </div>
        </div>
        <div class="actions">
          <button @click="playCheck(index)" class="action-btn">
            <el-icon><View /></el-icon>
          </button>
          <button @click="editCheck(index)" class="action-btn">
            <el-icon><Operation /></el-icon>
          </button>
          <button @click="deleteCheck(index)" class="action-btn">
            <el-icon><Delete /></el-icon>
          </button>
</div>
      </div>
    </main>
  </div>
</template>

<script>
export default {
  data() {
    return {
      // 示例数据
      checkList: [
        { name: 'test1', lastExecuted: '2021-08-25 13:14:48' },
        { name: 'test2', lastExecuted: '2023-04-12 09:32:15' },
        { name: 'test3', lastExecuted: '2023-08-01 16:45:00' }
      ]
    }
  },
  methods: {
    playCheck(index) {
      console.log(`打开检查项 ${this.checkList[index].name}`);
    },
    copyCheck(index) {
      console.log(`复制检查项 ${this.checkList[index].name}`);
    },
    editCheck(index) {
      console.log(`编辑检查项 ${this.checkList[index].name}`);
    },
    deleteCheck(index) {
      console.log(`删除检查项 ${this.checkList[index].name}`);
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

/* 检查项样式 */
.check-item {
  border: 1px solid #ddd;
  padding: 1rem;
  margin-bottom: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #ffffff;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

/* 信息区域样式 */
.item-info {
  display: flex;
  flex-direction: row; 
  gap: 25rem; 
}

/* 名称和时间组样式 */
.name-time-group {
  display: flex;
  flex-direction: column;
  align-items: flex-start; 
}

.name-time-group small {
  color: #999999;
  font-size: 12px;
}


/* 修改检查名称样式 */
.check-name {
  font-size: 18px; 
  color: #000000; 
}

/* 执行时间样式 */
.exec-time {
  color: #000000;
  font-size: 18px; 
}

/* 修改名称时间组间距 */
.name-time-group {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5rem; 
}

/* 操作按钮组 */
.actions {
  display: flex;
  gap: 0.5rem;
}

/* 操作按钮样式 */
.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  color: #409EFF;
  padding: 0.3rem;
  border-radius: 4px;
  transition: all 0.3s ease;
}

/* 操作按钮悬停效果 */
.action-btn:hover {
  background-color: #ecf5ff;
  color: #367fd1;
  transform: scale(1.1);
}
</style>