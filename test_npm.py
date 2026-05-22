import subprocess
import os
os.environ["PATH"] = f"/opt/local/bin:{os.environ.get('PATH', '')}"
result = subprocess.run(["npm", "install", "Apple-macOS-Platform-Utilities", "--no-save", "--no-audit", "--no-fund", "--prefer-offline", "--loglevel=error"], capture_output=True, text=True)
print("RC:", result.returncode)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
