from PyQt6 import QtWidgets, QtCore, QtGui


class ThresholdSliderBar(QtWidgets.QWidget):
    threshold_changed = QtCore.pyqtSignal(list)

    def __init__(self, thresholds, colors, parent=None):
        super().__init__(parent)
        self.thresholds = thresholds  # List of ints (0-255)
        self.colors = colors  # List of RGB tuples
        self.setFixedHeight(50)

        self.slider_radius = 7
        self.dragging_index = None

        self.max = 50

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        width = self.width()
        height = self.height()
        num_segments = len(self.colors)
        sorted_thresholds = sorted(self.thresholds)

        # Map thresholds (0-50) to x coordinates
        x_positions = [int(t / self.max * width) for t in sorted_thresholds]
        x_positions = [0] + x_positions + [width]

        # Draw colored segments
        for i in range(num_segments):
            start_x = x_positions[i + 1]
            end_x = x_positions[i + 2]
            rect = QtCore.QRect(start_x, 0, end_x - start_x, height // 2)
            painter.fillRect(rect, QtGui.QColor(*self.colors[i]))

        # Draw slider handles
        for x in x_positions[1:-1]:
            painter.setBrush(QtGui.QColor("black"))
            painter.setPen(QtGui.QPen(QtGui.QColor("white"), 1))
            painter.drawEllipse(QtCore.QPointF(x, height // 2), self.slider_radius, self.slider_radius)

    def mousePressEvent(self, event):
        x = event.position().x()
        width = self.width()

        for i, t in enumerate(self.thresholds):
            handle_x = t / self.max * width
            if abs(x - handle_x) <= self.slider_radius + 3:
                self.dragging_index = i
                break

    def mouseMoveEvent(self, event):
        if self.dragging_index is not None:
            x = event.position().x()
            width = self.width()
            t = int(x / width * self.max)
            t = max(0, min(self.max, t))

            # Keep thresholds sorted and avoid overlap
            if self.dragging_index > 0 and t < self.thresholds[self.dragging_index - 1] + 1:
                t = self.thresholds[self.dragging_index - 1] + 1
            if self.dragging_index < len(self.thresholds) - 1 and t > self.thresholds[self.dragging_index + 1] - 1: 
                t = self.thresholds[self.dragging_index + 1] - 1

            self.thresholds[self.dragging_index] = t
            self.threshold_changed.emit(self.thresholds)
            self.update()

    def mouseReleaseEvent(self, event):
        self.dragging_index = None  
