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
    echo "virtual environment created ($(pwd)/.env)"

    # add .env/bin to PATH so that python and pip versions match env spec
    export PATH=$(pwd)/.env/bin:$PATH
    echo "exported venv to current path (changes only persist in this terminal instance)"

    # install kivy
    pip install "kivy[full]"
    echo "installed kivy."
}

main() {
    is_sourced || (echo "This file must be sourced to work correctly (\`source setup.sh\`)." && exit 1) &&
        (python3.13 --version ||
            (echo "This project requires Python3.13 to install Kivy with. Please install that version and try again." && exit 2) &&
            setup_env)

}

main
