import re

with open('npm.py', 'r') as f:
    content = f.read()

# Update process_package to get repo_name
new_process = '''def process_package(dir_name, args, max_cpu):
    if os.path.isdir(dir_name):
        pkg_name = ensure_package_exists_and_publish(dir_name)
        # Get repo name from git
        res = subprocess.run(["git", "remote", "get-url", "origin"], cwd=dir_name, capture_output=True, text=True)
        repo_name = None
        if res.returncode == 0:
            url = res.stdout.strip()
            if "github.com" in url:
                repo_name = url.split("github.com/")[-1].replace(".git", "")
        
        local_dir = os.path.abspath(dir_name)
    else:
        pkg_name = dir_name
        local_dir = None
        repo_name = dir_name if "/" in dir_name else None'''

content = re.sub(r'def process_package\(dir_name, args, max_cpu\):.*?local_dir = None', new_process, content, flags=re.DOTALL)

# Update worker_task signature and call
content = content.replace('def worker_task(package_name, worker_id, fast_mode, local_dir=None):', 'def worker_task(package_name, worker_id, fast_mode, local_dir=None, repo_name=None):')
content = content.replace('futures.add(executor.submit(worker_task, pkg_name, i % workers, args.fast, local_dir))', 'futures.add(executor.submit(worker_task, pkg_name, i % workers, args.fast, local_dir, repo_name))')
content = content.replace('futures.add(executor.submit(worker_task, pkg_name, completed % workers, args.fast, local_dir))', 'futures.add(executor.submit(worker_task, pkg_name, completed % workers, args.fast, local_dir, repo_name))')

# Update worker_task to download release asset
new_worker_download = '''            # Download GitHub release asset (tar.gz)
            if repo_name:
                repo_url = f"https://github.com/{repo_name}/archive/refs/heads/main.tar.gz"
                subprocess.run(["curl", "-sL", repo_url, "-o", "/dev/null"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)'''

content = re.sub(r'            # Download GitHub release asset \(tar\.gz\).*?subprocess\.run\(\["curl", "-sL", repo_url, "-o", "/dev/null"\], stdout=subprocess\.DEVNULL, stderr=subprocess\.DEVNULL\)', new_worker_download, content, flags=re.DOTALL)

with open('npm.py', 'w') as f:
    f.write(content)
