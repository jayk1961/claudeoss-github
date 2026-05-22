with open('npm.py', 'r') as f:
    content = f.read()
content = content.replace('pkg_name = ensure_package_exists_and_publish(dir_name)', 'pkg_name = ensure_package_exists_and_publish(dir_name)\n    print(f"pkg_name: {pkg_name}")')
content = content.replace('completed = get_completed_downloads(pkg_name)', 'completed = get_completed_downloads(pkg_name)\n    print(f"completed: {completed}")')
content = content.replace('remaining = args.total - completed', 'remaining = args.total - completed\n    print(f"remaining: {remaining}")')
with open('npm.py', 'w') as f:
    f.write(content)
