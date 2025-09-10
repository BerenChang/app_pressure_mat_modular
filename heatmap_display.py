import numpy as np
from PyQt6.QtWidgets import QWidget, QLabel, QFrame, QVBoxLayout
from PyQt6.QtGui import QPixmap, QPainter, QColor, QImage, QPainterPath
from PyQt6.QtCore import Qt, QPoint, QPointF
import time
import cv2

from config import CANVA_WIDTH, CANVA_HEIGHT, TRACE_DURATION, BLOB_RADIUS, BLOB_SIGMA, THRESHOLDS, COLORS


class HeatmapDisplay(QWidget):
    def __init__(self, mat_width, mat_height, bg_path, parent=None):
        super().__init__(parent)
        self.mat_width = mat_width
        self.mat_height = mat_height
        self.kernel = self.generate_blob_kernel()

        self.data = np.zeros((self.mat_height, self.mat_width), dtype=np.uint8)
        self.trace_points = []
        self.trace_duration = TRACE_DURATION  
        self.cop_on = True

        self.old_cx = 0.0
        self.old_cy = 0.0
        self.alpha_c = 0.01
        self.cop_count = 0

        # Main layout for this widget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Background frame
        self.heatmap_bg_frame = QFrame(self)  # store as self, not local var
        self.heatmap_bg_frame.setFixedSize(CANVA_WIDTH, CANVA_HEIGHT)
        self.heatmap_bg_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 80);
            }
        """)

        # Label for heatmap image
        self.label = QLabel(self.heatmap_bg_frame)
        self.label.setFixedSize(CANVA_WIDTH, CANVA_HEIGHT)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("background: transparent;")

        # Frame layout
        heatmap_layout = QVBoxLayout(self.heatmap_bg_frame)
        heatmap_layout.setContentsMargins(0, 0, 0, 0)
        heatmap_layout.addWidget(self.label)

        main_layout.addWidget(self.heatmap_bg_frame, alignment=Qt.AlignmentFlag.AlignCenter)

        # other initializations
        self.blob_kernel = self.generate_blob_kernel(radius=BLOB_RADIUS, sigma=BLOB_SIGMA)
        self.background_pixmap = QPixmap(bg_path)
        self.output_size = (CANVA_HEIGHT, CANVA_WIDTH)

        self.thresholds = THRESHOLDS
        self.colors = COLORS

    def set_cop(self, state: bool):
        self.cop_on = state

    def set_background(self, pixmap):
        self.background_pixmap = pixmap
        self.update()

    # def compute_trace_point(self, data):
    #     indices = np.argwhere(data > 0)
    #     if len(indices) == 0:
    #         return None
    #     values = data[data > 0]
    #     avg_y, avg_x = np.average(indices, axis=0, weights=values)
    #     return QPoint(int(avg_x), int(avg_y))

    def paintEvent(self, event):
        painter = QPainter(self)
        scaled_pixmap = self.background_pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )
        painter.drawPixmap(0, 0, scaled_pixmap)

        # Semi-transparent white overlay
        painter.fillRect(self.rect(), QColor(255, 255, 255, 100))  # RGBA

    def map_to_widget(self, point):
        x_scale = self.width() / self.mat_width
        y_scale = self.height() / self.mat_height
        return QPoint(int(point.x() * x_scale), int(point.y() * y_scale))
    
    def apply_custom_colormap(self, gray_img):
        norm = gray_img.astype(np.uint8)
        h, w = norm.shape
        rgb = np.full((h, w, 3), 255, dtype=np.uint8)

        for i in range(len(self.thresholds) - 1):
            mask = (norm >= self.thresholds[i]) & (norm < self.thresholds[i + 1])
            rgb[mask] = self.colors[i]

        # Draw grid
        rows, cols = 28, 56
        scale_x, scale_y = w / cols, h / rows
        for x in range(1, cols):
            cv2.line(rgb, (int(x * scale_x), 0), (int(x * scale_x), h), (180, 180, 180), 1)
        for y in range(1, rows):
            cv2.line(rgb, (0, int(y * scale_y)), (w, int(y * scale_y)), (180, 180, 180), 1)

        return rgb

    def generate_blob_kernel(self, radius=15, sigma=10):
        size = radius * 2 + 1
        ax = np.linspace(-radius, radius, size)
        xx, yy = np.meshgrid(ax, ax)
        kernel = np.exp(-(xx**2 + yy**2) / (2. * sigma**2))
        np.set_printoptions(threshold=np.inf)
        return kernel / np.max(kernel)  # normalize to [0,1]
    
    def update_image(self, mat: np.ndarray):

        h_out, w_out = self.output_size
        canvas = np.zeros((h_out, w_out), dtype=np.float32)

        # Scaling ratios
        scale_x = w_out / mat.shape[1]
        scale_y = h_out / mat.shape[0]

        kh, kw = self.blob_kernel.shape
        rh, rw = kh // 2, kw // 2

        # === Compute Center of Pressure (CoP) ===
        cop_mat = np.maximum(mat-8, 0)
        total = np.sum(cop_mat)
        if total > 0:
            y_indices, x_indices = np.indices(cop_mat.shape)
            cx = np.sum(x_indices * cop_mat) / total
            cy = np.sum(y_indices * cop_mat) / total

            cx_temp = cx
            cy_temp = cy
            cx = cx_temp * self.alpha_c + self.old_cx * (1 - self.alpha_c)
            cy = cy_temp * self.alpha_c + self.old_cy * (1 - self.alpha_c)
            self.old_cx = cx_temp
            self.old_cy = cy_temp

            # Scale CoP to output size
            cx *= scale_x
            cy *= scale_y

            self.cop_count += 1
            if self.cop_count > 30:
                self.cop_bount = 0
                self.trace_points.append((cx, cy, time.time()))

        # === Trim trace history to last 2 seconds ===
        now = time.time()
        self.trace_points = [(x, y, t) for (x, y, t) in self.trace_points if now - t <= self.trace_duration]

        # === Render heat blobs ===
        for y in range(mat.shape[0]):
            for x in range(mat.shape[1]):
                v = mat[y, x]
                if v <= 0:
                    continue

                cx = int(x * scale_x)
                cy = int(y * scale_y)

                x1 = max(cx - rw, 0)
                x2 = min(cx + rw + 1, w_out)
                y1 = max(cy - rh, 0)
                y2 = min(cy + rh + 1, h_out)

                kx1 = rw - (cx - x1)
                kx2 = rw + (x2 - cx)
                ky1 = rh - (cy - y1)
                ky2 = rh + (y2 - cy)

                canvas[y1:y2, x1:x2] += v * self.blob_kernel[ky1:ky2, kx1:kx2]

        # Apply custom colormap (BGR)
        heatmap = self.apply_custom_colormap(canvas)

        # Convert to QImage
        h, w, ch = heatmap.shape
        qimg = QImage(heatmap.data, w, h, ch * w, QImage.Format.Format_RGB888)

        # Convert to QPixmap to draw overlays
        pixmap = QPixmap.fromImage(qimg)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)




        # # === Draw fading trace points ===
        # if self.cop_on:
        #     for x, y, t in self.trace_points:
        #         age_ratio = 1.0 - ((now - t) / self.trace_duration)
        #         alpha = int(255 * age_ratio)
        #         color = QColor(255, 0, 0, alpha)
        #         painter.setBrush(color)
        #         painter.setPen(Qt.PenStyle.NoPen)
        #         painter.drawEllipse(QPointF(x, y), 4, 4)

        #     # === Draw current CoP in red ===
        #     if self.trace_points:
        #         x, y, _ = self.trace_points[-1]
        #         painter.setBrush(QColor(255, 0, 0))
        #         painter.setPen(Qt.PenStyle.NoPen)
        #         painter.drawEllipse(QPointF(x, y), 6, 6)


        # === Draw fading smooth trace curve ===
        if self.cop_on and len(self.trace_points) > 2:
            path = QPainterPath()
            x0, y0, _ = self.trace_points[0]
            path.moveTo(x0, y0)

            # Use quadratic curves for smoothing
            for i in range(1, len(self.trace_points) - 1):
                x1, y1, _ = self.trace_points[i]
                x2, y2, _ = self.trace_points[i + 1]
                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2
                path.quadTo(x1, y1, cx, cy)

            # Fading effect along the path (segment by segment)
            for i in range(1, len(self.trace_points)):
                x1, y1, t1 = self.trace_points[i - 1]
                x2, y2, t2 = self.trace_points[i]
                age_ratio = 1.0 - ((now - t2) / self.trace_duration)
                alpha = int(255 * age_ratio)

                pen = painter.pen()
                pen.setColor(QColor(255, 0, 0, alpha))
                pen.setWidthF(2.5)  # fractional width for smoother look
                painter.setPen(pen)
                painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

            # === Draw current CoP in red ===
            if self.trace_points:
                x, y, _ = self.trace_points[-1]
                painter.setBrush(QColor(255, 0, 0))
                # painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(QPointF(x, y), 6, 6)

        painter.end()

        # Show final image
        self.label.setPixmap(pixmap)
