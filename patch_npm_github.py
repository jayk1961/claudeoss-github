with open('npm.py', 'r') as f:
    content = f.read()

content = content.replace('''def process_package(dir_name, args, max_cpu):
    pkg_name = ensure_package_exists_and_publish(dir_name)''', '''def process_package(dir_name, args, max_cpu):
    if os.path.isdir(dir_name):
        pkg_name = ensure_package_exists_and_publish(dir_name)
        # Check if package is actually published, if not, fallback to local dir for testing
        res = subprocess.run(["/opt/local/bin/npm", "view", pkg_name], capture_output=True, text=True)
        local_dir = os.path.abspath(dir_name) if res.returncode != 0 else None
    else:
        pkg_name = dir_name
        local_dir = None''')

content = content.replace('''    # Check if package is actually published, if not, fallback to local dir for testing
    res = subprocess.run(["/opt/local/bin/npm", "view", pkg_name], capture_output=True, text=True)
    local_dir = os.path.abspath(dir_name) if res.returncode != 0 else None''', '')

content = content.replace('''            if not os.path.isdir(dir_name):
                print(f"Skipping {dir_name} as it is not a directory.")
                continue''', '')

content = content.replace('''            futures = [executor.submit(process_package, pkg.rstrip('/'), args, max_cpu) for pkg in packages if os.path.isdir(pkg.rstrip('/'))]''', '''            futures = [executor.submit(process_package, pkg.rstrip('/'), args, max_cpu) for pkg in packages]''')

with open('npm.py', 'w') as f:
    f.write(content)
