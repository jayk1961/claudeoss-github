import subprocess
import os

cache_dir = "/tmp/npm_cache_0"
work_dir = "/tmp/npm_work_0"
os.makedirs(cache_dir, exist_ok=True)
os.makedirs(work_dir, exist_ok=True)

cmd = [
    "/opt/local/bin/npm", "install", "jayk1961/jayk",
    "--cache", cache_dir,
    "--no-save", "--no-audit", "--no-fund", "--prefer-online", "--loglevel=error"
]
result = subprocess.run(cmd, cwd=work_dir, capture_output=True, text=True)
print("returncode:", result.returncode)
print("stdout:", result.stdout)
print("stderr:", result.stderr)
