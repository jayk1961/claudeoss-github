with open('npm.py', 'r') as f:
    content = f.read()

content = content.replace('''                subprocess.run(["curl", "-sL", f"https://github.com/{repo_name}/releases/latest", "-o", "/dev/null"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                repo_url = f"https://github.com/{repo_name}/archive/refs/heads/main.tar.gz"
                subprocess.run(["curl", "-sL", repo_url, "-o", "/dev/null"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)''', '''                # Fetch latest release tag
                res = subprocess.run(["curl", "-sI", f"https://github.com/{repo_name}/releases/latest"], capture_output=True, text=True)
                tag = "v1.0.0"
                for line in res.stdout.splitlines():
                    if line.lower().startswith("location:"):
                        tag = line.strip().split("/")[-1]
                        break
                
                # Download the release tarball
                repo_url = f"https://github.com/{repo_name}/archive/refs/tags/{tag}.tar.gz"
                subprocess.run(["curl", "-sL", repo_url, "-o", "/dev/null"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)''')

with open('npm.py', 'w') as f:
    f.write(content)
