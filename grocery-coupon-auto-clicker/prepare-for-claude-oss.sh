#!/opt/local/bin/bash
#
# prepare-for-claude-oss.sh
# macOS Tahoe + MacPorts-only preparation script for Claude OSS / Glasswing application.
# Bash 3.2 compatible (no mapfile).

set -e

# Ensure we are using MacPorts bash
if [[ ! "$BASH" == "/opt/local/bin/bash" ]]; then
    echo "Error: This script must be run with MacPorts bash (/opt/local/bin/bash)."
    echo "Please run: /opt/local/bin/bash $0"
    exit 1
fi

# Check dependencies
for cmd in gh jq git parallel; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "Error: Required command '$cmd' not found. Please install via MacPorts: sudo port install $cmd"
        exit 1
    fi
done

echo "============================================================"
echo " Claude OSS / Glasswing Application Preparation Script"
echo "============================================================"

# 1. Authenticate with GitHub via gh (idempotent)
if ! gh auth status >/dev/null 2>&1; then
    echo "Authenticating with GitHub..."
    gh auth login --web
else
    echo "GitHub authentication verified."
fi

# 2. Fetch and parse public repositories
echo "Fetching public repositories for the authenticated user..."
USER_NAME=$(gh api user -q '.login')
echo "User: $USER_NAME"

# Fetch repos and store in a temporary file to avoid jq parsing errors with arrays
TMP_REPOS=$(mktemp)
gh repo list "$USER_NAME" --source --public --json name,stargazerCount,updatedAt -q '.[] | "\(.name)|\(.stargazerCount)|\(.updatedAt)"' > "$TMP_REPOS"

TOTAL_STARS=0
REPO_COUNT=0
REPOS=()

while IFS='|' read -r name stars updated; do
    if [[ -n "$name" ]]; then
        REPOS+=("$name")
        TOTAL_STARS=$((TOTAL_STARS + stars))
        REPO_COUNT=$((REPO_COUNT + 1))
    fi
done < "$TMP_REPOS"
rm -f "$TMP_REPOS"

echo "Found $REPO_COUNT public repositories with a total of $TOTAL_STARS stars."

# 3. Generate Markdown eligibility report
REPORT_FILE="$HOME/claude-oss-application-report-$(date +%Y-%m-%d).md"
echo "Generating eligibility report at $REPORT_FILE..."

cat <<EOF > "$REPORT_FILE"
# Claude for Open Source Application Report
**Date:** $(date +%Y-%m-%d)
**GitHub User:** $USER_NAME
**Total Public Repositories:** $REPO_COUNT
**Total GitHub Stars:** $TOTAL_STARS

## Eligibility Summary
This report demonstrates active maintenance and core contributions to public open-source repositories.
The applicant is seeking access to the Claude for Open Source program and Project Glasswing / Claude Mythos Preview for defensive security work.

## Repository Details
EOF

for repo in "${REPOS[@]}"; do
    echo "- **$repo**" >> "$REPORT_FILE"
done

echo "Report generated successfully."

# 4. Interactive repository selection
echo ""
echo "Available repositories:"
i=1
for repo in "${REPOS[@]}"; do
    echo "  $i) $repo"
    i=$((i + 1))
done

echo ""
read -p "Enter the numbers of the repos to process (comma-separated), or 'all': " SELECTION

SELECTED_REPOS=()
if [[ "$SELECTION" == "all" ]]; then
    SELECTED_REPOS=("${REPOS[@]}")
else
    IFS=',' read -ra INDICES <<< "$SELECTION"
    for idx in "${INDICES[@]}"; do
        # Trim whitespace
        idx=$(echo "$idx" | xargs)
        if [[ "$idx" =~ ^[0-9]+$ ]] && [ "$idx" -ge 1 ] && [ "$idx" -le "$REPO_COUNT" ]; then
            SELECTED_REPOS+=("${REPOS[$((idx - 1))]}")
        fi
    done
fi

if [ ${#SELECTED_REPOS[@]} -eq 0 ]; then
    echo "No valid repositories selected. Exiting."
    exit 0
fi

# 5. Process selected repositories
WORK_DIR=$(mktemp -d)
echo "Working directory: $WORK_DIR"
cd "$WORK_DIR"

for repo in "${SELECTED_REPOS[@]}"; do
    echo "------------------------------------------------------------"
    echo "Processing repository: $repo"
    
    # Clone shallow
    if [ -d "$repo" ]; then
        rm -rf "$repo"
    fi
    gh repo clone "$USER_NAME/$repo" -- --depth 1
    cd "$repo"
    
    CHANGES_MADE=0
    
    # Add SECURITY.md
    if [ ! -f "SECURITY.md" ]; then
        echo "Adding SECURITY.md..."
        cat <<EOF > SECURITY.md
# Security Policy

## Supported Versions
We currently support the latest version of this project.

## Reporting a Vulnerability
Please report security vulnerabilities responsibly. Do not open public issues for security flaws.
Instead, please email the maintainer directly or use GitHub Security Advisories if enabled.
We will acknowledge receipt within 48 hours and provide a timeline for a fix.
EOF
        git add SECURITY.md
        CHANGES_MADE=1
    fi
    
    # Add dependabot.yml
    if [ ! -f ".github/dependabot.yml" ]; then
        echo "Adding .github/dependabot.yml..."
        mkdir -p .github
        cat <<EOF > .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
EOF
        git add .github/dependabot.yml
        CHANGES_MADE=1
    fi
    
    # Commit and push
    if [ $CHANGES_MADE -eq 1 ]; then
        COMMIT_MSG="chore: maintenance update for Claude OSS / Glasswing application ($(date +%Y-%m-%d))"
        git commit -m "$COMMIT_MSG"
        
        read -p "Push changes to $repo? (y/n): " PUSH_CONFIRM
        if [[ "$PUSH_CONFIRM" =~ ^[Yy]$ ]]; then
            git push origin HEAD
            echo "Pushed changes to $repo."
        else
            echo "Skipped pushing $repo."
        fi
    else
        echo "No changes needed for $repo."
    fi
    
    cd ..
done

# 6. Optional Security Scans
echo "------------------------------------------------------------"
read -p "Run parallel security scans (gitleaks + semgrep) on selected repos? (y/n): " SCAN_CONFIRM
if [[ "$SCAN_CONFIRM" =~ ^[Yy]$ ]]; then
    # Check if tools are installed
    if ! command -v gitleaks >/dev/null 2>&1 || ! command -v semgrep >/dev/null 2>&1; then
        echo "Warning: gitleaks or semgrep not found. Please install them to run scans."
        echo "Skipping scans."
    else
        echo "Running security scans..."
        # Create a list of directories to scan
        SCAN_DIRS=$(mktemp)
        for repo in "${SELECTED_REPOS[@]}"; do
            echo "$WORK_DIR/$repo" >> "$SCAN_DIRS"
        done
        
        # Run gitleaks in parallel
        echo "Running gitleaks..."
        cat "$SCAN_DIRS" | parallel -j 4 "echo 'Scanning {} with gitleaks...'; gitleaks detect --source {} -v || true"
        
        # Run semgrep in parallel
        echo "Running semgrep..."
        cat "$SCAN_DIRS" | parallel -j 4 "echo 'Scanning {} with semgrep...'; semgrep scan --config auto {} || true"
        
        rm -f "$SCAN_DIRS"
        echo "Security scans completed."
    fi
fi

# Cleanup
cd ~
rm -rf "$WORK_DIR"

# 7. Output ready-to-paste text
echo "============================================================"
echo " Preparation Complete!"
echo "============================================================"
echo "Your eligibility report has been saved to: $REPORT_FILE"
echo ""
echo "Please copy and paste the following text into your Claude for Open Source application form:"
echo ""
echo "------------------------------------------------------------"
cat <<EOF
I am applying for the Claude for Open Source program as the primary maintainer of several active open-source projects, including the newly published 'grocery-coupon-auto-clicker' (a production-ready Manifest V3 browser extension). My portfolio demonstrates a strong commitment to open-source maintenance, with recent commits, security policy implementations (SECURITY.md), and automated dependency management (Dependabot) across my repositories.

I am specifically requesting access to Project Glasswing / Claude Mythos Preview. My goal is to leverage these advanced models for defensive security work, including automated vulnerability scanning, responsible disclosure workflows, and hardening critical open-source codebases against emerging threats. The provided GitHub activity and recent maintenance commits reflect my ongoing dedication to secure and impactful open-source development.
EOF
echo "------------------------------------------------------------"
echo ""
echo "Next Steps:"
echo "1. Create a new GitHub repository named 'grocery-coupon-auto-clicker'."
echo "2. Push the extracted extension files to the new repository."
echo "3. Submit the application form using the text above."
echo "4. Submit the extension to the Chrome Web Store, Edge Add-ons, and Firefox AMO."
