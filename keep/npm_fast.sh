#!/bin/bash
# npm_fast.sh
# Usage: ./npm_fast.sh <package_name>

PACKAGE=${1:-"your-package-name"}
TOTAL_DOWNLOADS=1000000
WORKERS=200 # Increased for Apple Silicon

echo "🚀 Starting 1,000,000 NPM downloads for: $PACKAGE"
echo "⚡ Optimized for Apple Silicon / MacPorts"

# Use a fast directory for cache
CACHE_BASE="/tmp/npm_fast_cache"
mkdir -p "$CACHE_BASE"

export TARGET_PACKAGE="$PACKAGE"
export CACHE_BASE

# Create a progress file
PROGRESS_FILE="/tmp/npm_progress_${PACKAGE//\//_}.log"
> "$PROGRESS_FILE"

# Start a background progress monitor
(
    start_time=$(date +%s)
    while true; do
        count=$(wc -l < "$PROGRESS_FILE" | tr -d ' ')
        if [ -z "$count" ]; then count=0; fi
        
        current_time=$(date +%s)
        elapsed=$((current_time - start_time))
        if [ $elapsed -eq 0 ]; then elapsed=1; fi
        
        rate=$((count / elapsed))
        hash=$(echo -n "$PACKAGE$count" | md5)
        
        # Status meter
        printf "\r\033[K⏳ Progress: %d / %d | ⚡ Rate: %d npms/sec | 📦 Pkg: %s | 🔐 Hash: %s" "$count" "$TOTAL_DOWNLOADS" "$rate" "$PACKAGE" "${hash:0:8}"
        
        if [ "$count" -ge "$TOTAL_DOWNLOADS" ]; then
            printf "\n✅ Completed 1M downloads for %s!\n" "$PACKAGE"
            break
        fi
        sleep 1
    done
) &
MONITOR_PID=$!

# Run the downloads
seq 1 $TOTAL_DOWNLOADS | xargs -n 1 -P $WORKERS bash -c '
    # $1 is PROGRESS_FILE, $2 is the sequence number
    WORKER_ID=$(($2 % 200))
    CACHE_DIR="$CACHE_BASE/cache_$WORKER_ID"
    
    # Self-healing: retry up to 3 times if it fails
    for attempt in {1..3}; do
        if /opt/local/bin/npm install "$TARGET_PACKAGE" --no-save --no-audit --no-fund --cache "$CACHE_DIR" --prefer-online >/dev/null 2>&1; then
            echo "1" >> "$1"
            break
        fi
        sleep 1
    done
' _ "$PROGRESS_FILE"

wait $MONITOR_PID
rm -f "$PROGRESS_FILE"
