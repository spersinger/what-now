#!/usr/bin/env bash

# Install libv4l-devel (fedora, may be different, I didn't look)
#
pyinstaller \
  --noconfirm \
  --windowed \
  --name MyApp \
  --collect-binaries llama_cpp \
  --collect-binaries opencv-python \
  --additional-hooks-dir=. \
  --hidden-import=cv2 \
  --hidden-import=kivy \
  --hidden-import=kivy.core.window \
  --hidden-import=kivy.graphics \
  --hidden-import=kivy.uix.camera \
  --add-data "main.kv:." \
  --add-data "mic_white.png:." \
  --add-data "mic_green.png:." \
  src/main.py
