<!-- 接口测试界面 -->
<template>
    <div class="test-container">
        <!-- 请求触发按钮 -->
        <button @click="fetchData" :disabled="loading" class="request-btn">
            {{ loading ? '请求中...' : '发起接口请求' }}
        </button>

        <!-- 错误提示 -->
        <div v-if="error" class="error-message">
            {{ error }}
        </div>

        <!-- 响应数据展示 -->
        <div v-if="response" class="response-data">
            <h3>接口回显数据：</h3>
            <pre>{{ formattedResponse }}</pre>
        </div>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    data() {
        return {
            response: null,
            error: null,
            loading: false
        };
    },
    methods: {
        async fetchData() {
            this.loading = true;
            this.error = null;

            try {
                // 发起 GET 请求
                const response = await axios.get('http://127.0.0.1:8000/system_status');

                // 保存响应数据
                this.response = response.data;
            } catch (err) {
                // 处理错误
                this.error = err.response?.data?.message || '请求失败，请检查网络或接口地址';
            } finally {
                this.loading = false;
            }
        }
    },
    computed: {
        // 格式化 JSON 数据展示
        formattedResponse() {
            return JSON.stringify(this.response, null, 2);
        }
    }
};
</script>

<style scoped>
.test-container {
    padding: 20px;
    max-width: 800px;
    margin: 0 auto;
}

.request-btn {
    padding: 10px 20px;
    font-size: 16px;
    cursor: pointer;
    background: #42b983;
    color: white;
    border: none;
    border-radius: 4px;
    margin-bottom: 20px;
}

.request-btn:disabled {
    background: #ccc;
    cursor: not-allowed;
}

.error-message {
    color: #e74c3c;
    margin: 15px 0;
    padding: 10px;
    background: #ffeaea;
    border-radius: 4px;
}

.response-data {
    background: #f4f4f4;
    padding: 15px;
    border-radius: 4px;
    white-space: pre-wrap;
    word-break: break-word;
}

pre {
    margin: 0;
}
</style>