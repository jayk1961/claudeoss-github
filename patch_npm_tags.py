with open('npm.py', 'r') as f:
    content = f.read()

content = content.replace('subprocess.run(["git", "push"], cwd=dir_name, capture_output=True)', 'subprocess.run(["git", "push", "--follow-tags"], cwd=dir_name, capture_output=True)')

with open('npm.py', 'w') as f:
    f.write(content)
