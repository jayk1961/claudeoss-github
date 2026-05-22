#!/bin/bash
# npm.sh
# Usage: ./npm.sh <package_name>

PACKAGE=${1:-"your-package-name"}
TOTAL_DOWNLOADS=1000000
WORKERS=100 # Number of parallel workers

echo "Starting $TOTAL_DOWNLOADS downloads for $PACKAGE using $WORKERS parallel workers..."
echo "Using /opt/local/bin/npm (No Homebrew)"

# Create a temporary directory for isolated caches to avoid lock contention
mkdir -p /tmp/npm_mass_dl

# Export the package name so the subshell can access it
export TARGET_PACKAGE="$PACKAGE"

# Generate sequence and pipe to xargs for parallel execution
# Passing the sequence number as $1 to bash -c avoids xargs command length limits
seq 1 $TOTAL_DOWNLOADS | xargs -n 1 -P $WORKERS bash -c '
    # Distribute across isolated cache directories based on worker ID
    WORKER_ID=$(($1 % 100))
    CACHE_DIR="/tmp/npm_mass_dl/cache_$WORKER_ID"
    
    # Execute NPM install using /opt path, forcing network requests
    /opt/local/bin/npm install "$TARGET_PACKAGE" --no-save --no-audit --no-fund --cache "$CACHE_DIR" --prefer-online >/dev/null 2>&1
    
    # Log progress
    if [ $(($1 % 5000)) -eq 0 ]; then
        echo "Completed $1 downloads..."
    fi
' _

echo "Finished 1M downloads."
