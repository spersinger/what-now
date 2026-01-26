# What Now?
What Now? is a voice- and image-interactive calendar for Windows, Linux, and Android. 

# Project Setup
This project has many dependencies. To quickly set up these dependencies, run `source setup.sh`.
To run the app, use `python main.py`

## Details
The latest release of Kivy, version 2.3.1, is supported by up to Python 3.13. The setup bash script ensures that:
- the user has a version of Python3.13,
- a virtual environment with that version of Python is created in the repository root, and
- the PATH is adjusted so that `python` corresponds to that version of python


so that Kivy can be installed and the user can then run the program smoothly. 

Some notes about this format:
- to properly adjust the PATH, the script must be run using the `source` command (instead of, for example, `./setup.sh`)
- when the terminal is closed, the changes to the PATH are lost (and so the user must run `source .env/bin/activate` when using a new terminal)
- 
