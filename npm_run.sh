#!/bin/bash
# npm_run.sh

REPOS=(
    "Perl-Ecosystem-Tools"
    "Text-Processing-Utilities"
    "Compression-and-Archiving-Utilities"
    "Networking-DNS-SNMP-Tools"
    "Development-Build-and-Version-Control-Tools"
    "Apple-macOS-Platform-Utilities"
    "System-Diagnostics-and-Debugging-Tools"
    "Core-Utilities-and-Scripting-Runtimes"
)

chmod +x ./npm_fast.sh

for repo in "${REPOS[@]}"; do
    echo "========================================================"
    echo "Starting 1M NPM downloads for $repo"
    echo "========================================================"
    ./npm_fast.sh "$repo"
done
