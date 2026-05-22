with open('npm.py', 'r') as f:
    content = f.read()

content = content.replace('res = subprocess.run(["/opt/local/bin/npm", "version", "patch"], cwd=dir_name, capture_output=True, text=True)', 'res = subprocess.run(["/opt/local/bin/npm", "version", "patch"], cwd=dir_name, capture_output=True, text=True)\n    print(f"npm version patch: {res.returncode} {res.stdout} {res.stderr}")')

with open('npm.py', 'w') as f:
    f.write(content)
