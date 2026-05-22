with open('npm.py', 'r') as f:
    content = f.read()
content = content.replace('while futures and completed < args.total:', 'print(f"futures: {len(futures)}")\n        while futures and completed < args.total:')
with open('npm.py', 'w') as f:
    f.write(content)
