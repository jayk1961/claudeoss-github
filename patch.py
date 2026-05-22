with open('npm.py', 'r') as f:
    content = f.read()
content = content.replace('def process_package(dir_name, args, max_cpu):', 'def process_package(dir_name, args, max_cpu):\n    print(f"Processing {dir_name}")')
with open('npm.py', 'w') as f:
    f.write(content)
