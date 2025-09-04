from PyQt6.QtWidgets import QWidget, QPushButton, QGridLayout, QLabel, QComboBox
from PyQt6 import QtCore
from serial.tools import list_ports
from serial_reader import SerialReader
import numpy as np
import time
from config import SERIAL_PORT, BAUD_RATE, MAT_WIDTH, MAT_HEIGHT

class ControlPanel(QWidget):
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

        self.reader = None
        ports = list_ports.comports()
        for p in ports:
            self.port_dropdown.addItem(p.device)

        self.is_reading = False
        self.cop_on = True


        self.refresh_button = QPushButton("🔄")
        self.refresh_button.setFixedSize(30, 24)
        self.refresh_button.clicked.connect(self.refresh_ports)
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_serial)
        self.calibration_button = QPushButton("Calibration")
        self.calibration_button.clicked.connect(self.calibration)
        self.start_button = QPushButton('Start Reading')
        self.start_button.clicked.connect(self.toggle_reading)

        self.cop_button = QPushButton('CoP OFF')
        self.cop_button.clicked.connect(self.toggle_cop)

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(port_label, 0, 0)
        layout.addWidget(self.port_dropdown, 0, 1)
        layout.addWidget(self.refresh_button, 0, 2)
        layout.addWidget(self.connect_button, 0, 3)
        layout.addWidget(self.start_button, 0, 4)
        layout.addWidget(self.cop_button, 0, 5)
        # layout.addWidget(self.calibration_button, 0, 4)
        # layout.setContentsMargins(330, 1, 330, 1)  # (left, top, right, bottom)

        # self.start_button = QPushButton('Start')
        # self.start_button.clicked.connect(self.toggle_reading)
        # self.start_button.clicked.connect(self.start_reading)
        # self.stop_button = QPushButton('Stop')
        # self.stop_button.clicked.connect(self.stop_reading)

        # layout.addWidget(self.start_button, 1, 1)
        # layout.addWidget(self.stop_button, 1, 2)
        

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

        # Disable dropdown after connection
        self.port_dropdown.setEnabled(False)
        self.connect_button.setEnabled(False)

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

    def toggle_reading(self):
        if self.is_reading:
            self.is_reading = False
            self.start_button.setText("Start")
            self.stop_reading()
        else:
            self.is_reading = True
            self.start_button.setText("Pause Reading")
            self.start_reading()

    def start_reading(self):
        self.frames.clear()
        self.reader.start()

    def stop_reading(self):
        self.reader.stop()

    def toggle_cop(self):
        if self.cop_on:
            self.cop_on = False
            self.cop_button.setText("CoP OFF")
        else:
            self.cop_on = True
            self.cop_button.setText("CoP ON")