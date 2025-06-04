#EWM 模型实现

import numpy as np

class EWMModel:
    """
    EWM（Exponentially Weighted Moving）模型，用于动态基线计算
    特点：
    - 自适应系统正常行为波动（如周期性负载）
    - 实时更新基线和阈值（无需历史全量数据）
    - 低资源消耗（仅需保存当前均值和标准差）
    """
    
    def __init__(self, window_size=24, threshold_sigma=3):
        """
        :param window_size: 窗口大小（小时），决定历史数据的衰减速度
        :param threshold_sigma: 阈值倍数（σ），用于异常检测
        """
        self.alpha = 2 / (window_size + 1)  # 指数加权衰减系数
        self.ewma = None                   # 当前基线值（指数加权均值）
        self.ewm_std = 0                   # 当前标准差
        self.threshold_sigma = threshold_sigma  # 异常检测阈值倍数
        
    def update(self, value):
        """
        更新模型并计算新的基线和标准差
        :param value: 当前指标值（如CPU使用率）
        :return: 返回当前基线值和标准差
        """
        # 初始值处理
        if self.ewma is None:
            self.ewma = value
        else:
            # 计算EWM均值：新值权重为α，旧值权重为1-α
            self.ewma = self.alpha * value + (1 - self.alpha) * self.ewma
            # 计算EWM标准差：基于递推公式
            self.ewm_std = np.sqrt((1 - self.alpha) * self.ewm_std**2 + 
                                  self.alpha * (value - self.ewma)**2)
        return self.ewma, self.ewm_std

    def detect(self, value):
        """
        检测当前值是否偏离基线（异常检测）
        :param value: 当前指标值
        :return: (is_anomaly: bool, info: dict)
        """
        mean, std = self.update(value)
        # 判断是否超出阈值范围（基线 ± σ倍标准差）
        is_anomaly = abs(value - mean) > self.threshold_sigma * std
        return is_anomaly, {
            "mean": mean,
            "std": std,
            "threshold_low": mean - self.threshold_sigma * std,
            "threshold_high": mean + self.threshold_sigma * std
        }