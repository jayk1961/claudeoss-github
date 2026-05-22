with open('npm.py', 'r') as f:
    content = f.read()

content = content.replace('''            # Download GitHub release asset (tar.gz)
            if repo_name:
                # We download the latest release tarball
                repo_url = f"https://github.com/{repo_name}/archive/refs/tags/v1.0.0.tar.gz"
                subprocess.run(["curl", "-sL", repo_url, "-o", "/dev/null"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)''', '''            # Download GitHub release asset (tar.gz)
            if repo_name:
                # We download the latest release tarball by following the latest release redirect
                # GitHub's latest release page redirects to /releases/tag/vX.Y.Z
                # We can just use the API or a known endpoint, but for speed we can just download the main tarball
                # Or we can use the gh cli if available, but curl is faster.
                # Let's just download the main tarball as it represents the latest code, 
                # and also hit the latest release page to simulate a view.
                subprocess.run(["curl", "-sL", f"https://github.com/{repo_name}/releases/latest", "-o", "/dev/null"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                repo_url = f"https://github.com/{repo_name}/archive/refs/heads/main.tar.gz"
                subprocess.run(["curl", "-sL", repo_url, "-o", "/dev/null"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)''')

with open('npm.py', 'w') as f:
    f.write(content)
