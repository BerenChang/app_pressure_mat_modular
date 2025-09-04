from PIL import Image

img = Image.open("logo.jpg")
img.save(
    "logo.ico",
    sizes=[(256,256), (128,128), (64,64), (32,32), (16,16)]
)