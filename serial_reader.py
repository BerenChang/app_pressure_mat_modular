import numpy as np
import serial
import threading
from PyQt6 import QtCore
from scipy.ndimage import gaussian_filter
from config import START_READING_COMMAND, MAT_HEIGHT, MAT_WIDTH, VERIFICATION_WIDTH, VERIFICATION_SEQUENCE, MAT_SIZE, GET_CAL_VALS_COMMAND

class SerialReader(QtCore.QObject):
    new_frame = QtCore.pyqtSignal(np.ndarray)

    def __init__(self, port, baud, parent=None):
        super().__init__(parent)
        self.ser = serial.Serial(port, baud, timeout=1)
        self.running = False
        
        # ===== filtering ==========
        self.prev_filtered_mat = np.zeros((MAT_HEIGHT, MAT_WIDTH), dtype=np.float32)
        self.alpha = 1.0  # Smoothing factor (tweak as needed)

        self.offset = np.zeros((MAT_WIDTH, MAT_HEIGHT), dtype=np.float32)

    def start(self):
        self.ser.write((START_READING_COMMAND + '\n').encode('utf-8'))
        self.running = True
        threading.Thread(target=self.read_loop, daemon=True).start()

    def stop(self):
        self.running = False
        # if self.ser.is_open:
        #     self.ser.close()

    def mat_list_to_array_subsize(self, mat_as_list: list, width: int, height: int):
        """
        Converts a 1d python list (presumably the mat) to a 2D numpy array
        """

        array = np.empty((width, height), dtype=np.uint8)
        
        for i in range(width):
            array[i, :] = mat_as_list[i*MAT_HEIGHT : i*MAT_HEIGHT+height]

        return array
    
    def read_serial_once(self):
        self.ser.write((GET_CAL_VALS_COMMAND + '\n').encode('utf-8'))
        bytes = self.ser.read(VERIFICATION_WIDTH + MAT_SIZE)
        if bytes == b'':
            print("Serial timed out!")
            
        flat_mat = [x for x in bytes]
        subarray = self.mat_list_to_array_subsize(flat_mat, 56, 28)
        return subarray

    def read_loop(self):
        while self.running:
            try:
                data = self.ser.read(VERIFICATION_WIDTH + MAT_SIZE)
                if data == b'':
                    print("Serial timed out!")
                    continue
            
                flat_mat = [x for x in data]
                for ver, val in zip(VERIFICATION_SEQUENCE, flat_mat[-4:]):
                    if not (ver == val):
                        print("==== SYNCHRONIZING SERIAL DATA ====")
                        self.ser.reset_input_buffer()
                        hist = np.zeros(VERIFICATION_WIDTH, dtype=np.uint8)

                        while(not np.array_equal(hist, np.asarray(VERIFICATION_SEQUENCE, dtype=np.uint8))):
                            hist = np.roll(hist, -1)
                            hist[-1] = int.from_bytes(self.ser.read(1), "big")

                        break   # do not false positive another error

                subarray = np.array(self.mat_list_to_array_subsize(flat_mat, 56, 28))
                # subarray = np.maximum(subarray - self.offset, 0)
                subarray[subarray < 3] = 0
                subarray = subarray.transpose()
                # self.new_frame.emit(subarray)
                sigma_y = 2.0  # heel-to-toe spread
                sigma_x = 1.0  # side-to-side spread
                self.prev_filtered_mat = self.alpha * subarray + (1 - self.alpha) * self.prev_filtered_mat
                self.prev_filtered_mat = gaussian_filter(self.prev_filtered_mat, sigma=(sigma_y, sigma_x))
                self.new_frame.emit(self.prev_filtered_mat)

            except Exception as e:
                print(f"[Serial Error] {e}")
