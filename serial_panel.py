from PyQt6.QtWidgets import QWidget, QPushButton, QGridLayout, QListWidget, QLabel, QComboBox
from PyQt6 import QtCore
from serial.tools import list_ports
from serial_reader import SerialReader
import numpy as np
import time
from config import SERIAL_PORT, BAUD_RATE, MAT_WIDTH, MAT_HEIGHT

class SerialPanel(QWidget):
    new_frame = QtCore.pyqtSignal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.frames = []
        self.calibration_frames = []
        self.offset = np.zeros((MAT_WIDTH, MAT_HEIGHT), dtype=np.float32)
        
        # --- Serial Port Selector ---
        port_label = QLabel("Select Serial Port:")
        self.port_dropdown = QComboBox()
        self.available_ports = []

        ports = list_ports.comports()
        for p in ports:
            self.port_dropdown.addItem(p.device)

        self.refresh_button = QPushButton("🔄")
        self.refresh_button.setFixedSize(30, 24)
        self.refresh_button.clicked.connect(self.refresh_ports)
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_serial)
        self.calibration_button = QPushButton("Calibration")
        self.calibration_button.clicked.connect(self.calibration)

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(port_label, 0, 0)
        layout.addWidget(self.port_dropdown, 0, 1)
        layout.addWidget(self.refresh_button, 0, 2)
        layout.addWidget(self.connect_button, 0, 3)
        layout.addWidget(self.calibration_button, 0, 4)
        # layout.setContentsMargins(330, 1, 330, 1)  # (left, top, right, bottom)

        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.start_reading)
        self.stop_button = QPushButton('Stop')
        # self.replay_button = QPushButton('Replay')
        # self.session_list = QListWidget()

        layout.addWidget(self.start_button, 1, 1)
        layout.addWidget(self.stop_button, 1, 2)
        # layout.addWidget(self.replay_button, 1, 3)
        # layout.addWidget(self.session_list, 2, 0, 4, 0)


    def refresh_ports(self):
        ports = [p.device for p in list_ports.comports()]
        if ports != self.available_ports:
            self.available_ports = ports

            current_selection = self.port_dropdown.currentText()
            self.port_dropdown.blockSignals(True)
            self.port_dropdown.clear()
            self.port_dropdown.addItems(ports)
            self.port_dropdown.blockSignals(False)

            # Try to reselect the previous port if it's still there
            if current_selection in ports:
                index = ports.index(current_selection)
                self.port_dropdown.setCurrentIndex(index)

    def connect_serial(self):
        selected_port = self.port_dropdown.currentText()
        if not selected_port:
            print("⚠ No port selected.")
            return

        global SERIAL_PORT
        SERIAL_PORT = selected_port
        print(f"[🔌] Connecting to {SERIAL_PORT}...")

        # Start reader
        self.reader = SerialReader(SERIAL_PORT, BAUD_RATE)
        self.reader.new_frame.connect(self.new_frame.emit)
        # self.reader.new_frame.connect(self.update_image)
        # self.reader.start()

        # Disable dropdown after connection
        self.port_dropdown.setEnabled(False)
        self.connect_button.setEnabled(False)

        # self.port_timer.stop()

    def calibration(self):
        for i in range(10):
            temp_frame = self.reader.read_serial_once()
            self.calibration_frames.append(temp_frame)
            self.offset += temp_frame
            time.sleep(0.1)
        self.offset = self.offset / 10
        np.set_printoptions(threshold=np.inf, linewidth=np.inf)
        print(self.offset)
        self.reader.offset = self.offset

    def start_reading(self):
        self.frames.clear()
        self.reader.start()
