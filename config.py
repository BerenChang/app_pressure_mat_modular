# === CONFIGURATION ===
SERIAL_PORT = "COM6"  # Change to your port
BAUD_RATE = 115200
MAT_WIDTH = 56
MAT_HEIGHT = 28
CANVA_WIDTH = int(560*1.5)
CANVA_HEIGHT = int(280*1.5)
MAT_SIZE = MAT_WIDTH * MAT_HEIGHT
START_READING_COMMAND = "start_reading"
GET_CAL_VALS_COMMAND  = "get_cal_vals"
VERIFICATION_WIDTH = 4
VERIFICATION_SEQUENCE = [255, 254, 254, 255]
TRACE_DURATION = 2.0 # seconds
BLOB_RADIUS = 30
BLOB_SIGMA = 10
THRESHOLDS = [18, 19, 20, 24, 27, 30, 40, 45, 50]
COLORS = [
    (200, 200, 200),  # gray
    (135, 206, 235),  # sky blue
    (0, 0, 255),      # blue
    
    # Greens
    (0, 200, 0),      # darker green
    (0, 255, 0),      # bright green
    
    # Yellows
    (255, 255, 153),  # light yellow
    (255, 255, 0),    # pure yellow
    
    # Reds
    # (255, 153, 153),  # light red
    (255, 51, 51),    # medium red
    (255, 0, 0),      # bright red
]
# THRESHOLDS = [18, 19, 20, 21, 23, 24, 27, 30, 33, 35, 37, 40, 43, 47, 50]
# COLORS = [
#     # Gray (3 shades)
#     (200, 200, 200),
#     (150, 150, 150),
#     (100, 100, 100),

#     # Blue (3 shades)
#     (135, 206, 235),  # sky blue
#     (0, 0, 255),      # blue
#     (0, 0, 180),      # dark blue

#     # Green (3 shades)
#     (0, 255, 0),      # green
#     (50, 205, 50),    # lime green
#     (0, 128, 0),      # dark green

#     # Yellow (3 shades)
#     (255, 255, 0),    # yellow
#     (255, 215, 0),    # gold
#     (204, 204, 0),    # olive yellow

#     # Red (3 shades)
#     (255, 0, 0),      # red
#     (220, 20, 60),    # crimson
#     (139, 0, 0)       # dark red
# ]