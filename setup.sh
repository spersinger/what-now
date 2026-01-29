#! /usr/bin/bash

# Helper function (from https://stackoverflow.com/questions/2683279/how-to-detect-if-a-script-is-being-sourced)
is_sourced() {
    if [ -n "$ZSH_VERSION" ]; then
        case $ZSH_EVAL_CONTEXT in *:file:*) return 0 ;; esac
    else # Add additional POSIX-compatible shell names here, if needed.
        case ${0##*/} in dash | -dash | bash | -bash | ksh | -ksh | sh | -sh) return 0 ;; esac
    fi
    return 1 # NOT sourced.
}

setup_env() {
    # create the virtual environment with the correct python version
    python3.13 -m venv .env
    echo -e "\nvirtual environment created ($(pwd)/.env)"

    # add .env/bin to PATH so that python and pip versions match env spec
    export PATH=$(pwd)/.env/bin:$PATH
    echo -e "exported venv to current path (changes only persist in this terminal instance)\n"

    # install kivy
    pip install -r requirements.txt
    echo -e "\ninstalled requiremnets."
}

main() {

    if [ -d ".env" ]; then
        echo -e "\nThis file has already been sourced."
        echo -e "To re-enable the virtual environment, use \`source .env/bin/activate\`."
        echo -e "If there are still issues, delete the .env folder and re-source this file in a new terminal."
        echo -e "Otherwise, if there are still issues, re-cloning the repo is always an option."
        return 0
    fi

    is_sourced ||
        (echo "This file must be sourced to work correctly (\`source setup.sh\`)." && exit 1) &&
        (
            command -v python3.13 ||
                (echo "This project requires Python3.13 to install Kivy with. Please install that version and try again." && exit 2) &&
                setup_env
        )
}

main
