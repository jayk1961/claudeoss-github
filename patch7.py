with open('npm.py', 'r') as f:
    content = f.read()
content = content.replace('done, not_done = wait(futures, timeout=1.0, return_when=FIRST_COMPLETED)', 'print("waiting...")\n            done, not_done = wait(futures, timeout=1.0, return_when=FIRST_COMPLETED)\n            print(f"done: {len(done)}, not_done: {len(not_done)}")')
with open('npm.py', 'w') as f:
    f.write(content)
