from PyQt6.QtWidgets import QWidget, QPushButton, QGridLayout, QLabel, QComboBox
from PyQt6 import QtCore
import numpy as np

class RecordManager(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.is_recording = False
        self.is_replaying = False
        self.recorded_frames = []
        self.replay_frame = None

        self.record_button = QPushButton('Record')
        self.record_button.clicked.connect(self.toggle_record)
        self.replay_button = QPushButton('Replay')
        # self.replay_button.clicked.connect(self.replay)

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.record_button, 1, 3)
        layout.addWidget(self.replay_button, 1, 4)
        # layout.addWidget(self.session_list, 2, 0, 4, 0)


    def toggle_replay(self):
        if self.is_replaying:
            self.stop_replay()
        else:
            self.start_replay()

    def start_replay(self):
        try:
            self.replay_frames = np.load("last_recording.npy")
        except FileNotFoundError:
            print("No recording found")
            return
        if len(self.replay_frames) == 0:
            print("Empty recording")
            return
        self.was_running = self.reader.running if hasattr(self, 'reader') else False
        if self.was_running:
            self.stop_reading()
        self.replay_index = 0
        self.is_replaying = True
        self.replay_button.setText("Stop")
        self.replay_timer.start(100)  # 10 FPS
        print("[▶️] Replay started")

    def stop_replay(self):
        self.replay_timer.stop()
        self.is_replaying = False
        self.replay_button.setText("Replay")
        if self.was_running:
            self.start_reading()
        print("[⏹] Replay stopped")

    def play_next_frame(self):
        if self.replay_index >= len(self.replay_frames):
            self.stop_replay()
            return
        frame = self.replay_frames[self.replay_index]
        self.new_frame.emit(frame)
        self.replay_index += 1

    def toggle_record(self):
        if self.is_recording:
            self.is_recording = False
            self.record_button.setText("Record")
            if self.recorded_frames:
                print(self.recorded_frames)
                np.save("last_recording.npy", np.stack(self.recorded_frames))
                print(f"[📼] Saved {len(self.recorded_frames)} frames to last_recording.npy")
            self.recorded_frames = []
        else:
            self.is_recording = True
            self.record_button.setText("Stop Recording")
            print("[📼] Recording started")
