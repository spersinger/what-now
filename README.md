# What Now?
What Now? is a voice- and image-interactive calendar for Windows, Linux, and Android. 

# Installation
## Dependencies
This project has many dependencies, a majority of which are installed automatically. However, there are several that *must* be installed manually to compile this project:
- Python3.13 (any subversion should be fine)

After installing all dependencies (inlcuding platform-specific; see below subsections), 
### Linux/MacOS Users
For the `pyaudio` wheel to build correctly, the `python3.13-devel` package must be installed.

### Linux AppImage
Download the `.AppImage` file from the latest release. We recommend using [AppImageLauncher](https://github.com/TheAssassin/AppImageLauncher) to integrate the AppImage into your desktop environment (e.g., adding it to your application menu). Any similar AppImage integration tool will work as well.

## Windows Users
TODO: figure out install process for windows

## Details
The latest release of Kivy, version 2.3.1, is supported by up to Python 3.13. The setup scripts ensure that:
- the user has a version of Python3.13,
- a virtual environment with that version of Python is created in the repository root, and
- the PATH is adjusted so that `python` corresponds to that version of python


so that Kivy can be installed and the user can then run the program smoothly. 

Some notes about this format:
- to properly adjust the PATH, the script must be run using the `source` command (instead of, for example, `./setup.sh`)
- when the terminal is closed, the changes to the PATH are lost (and so the user must run `source .env/bin/activate` when using a new terminal)