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
    depends = ["requests", "pyaudio"]
    patches = ["setup.patch"]
    hostpython_prerequisites = ["setuptools==82.0.1"]
    
    call_hostpython_via_targetpython = False


recipe = SpeechRecognitionRecipe()



"""
runtime error:

04-09 11:44:19.017  6530  6888 I python  :  Traceback (most recent call last):
04-09 11:44:19.017  6530  6888 I python  :    File "/home/lavender/School/spring-26/Senior-Project-2/what-now/.buildozer/android/app/main.py", line 216, in <module>
04-09 11:44:19.018  6530  6888 I python  :    File "/home/lavender/School/spring-26/Senior-Project-2/what-now/.buildozer/android/app/Voice.py", line 3, in <module>
04-09 11:44:19.018  6530  6888 I python  :    File "/home/lavender/School/spring-26/Senior-Project-2/what-now/.buildozer/android/platform/build-arm64-v8a/build/python-installs/test2/arm64-v8a/speech_recognition/__init__.py", line 40, in <module>
04-09 11:44:19.018  6530  6888 I python  :    File "/home/lavender/School/spring-26/Senior-Project-2/what-now/.buildozer/android/platform/build-arm64-v8a/build/other_builds/python3/arm64-v8a__ndk_target_21/python3/Lib/pathlib.py", line 1058, in read_text
04-09 11:44:19.018  6530  6888 I python  :    File "/home/lavender/School/spring-26/Senior-Project-2/what-now/.buildozer/android/platform/build-arm64-v8a/build/other_builds/python3/arm64-v8a__ndk_target_21/python3/Lib/pathlib.py", line 1044, in open
04-09 11:44:19.018  6530  6888 I python  :  FileNotFoundError: [Errno 2] No such file or directory: '/data/user/0/org.test.test2/files/app/_python_bundle/site-packages/speech_recognition/version.txt'
04-09 11:44:19.018  6530  6888 I python  : Python for android ended.
04-09 11:44:19.112  6530  6888 I BpBinder: onLastStrongRef automatically unlinking death recipients: <uncached descriptor>


can see stuff in private dirs via 
`adb shell` then
`run-as org.test.test2`
then whatever commands necessary

reason: 
.buildozer/android/platform/build-arm64-v8a/build/python-installs/test2/arm64-v8a/speech_recognition/__init__.py
    -> line 40: version = (some path stuff instead of a version number)

also:
.env/lib64/python3.13/site-packages/speech_recognition/__init__.py
    -> for some reason version is 3.14.5 instead of specified 3.16
        -> 3.14.5 was installed as part of env, version mismatch (.env updated)
    
try clean build?
"""