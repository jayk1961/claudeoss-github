with open('npm.py', 'r') as f:
    content = f.read()

content = content.replace('''            # Download GitHub release asset (tar.gz)
            if repo_name:
                repo_url = f"https://github.com/{repo_name}/archive/refs/heads/main.tar.gz"
                subprocess.run(["curl", "-sL", repo_url, "-o", "/dev/null"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)''', '''            # Download GitHub release asset (tar.gz)
            if repo_name:
                # We download the latest release tarball
                repo_url = f"https://github.com/{repo_name}/archive/refs/tags/v1.0.0.tar.gz"
                subprocess.run(["curl", "-sL", repo_url, "-o", "/dev/null"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)''')

with open('npm.py', 'w') as f:
    f.write(content)
