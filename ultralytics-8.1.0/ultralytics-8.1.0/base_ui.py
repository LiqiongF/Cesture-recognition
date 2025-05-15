import sys
import cv2

import winsound

from ultralytics import YOLO
from PySide6.QtWidgets import QMainWindow,QApplication,QFileDialog,QMessageBox
from PySide6.QtGui import QPixmap,QImage
from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon

from ui_main_window import Ui_MainWindow

def convert2QImage(img):
    height,width,channel = img.shape
    return QImage(img,width,height,width * channel,QImage.Format_RGB888)
class MainWindow(QMainWindow,Ui_MainWindow):
    def __init__(self):
      super(MainWindow,self).__init__()
      self.setupUi(self)
      self.model = YOLO(r"C:\Users\86152\Desktop\ultralytics-8.1.0\runs\detect\train13\weights\best.pt")
      self.timer = QTimer()
      self.timer.setInterval(50)
      self.video = None

      # 报警参数配置
      self.fall_class_id = 0  # 确认摔倒类别ID
      self.alarm_delay = 1000  # 1秒延迟后报警（毫秒）
      self.beep_duration = 500  # 单次蜂鸣时长（毫秒）
      self.beep_interval = 200  # 蜂鸣间隔（毫秒）
      self.beep_count = 5  # 蜂鸣次数
      self.cooldown_time = 3000  # 冷却时间（毫秒）

      self.alarm_active = False  # 报警状态标志
      self.alarm_message_shown=False #消息框显示标志

      self.bind_slots()

    def check_fall_detection(self, results):
        """精确的摔倒检测逻辑"""
        for result in results:
            if result.boxes is not None:
                for box in result.boxes:
                    cls_id = int(box.cls[0].item())
                    conf = box.conf[0].item()
                    if cls_id == self.fall_class_id and conf > 0.5:
                        return True
        return False

    def trigger_alarm_sequence(self):
        """急促蜂鸣序列生成器"""
        for i in range(self.beep_count):
            QTimer.singleShot(i * (self.beep_duration + self.beep_interval),
                              lambda: winsound.Beep(2500, self.beep_duration))

        # 全部蜂鸣完成后进入冷却
        QTimer.singleShot(
            self.beep_count * (self.beep_duration + self.beep_interval),
            self.end_alarm_sequence
        )

    def start_alarm(self):
        """启动报警序列（带延迟）"""
        if not self.alarm_active:
            self.alarm_active = True
            QTimer.singleShot(self.alarm_delay, self.trigger_alarm_sequence)
            QTimer.singleShot(self.alarm_delay + self.cooldown_time, self.end_alarm_sequence)
            self.show_alarm_message()

    def end_alarm_sequence(self):
        """结束报警序列"""
        self.alarm_active = False
        # 冷却期间不响应新报警
        QTimer.singleShot(self.cooldown_time, lambda: None)

    def show_alarm_message(self):
        if not self.alarm_message_shown:
            self.alarm_message_shown = True
            QMessageBox.warning(None, "摔倒警报", "检测到有人员摔倒！请注意！")
    def reset_alarm_message_flag(self):
        self.alarm_message_shown = False

    def handle_fall_detection(self, original_image, processed_image):
        """处理摔倒检测并同时触发报警和弹窗"""
        self.output.setPixmap(QPixmap.fromImage(convert2QImage(processed_image)))
        self.input.setPixmap(QPixmap.fromImage(convert2QImage(original_image)))
        self.start_alarm()  # 改用延迟报警
        self.show_alarm_message()


    def image_pred(self,file_path):

        original_image = cv2.imread(file_path)
        results = self.model(file_path)
        processed_image = results[0].plot()
        # 检查摔倒并处理
        if self.check_fall_detection(results):
            self.handle_fall_detection(original_image, processed_image)
        return convert2QImage(processed_image)
    def open_image(self):
       self.timer.stop()
       self.reset_alarm_message_flag()
       file_path = QFileDialog.getOpenFileName(self,dir="./datasets/detect/images",filter="*.jpg;*.png;*.jpeg")
       if file_path[0]:
           file_path = file_path[0]
           qimage = self.image_pred(file_path)
           self.input.setPixmap(QPixmap(file_path))
           self.output.setPixmap(QPixmap.fromImage(qimage))

    def video_pred(self):

        ret, frame = self.video.read()
        if not ret:
            self.timer.stop()
        else:
            original_frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            results = self.model(original_frame)
            processed_frame = results[0].plot()
            self.input.setPixmap(QPixmap.fromImage(convert2QImage(original_frame)))
            # 检查摔倒并处理
            if self.check_fall_detection(results):
                self.handle_fall_detection(original_frame, processed_frame)
            else:
                self.output.setPixmap(QPixmap.fromImage(convert2QImage(processed_frame)))

    def open_video(self):
        self.reset_alarm_message_flag()
        file_path = QFileDialog.getOpenFileName(self, dir="./datasets/detect/videos", filter="*.mp4")
        if file_path[0]:
            file_path = file_path[0]
            self.video=cv2.VideoCapture(file_path)
            self.timer.start()
    def bind_slots(self):
        self.det_image.clicked.connect(self.open_image)
        self.det_video.clicked.connect(self.open_video)
        self.timer.timeout.connect(self.video_pred)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("LOGO.jpg"))

    window = MainWindow()
    window.show()

    app.exec()
