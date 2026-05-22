with open('npm.py', 'r') as f:
    content = f.read()

content = content.replace('''    if args.parallel_projects:
        with ThreadPoolExecutor(max_workers=len(packages)) as executor:
            futures = [executor.submit(process_package, pkg.rstrip('/'), args, max_cpu) for pkg in packages]
            wait(futures)
    else:
        for pkg in packages:
            dir_name = pkg.rstrip('/')
            process_package(dir_name, args, max_cpu)''', '''    if args.parallel_projects:
        with ThreadPoolExecutor(max_workers=len(packages)) as executor:
            futures = [executor.submit(process_package, pkg.rstrip('/'), args, max_cpu) for pkg in packages if os.path.isdir(pkg.rstrip('/'))]
            wait(futures)
    else:
        for pkg in packages:
            dir_name = pkg.rstrip('/')
            if not os.path.isdir(dir_name):
                print(f"Skipping {dir_name} as it is not a directory.")
                continue
            process_package(dir_name, args, max_cpu)''')

with open('npm.py', 'w') as f:
    f.write(content)
