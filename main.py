import sys
import os
from PyQt6 import QtWidgets, QtGui
# from PyQt6.QtCore import Qt
# from heatmap_widget import HeatmapWidget
from heatmap_display import HeatmapDisplay
# from heatmap_interpolation import HeatmapInterpolation
from control_panel import ControlPanel
from threshold_slider import ThresholdSliderBar
from record_manager import RecordManager
# import numpy as np

from config import MAT_WIDTH, MAT_HEIGHT, THRESHOLDS, COLORS

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        # Running in PyInstaller bundle
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        # Running normally
        return os.path.join(os.path.abspath("."), relative_path)

class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        bg_path = resource_path("background.jpg")
        logo_path = resource_path("logo.jpg")

        self.setWindowTitle('Impact Sports Pressure Visualization System')
        self.setGeometry(100, 100, 1000, 600)
        self.setWindowIcon(QtGui.QIcon(logo_path))

        self.background_pixmap = QtGui.QPixmap(bg_path)
        self.heatmap = HeatmapDisplay(MAT_WIDTH, MAT_HEIGHT, bg_path)
        # self.heatmap = HeatmapWidget(MAT_WIDTH, MAT_HEIGHT)
        # self.heatmap = HeatmapInterpolation(MAT_WIDTH, MAT_HEIGHT)

        self.threshold_bar = ThresholdSliderBar(
            thresholds=THRESHOLDS,
            colors=COLORS
        )
        self.threshold_bar.threshold_changed.connect(self.on_thresholds_updated)

        self.control_panel = ControlPanel()
        self.control_panel.new_frame.connect(self.handle_data)

        self.record_manager = RecordManager()
        self.record_manager.new_frame.connect(self.handle_data)

        self.control_panel.toggle_record.connect(self.record_manager.set_record_button)
        self.control_panel.cop_on_emitter.connect(self.heatmap.set_cop)        

        central_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central_widget)
        layout.addWidget(self.heatmap, 4)
        layout.addWidget(self.control_panel, 1)
        layout.addWidget(self.record_manager, 1)
        layout.addWidget(self.threshold_bar, 2)
        self.setCentralWidget(central_widget)

    def handle_data(self, data):
        # np.set_printoptions(threshold=np.inf, linewidth=np.inf)
        # print(data)
        
        if self.record_manager.is_replaying:
            self.heatmap.update_image(self.record_manager.replay_frame)
        elif self.record_manager.is_recording:
            self.heatmap.update_image(data)
            self.record_manager.recorded_frames.append(data)
        else:
            self.heatmap.update_image(data)

    # def handle_data(self, data):
    #     self.heatmap.cop_on = self.control_panel.cop_on
    #     self.heatmap.update_image(data)

    def on_thresholds_updated(self, new_thresholds):
        self.heatmap.thresholds = new_thresholds
        print("Updated thresholds:", new_thresholds)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = MainApp()
    win.show()
    sys.exit(app.exec())

