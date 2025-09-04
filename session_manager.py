from PyQt6 import QtWidgets
import os

class SessionManager:
    def __init__(self, layout: QtWidgets.QVBoxLayout):
        self.layout = layout
        self.selected_file = None
        self.selected_card = None

    def load_sessions(self):
        # Stub: implement loading session cards and adding to layout
        pass

    def save_session(self):
        # Stub: implement loading session cards and adding to layout
        pass

    def delete_session(self, filename):
        filepath = os.path.join("logs", filename)
        if os.path.exists(filepath):
            os.remove(filepath)

    def list_sessions(self):
        return sorted(
            [f for f in os.listdir(self.log_dir) if f.endswith('.npz')],
            reverse=True
        )

    def get_session_path(self, filename):
        return os.path.join(self.log_dir, filename)