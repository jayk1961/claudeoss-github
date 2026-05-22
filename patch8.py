with open('npm.py', 'r') as f:
    content = f.read()
content = content.replace('res = future.result()', 'res = future.result()\n                print(f"res: {res}")')
with open('npm.py', 'w') as f:
    f.write(content)
