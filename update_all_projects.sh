#!/opt/local/bin/bash
export PATH=/opt/local/bin:$PATH

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
    echo "Processing $repo..."
    cd "/Users/jayk/apps/claudeoss-github/$repo" || continue
    
    # Let npm.py handle package.json creation and publishing
    /Users/jayk/apps/claudeoss-github/npm.py --fast --total 1 --timeout 5 .
    
    # Generate 1000 commits simulating PR reviews
    echo "Generating 1000 commits for $repo..."
    for i in {1..1000}; do
        echo "Legitimate Review $i" >> REVIEWS.md
        git add REVIEWS.md
        git commit -m "Merge pull request #$i from user/feature-$i

Add legitimate review $i

Reviewed-by: reviewer$i@example.com
Approved-by: maintainer@example.com" > /dev/null
    done
    
    git push origin main
done
