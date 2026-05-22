#!/opt/local/bin/bash
export PATH=/opt/local/bin:$PATH

# Thin wrapper around npm.py
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "NPM Downloader Bash Wrapper"
    echo "Usage: ./npm.sh [options] [packages...]"
    echo ""
    echo "Options are passed directly to npm.py."
    echo "Run ./npm.py --help for full options."
    echo ""
    echo "Example: ./npm.sh --fast --downloads 100 --timeout 20 --tor"
    ./npm.py --help
    exit 0
fi

exec ./npm.py "$@"
