with open('npm.py', 'r') as f:
    content = f.read()
content = content.replace('while futures and completed < args.total:', '''while futures and completed < args.total:
            try:''')
content = content.replace('if successful_in_batch > 0:', '''except Exception as e:
                print(f"Exception: {e}")
                break
        if successful_in_batch > 0:''')
with open('npm.py', 'w') as f:
    f.write(content)
