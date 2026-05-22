#!/opt/local/bin/python3
import argparse
import os
import sys
import time
import subprocess
import multiprocessing
import hashlib
import psycopg2
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
import shutil
import json
import random

os.environ["PATH"] = f"/opt/local/bin:{os.environ.get('PATH', '')}"

DB_HOST = "localhost"
DB_USER = "postgres"
DB_PASS = "ast1973"
DB_NAME = "postgres"

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/118.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
]

def init_db():
    try:
        conn = psycopg2.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, dbname=DB_NAME)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS npm_downloads (
                package_name VARCHAR(255) PRIMARY KEY,
                downloads INT DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database init error: {e}")
        sys.exit(1)

def get_completed_downloads(package_name):
    try:
        conn = psycopg2.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, dbname=DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT downloads FROM npm_downloads WHERE package_name = %s", (package_name,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row[0] if row else 0
    except Exception:
        return 0

def update_completed_downloads(package_name, count):
    try:
        conn = psycopg2.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, dbname=DB_NAME)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO npm_downloads (package_name, downloads, last_updated)
            VALUES (%s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (package_name) DO UPDATE
            SET downloads = npm_downloads.downloads + %s,
                last_updated = CURRENT_TIMESTAMP;
        """, (package_name, count, count))
        cursor.close()
        conn.close()
    except Exception:
        pass

def ensure_package_exists_and_publish(dir_name):
    pkg_path = os.path.join(dir_name, "package.json")
    pkg_name = os.path.basename(os.path.abspath(dir_name)).lower().replace(" ", "-")

    if not os.path.exists(pkg_path):
        pkg_data = {
            "name": pkg_name,
            "version": "1.0.0",
            "description": f"Auto-generated package for {pkg_name}"
        }
        with open(pkg_path, "w") as f:
            json.dump(pkg_data, f, indent=2)
    else:
        with open(pkg_path, "r") as f:
            try:
                pkg_data = json.load(f)
                pkg_name = pkg_data.get("name", pkg_name)
            except:
                pass

    # Bump version
    res = subprocess.run(["/opt/local/bin/npm", "version", "patch"], cwd=dir_name, capture_output=True, text=True)
    new_version = res.stdout.strip() if res.returncode == 0 else "v1.0.1"
    print(f"[{pkg_name}] Bumped version to {new_version}")

    # Push to GitHub
    if os.path.exists(os.path.join(dir_name, ".git")):
        subprocess.run(["git", "add", "package.json"], cwd=dir_name, capture_output=True)
        subprocess.run(["git", "commit", "-m", f"chore: bump version to {new_version} for npm publish"], cwd=dir_name, capture_output=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=dir_name, capture_output=True)
        print(f"[{pkg_name}] Pushed to GitHub")

    # Publish - do not capture output so it can prompt for OTP/browser if needed
    print(f"[{pkg_name}] Publishing to npm...")
    res = subprocess.run(["/opt/local/bin/npm", "publish", "--access", "public"], cwd=dir_name)
    if res.returncode != 0:
        print(f"⚠️  Warning: npm publish failed for {pkg_name} with code {res.returncode}.")

    return pkg_name

def worker_task(package_name, worker_id, fast_mode, local_dir=None, repo_name=None, use_tor=False):
    cache_dir = f"/tmp/npm_cache_{worker_id}"
    work_dir = f"/tmp/npm_work_{worker_id}"
    os.makedirs(cache_dir, exist_ok=True)
    os.makedirs(work_dir, exist_ok=True)

    backoffs = [0.5, 2, 5] if fast_mode else [1, 5, 20]
    target = package_name if not local_dir else local_dir

    for wait_time in backoffs:
        try:
            # Download npm package
            cmd = [
                "/opt/local/bin/npm", "install", target,
                "--cache", cache_dir,
                "--no-save", "--no-audit", "--no-fund", "--prefer-online", "--loglevel=error"
            ]
            
            env = os.environ.copy()
            if use_tor:
                env["HTTP_PROXY"] = "socks5h://127.0.0.1:9050"
                env["HTTPS_PROXY"] = "socks5h://127.0.0.1:9050"
                
            result = subprocess.run(cmd, cwd=work_dir, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, env=env)

            # Download GitHub release asset (tar.gz)
            if repo_name:
                ua = random.choice(USER_AGENTS)
                curl_cmd = ["curl", "-sI", "-A", ua]
                if use_tor:
                    curl_cmd.extend(["--socks5-hostname", "127.0.0.1:9050"])
                curl_cmd.append(f"https://github.com/{repo_name}/releases/latest")
                
                res = subprocess.run(curl_cmd, capture_output=True, text=True)
                tag = "v1.0.0"
                for line in res.stdout.splitlines():
                    if line.lower().startswith("location:"):
                        tag = line.strip().split("/")[-1]
                        break
                repo_url = f"https://github.com/{repo_name}/archive/refs/tags/{tag}.tar.gz"
                
                dl_cmd = ["curl", "-sL", "-A", ua]
                if use_tor:
                    dl_cmd.extend(["--socks5-hostname", "127.0.0.1:9050"])
                dl_cmd.extend([repo_url, "-o", "/dev/null"])
                
                subprocess.run(dl_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            if result.returncode == 0:
                shutil.rmtree(os.path.join(work_dir, "node_modules"), ignore_errors=True)
                return "SUCCESS"
            else:
                if "E404" in result.stderr:
                    return "E404"
                time.sleep(wait_time)
        except Exception:
            time.sleep(wait_time)

    return "FAIL"

def process_package(dir_name, args, max_cpu):
    if os.path.isdir(dir_name):
        pkg_name = ensure_package_exists_and_publish(dir_name)
        res = subprocess.run(["git", "remote", "get-url", "origin"], cwd=dir_name, capture_output=True, text=True)
        repo_name = None
        if res.returncode == 0:
            url = res.stdout.strip()
            if "github.com" in url:
                repo_name = url.split("github.com/")[-1].replace(".git", "")
        local_dir = os.path.abspath(dir_name)
    else:
        pkg_name = dir_name
        local_dir = None
        repo_name = dir_name if "/" in dir_name else None

    workers = args.workers or args.parallel or args.jobs
    if not workers:
        workers = max_cpu * 10 if args.fast else max_cpu * 2

    completed = get_completed_downloads(pkg_name)
    remaining = args.downloads - completed

    if remaining <= 0:
        print(f"[{pkg_name}] Already reached {args.downloads} downloads.")
        return

    pkg_hash = hashlib.md5(pkg_name.encode()).hexdigest()[:8]
    start_time = time.time()
    batch_size = 10

    print(f"[{pkg_name}] Starting downloads (Target: {args.downloads}, Current: {completed}, Workers: {workers})")

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = set()
        for i in range(min(workers * 2, remaining)):
            futures.add(executor.submit(worker_task, pkg_name, i % workers, args.fast, local_dir, repo_name, args.tor))

        successful_in_batch = 0
        e404_count = 0

        while futures and completed < args.downloads:
            if args.timeout and (time.time() - start_time) > args.timeout:
                if successful_in_batch > 0:
                    update_completed_downloads(pkg_name, successful_in_batch)
                elapsed = time.time() - start_time
                rate = int((completed - (args.downloads - remaining)) / elapsed) if elapsed > 0 else 0
                sys.stdout.write(f"\r⏳ Progress: {completed} / {args.downloads} | ⚡ Rate: {rate} npms/sec | 📦 Pkg: {pkg_name} | 🔐 Hash: {pkg_hash} | 🔄 Instances: {workers} | Resume: from DB")
                sys.stdout.flush()
                print("\nTimeout reached. Exiting cleanly.")
                os._exit(0)

            done, not_done = wait(futures, timeout=1.0, return_when=FIRST_COMPLETED)
            futures = not_done

            for future in done:
                res = future.result()
                if res == "SUCCESS":
                    completed += 1
                    successful_in_batch += 1
                    if completed + len(futures) < args.downloads:
                        futures.add(executor.submit(worker_task, pkg_name, completed % workers, args.fast, local_dir, repo_name, args.tor))
                elif res == "E404":
                    e404_count += 1
                    if e404_count > 5:
                        print(f"\n[{pkg_name}] Package not found (E404). Stopping.")
                        for f in futures:
                            f.cancel()
                        return
                else:
                    if completed + len(futures) < args.downloads:
                        futures.add(executor.submit(worker_task, pkg_name, completed % workers, args.fast, local_dir, repo_name, args.tor))

                if successful_in_batch >= batch_size:
                    update_completed_downloads(pkg_name, successful_in_batch)
                    successful_in_batch = 0
                    elapsed = time.time() - start_time
                    rate = int((completed - (args.downloads - remaining)) / elapsed) if elapsed > 0 else 0
                    sys.stdout.write(f"\r⏳ Progress: {completed} / {args.downloads} | ⚡ Rate: {rate} npms/sec | 📦 Pkg: {pkg_name} | 🔐 Hash: {pkg_hash} | 🔄 Instances: {workers} | Resume: from DB")
                    sys.stdout.flush()

        if successful_in_batch > 0:
            update_completed_downloads(pkg_name, successful_in_batch)

    elapsed = time.time() - start_time
    rate = int((completed - (args.downloads - remaining)) / elapsed) if elapsed > 0 else 0
    sys.stdout.write(f"\r⏳ Progress: {completed} / {args.downloads} | ⚡ Rate: {rate} npms/sec | 📦 Pkg: {pkg_name} | 🔐 Hash: {pkg_hash} | 🔄 Instances: {workers} | Resume: from DB")
    sys.stdout.flush()
    print()

def main():
    parser = argparse.ArgumentParser(
        description="Fast NPM Downloader with PostgreSQL logging and Resume capability.",
        epilog="Example: ./npm.py --fast --downloads 100 --timeout 20"
    )
    parser.add_argument("packages", nargs="*", help="Directories to process. If none, uses all directories in cwd.")
    parser.add_argument("--fast", action="store_true", help="Enable fast mode (aggressive workers, faster backoffs)")
    parser.add_argument("--normal", action="store_true", help="Enable normal mode (conservative defaults)")
    parser.add_argument("--workers", type=int, help="Number of parallel workers")
    parser.add_argument("--parallel", type=int, help="Alias for --workers")
    parser.add_argument("--jobs", type=int, help="Alias for --workers")
    parser.add_argument("--downloads", "--total", type=int, default=1100000, help="Total downloads to achieve (default 1.1M)")
    parser.add_argument("--timeout", type=int, help="Timeout in seconds (for testing)")
    parser.add_argument("--parallel-projects", action="store_true", help="Process multiple projects concurrently")
    parser.add_argument("--tor", action="store_true", help="Use Tor proxy (socks5h://127.0.0.1:9050) for downloads")

    args = parser.parse_args()

    packages = args.packages
    if not packages:
        packages = [d for d in os.listdir('.') if os.path.isdir(d) and not d.startswith('.') and d not in ('node_modules', 'keep', 'mass_repos')]

    if not packages:
        print("No directories found in cwd.")
        sys.exit(1)

    max_cpu = multiprocessing.cpu_count()
    init_db()

    if args.parallel_projects:
        with ThreadPoolExecutor(max_workers=len(packages)) as executor:
            futures = [executor.submit(process_package, pkg.rstrip('/'), args, max_cpu) for pkg in packages]
            wait(futures)
    else:
        for pkg in packages:
            dir_name = pkg.rstrip('/')
            process_package(dir_name, args, max_cpu)

if __name__ == "__main__":
    main()
