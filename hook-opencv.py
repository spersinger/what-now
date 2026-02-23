from PyInstaller.utils.hooks import collect_dynamic_libs

binaries = collect_dynamic_libs('cv2')
hiddenimports = ['numpy']
