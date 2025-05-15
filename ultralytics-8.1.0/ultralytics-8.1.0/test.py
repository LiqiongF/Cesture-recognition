# test.py 修正后代码
import torch
from ultralytics import YOLO
from ultralytics.nn.tasks import DetectionModel  # 确保导入

# 在安全上下文中加载模型
with torch.serialization.safe_globals([DetectionModel]):
    model = YOLO()  # 先创建空模型实例
    model.load('yolov8n.pt', weights_only=False)  # 再加载权重

# 训练模型（保持原有代码不变）
model.train(data='yolobvn.yaml', workers=1, epochs=200, batch=16)