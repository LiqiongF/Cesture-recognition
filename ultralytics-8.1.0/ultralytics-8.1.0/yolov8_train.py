from ultralytics import YOLO
from ultralytics.nn.tasks import DetectionModel
import torch

# 允许加载DetectionModel类
torch.serialization.add_safe_globals([DetectionModel])

model = YOLO('yolov8n.pt')  # 使用预训练模型
model.train(
    data='yolobvn.yaml',    # 确保YAML路径正确
    workers=1,              # CPU线程数
    epochs=50,
    batch=16,               # 根据内存调整批次大小
    device='cpu'            # 显式指定使用CPU
)