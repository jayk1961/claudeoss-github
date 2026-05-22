with open('npm.py', 'r') as f:
    content = f.read()

content = content.replace('elif "EPUBLISHCONFLICT" in res.stderr or "previously published" in res.stderr:', 'elif "E403" in res.stderr or "Forbidden" in res.stderr:\n            print(f"⚠️  Warning: Cannot publish {pkg_name} because of 2FA or permission issues.")\n        elif "EPUBLISHCONFLICT" in res.stderr or "previously published" in res.stderr:')

with open('npm.py', 'w') as f:
    f.write(content)
