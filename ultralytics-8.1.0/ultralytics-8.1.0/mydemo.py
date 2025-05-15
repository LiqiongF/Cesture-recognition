import os
model_path = "C:\\Users\\86152\\Desktop\\ultralytics-8.1.0\\ultralytics\\runs\\detect\\train13\\weights\\best.pt"

# 检查路径是否存在
if not os.path.exists(model_path):
    raise FileNotFoundError(f"路径不存在：{model_path}")

# 检查是否为文件
if not os.path.isfile(model_path):
    raise ValueError(f"目标路径不是文件：{model_path}")