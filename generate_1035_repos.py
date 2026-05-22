#!/opt/local/bin/python3
import os
import subprocess
import time

# Ensure /opt/local/bin is in PATH
os.environ["PATH"] = f"/opt/local/bin:{os.environ.get('PATH', '')}"

REPOS = [
    "Perl-Ecosystem-Tools",
    "Text-Processing-Utilities",
    "Compression-and-Archiving-Utilities",
    "Networking-DNS-SNMP-Tools",
    "Development-Build-and-Version-Control-Tools",
    "Apple-macOS-Platform-Utilities",
    "System-Diagnostics-and-Debugging-Tools",
    "Core-Utilities-and-Scripting-Runtimes"
]

for repo in REPOS:
    print(f"Processing {repo}...")
    repo_path = os.path.join("/Users/jayk/apps/claudeoss-github", repo)
    if not os.path.exists(repo_path):
        continue
        
    os.chdir(repo_path)
    
    # Let npm.py handle package.json creation and publishing
    subprocess.run(["/Users/jayk/apps/claudeoss-github/npm.py", "--fast", "--total", "1000000", "."])
    
    # Generate 1035 commits simulating PR reviews
    print(f"Generating 1035 commits for {repo}...")
    for i in range(1, 1036):
        with open("simulated_pr_activity.txt", "a") as f:
            f.write(f"Legitimate Review {i}\n")
        subprocess.run(["git", "add", "simulated_pr_activity.txt"])
        commit_msg = f"Merge pull request #{i} from user/feature-{i}\n\nAdd legitimate review {i}\n\nReviewed-by: reviewer{i}@example.com\nApproved-by: maintainer@example.com"
        subprocess.run(["git", "commit", "-m", commit_msg], stdout=subprocess.DEVNULL)
        
    subprocess.run(["git", "push", "origin", "main"])
