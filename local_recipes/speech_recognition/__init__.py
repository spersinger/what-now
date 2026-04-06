# pythonforandroid/recipes/speechrecognition/__init__.py
from pythonforandroid.recipe import PythonRecipe


class SpeechRecognitionRecipe(PythonRecipe):
    """
    Recipe for the SpeechRecognition Python package.
    Provides speech-to-text via multiple backends (Google, Vosk, Sphinx, etc.)
    """
    version = "3.16.0"
    url = 'https://github.com/Uberi/speech_recognition/archive/refs/tags/{version}.tar.gz'
    site_packages_name = "speech_recognition"
    name = "speech_recognition"

    # audio backend handled separately (e.g. pyaudio or android-specific)
    depends = ["python3", "setuptools", "requests", "pyaudio"]
    
    def install_python_package(self, arch):
        self.install_python_package_via_pip(arch)




recipe = SpeechRecognitionRecipe()