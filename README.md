# Gatekeeper —— 智能主机安全基线动态检测系统

## 项目前端部分截图

<table>
<tr>
<td><img src="https://img.picui.cn/free/2025/07/03/6865631b92806.png" alt="图片1" width="500"/></td>
<td><img src="https://img.picui.cn/free/2025/07/03/686562ae1e3cb.png" alt="图片2" width="500"/></td>
</tr>
</table>

## 简介

Gatekeeper 是一个基于规则驱动的主机安全基线自动化检测与动态风险评估系统。它解决了传统人工检测效率低、覆盖不全、风险展示不直观等问题，通过前后端分离架构（前端Vue3+Element Plus+ECharts，后端Python+FastAPI），实现了高效的主机安全合规解决方案。

## 核心功能

1. **动态基线检测** ：引入指数加权移动平均（EWM）模型，实时学习系统指标（如CPU、内存）的正常范围，动态识别异常波动。

2. **自定义规则配置** ：支持命令、注册表、文件、脚本四类检测规则，用户可灵活适配CIS/NIST等安全标准。

3. **全维度自动化检测** ：覆盖账户安全、密码策略、网络配置等10+维度，单次扫描耗时<10秒，资源占用率低。

4. **三维可视化风险管控** ：通过安全评分圆环、风险等级饼图及动态基线折线图，结合修复指导，直观呈现风险详情。

## 技术栈

- **前端** ：Vue 3 + TypeScript + Element Plus + ECharts

- **后端** ：Python + FastAPI

- **数据库** ：SQLite

