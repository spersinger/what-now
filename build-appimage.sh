#!/bin/bash
set -e

APP_NAME="WhatNow"
APP_DIR="${APP_NAME}.AppDir"
ARCH=$(uname -m)

echo "Building AppImage for ${APP_NAME}..."

# Download Qwen model if not present
MODEL_URL="https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF/resolve/main/qwen2.5-coder-1.5b-instruct-q4_0.gguf"
MODEL_FILE="models/qwen2.5-coder-1.5b-instruct-q4_0.gguf"
if [ ! -f "${MODEL_FILE}" ]; then
    echo "Downloading Qwen model..."
    mkdir -p models
    wget -q --show-progress "${MODEL_URL}" -O "${MODEL_FILE}"
fi

# Check for appimagetool
if ! command -v appimagetool &> /dev/null; then
    echo "Installing appimagetool..."
    wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-${ARCH}.AppImage" -O appimagetool
    chmod +x appimagetool
    APPIMAGETOOL="./appimagetool"
else
    APPIMAGETOOL="appimagetool"
fi

# Build with PyInstaller unless SKIP_BUILD=1
if [ "$SKIP_BUILD" != "1" ]; then
    echo "Building with PyInstaller..."
    rm -rf dist/WhatNow build/WhatNow
    source .env/bin/activate
    pip install pyinstaller
    pyinstaller WhatNow.spec --clean
    deactivate
else
    echo "Skipping PyInstaller build (SKIP_BUILD=1)"
fi

# Update AppDir with new build
echo "Updating AppDir..."
rm -rf "${APP_DIR}/usr/bin/_internal"
rm -f "${APP_DIR}/usr/bin/${APP_NAME}"

cp -r "dist/${APP_NAME}/_internal" "${APP_DIR}/usr/bin/_internal"
cp "dist/${APP_NAME}/${APP_NAME}" "${APP_DIR}/usr/bin/${APP_NAME}"

# Make AppRun executable
chmod +x "${APP_DIR}/AppRun"

# Create AppImage
echo "Creating AppImage..."
ARCH=${ARCH} ${APPIMAGETOOL} "${APP_DIR}" "${APP_NAME}-${ARCH}.AppImage"

echo "Done! AppImage created: ${APP_NAME}-${ARCH}.AppImage"
