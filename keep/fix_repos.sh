#!/bin/bash

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

for repo in "${REPOS[@]}"; do
    echo "Fixing $repo..."
    cd "/Users/jayk/apps/claudeoss-github/$repo" || continue
    
    # Remove corrupted .git directory
    rm -rf .git
    
    # Re-initialize explicitly with main branch
    git init -b main
    git remote add origin "https://github.com/jayk1961/$repo.git"
    git fetch origin
    
    # Reset to remote main
    git reset --hard origin/main
    
    # Set upstream
    git branch --set-upstream-to=origin/main main
done
