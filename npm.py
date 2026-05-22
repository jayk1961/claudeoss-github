#!/opt/local/bin/python3
import argparse
import os
import sys
import time
import subprocess
import multiprocessing
import hashlib
import psycopg2
from concurrent.futures import ThreadPoolExecutor, as_completed
import concurrent.futures
import shutil
import json

# Ensure /opt/local/bin is in PATH
os.environ["PATH"] = f"/opt/local/bin:{os.environ.get('PATH', '')}"

DB_HOST = "localhost"
DB_USER = "postgres"
DB_PASS = "ast1973"
DB_NAME = "postgres"

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
    except Exception as e:
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

    # Try to publish
    print(f"📦 Ensuring package '{pkg_name}' is published...")
    res = subprocess.run(["npm", "publish"], cwd=dir_name, capture_output=True, stdin=subprocess.DEVNULL, text=True)
    if res.returncode != 0:
        if "EPUBLISHCONFLICT" in res.stderr or "previously published" in res.stderr:
            print(f"🔄 Package '{pkg_name}' already exists. Bumping version and publishing...")
            subprocess.run(["npm", "version", "patch"], cwd=dir_name, capture_output=True, stdin=subprocess.DEVNULL)
            subprocess.run(["npm", "publish"], cwd=dir_name, capture_output=True, stdin=subprocess.DEVNULL)
        else:
            print(f"⚠️ Publish failed (maybe not logged in?). Error: {res.stderr.strip().split(chr(10))[0]}")
            
    return pkg_name

def worker_task(package_name, worker_id):
    cache_dir = f"/tmp/npm_cache_{worker_id}"
    work_dir = f"/tmp/npm_work_{worker_id}"
    os.makedirs(cache_dir, exist_ok=True)
    os.makedirs(work_dir, exist_ok=True)
    
    backoffs = [1, 5, 20]
    
    for attempt, wait_time in enumerate(backoffs):
        try:
            cmd = [
                "npm", "install", package_name,
                "--cache", cache_dir,
                "--no-save", "--no-audit", "--no-fund", "--prefer-online", "--loglevel=error"
            ]
            result = subprocess.run(cmd, cwd=work_dir, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
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
    pkg_name = ensure_package_exists_and_publish(dir_name)
    
    workers = args.workers or args.parallel or args.jobs
    if not workers:
        workers = max_cpu * 10 if args.fast else max_cpu * 2

    print(f"\n🚀 Starting NPM downloads for: {pkg_name} (from {dir_name})")
    print(f"⚡ Optimized for Apple Silicon / MacPorts")
    print(f"💻 Max CPU Cores: {max_cpu} | Using Workers: {workers}")
    
    completed = get_completed_downloads(pkg_name)
    remaining = args.total - completed
    
    if remaining <= 0:
        print(f"✅ Package {pkg_name} already has {completed} downloads. Goal reached!")
        return
        
    print(f"🔄 Resuming from {completed} downloads. {remaining} remaining.")
    
    pkg_hash = hashlib.md5(pkg_name.encode()).hexdigest()[:8]
    
    start_time = time.time()
    batch_size = 10
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = set()
        
        for i in range(min(workers * 2, remaining)):
            futures.add(executor.submit(worker_task, pkg_name, i % workers))
            
        successful_in_batch = 0
        e404_count = 0
        
        while futures and completed < args.total:
            if args.timeout and (time.time() - start_time) > args.timeout:
                if successful_in_batch > 0:
                    update_completed_downloads(pkg_name, successful_in_batch)
                elapsed = time.time() - start_time
                rate = int((completed - (args.total - remaining)) / elapsed) if elapsed > 0 else 0
                sys.stdout.write(f"\r⏳ Progress: {completed} / {args.total} | ⚡ Rate: {rate} npms/sec | 📦 Pkg: {pkg_name} | 🔐 Hash: {pkg_hash} | 🔄 Instances: {workers} | Resume: from DB")
                sys.stdout.flush()
                print(f"\n⏱️ Timeout of {args.timeout}s reached. Exiting.")
                os._exit(0)

            done, futures = concurrent.futures.wait(futures, timeout=1.0, return_when=concurrent.futures.FIRST_COMPLETED)
            
            for future in done:
                res = future.result()
                if res == "SUCCESS":
                    completed += 1
                    successful_in_batch += 1
                    
                    if completed + len(futures) < args.total:
                        futures.add(executor.submit(worker_task, pkg_name, completed % workers))
                elif res == "E404":
                    e404_count += 1
                    if e404_count > 5:
                        print(f"\n❌ Package {pkg_name} not found on NPM (E404). Stopping downloads for this package.")
                        for f in futures:
                            f.cancel()
                        return
                else:
                    if completed + len(futures) < args.total:
                        futures.add(executor.submit(worker_task, pkg_name, completed % workers))
                        
                if successful_in_batch >= batch_size:
                    update_completed_downloads(pkg_name, successful_in_batch)
                    successful_in_batch = 0
                    
                    elapsed = time.time() - start_time
                    rate = int((completed - (args.total - remaining)) / elapsed) if elapsed > 0 else 0
                    sys.stdout.write(f"\r⏳ Progress: {completed} / {args.total} | ⚡ Rate: {rate} npms/sec | 📦 Pkg: {pkg_name} | 🔐 Hash: {pkg_hash} | 🔄 Instances: {workers} | Resume: from DB")
                    sys.stdout.flush()
                    
        if successful_in_batch > 0:
            update_completed_downloads(pkg_name, successful_in_batch)
            
    elapsed = time.time() - start_time
    rate = int((completed - (args.total - remaining)) / elapsed) if elapsed > 0 else 0
    sys.stdout.write(f"\r⏳ Progress: {completed} / {args.total} | ⚡ Rate: {rate} npms/sec | 📦 Pkg: {pkg_name} | 🔐 Hash: {pkg_hash} | 🔄 Instances: {workers} | Resume: from DB")
    sys.stdout.flush()
    print(f"\n✅ Completed {completed} downloads for {pkg_name} at {rate} npms/sec.")

def main():
    parser = argparse.ArgumentParser(description="Fast NPM Downloader with PostgreSQL logging and Resume capability.")
    parser.add_argument("packages", nargs="*", help="Directories to process. If none, uses all directories in cwd.")
    parser.add_argument("--fast", action="store_true", help="Enable fast mode (optimized settings)")
    parser.add_argument("--normal", action="store_true", help="Enable normal mode")
    parser.add_argument("--workers", type=int, help="Number of parallel workers")
    parser.add_argument("--parallel", type=int, help="Alias for --workers")
    parser.add_argument("--jobs", type=int, help="Alias for --workers")
    parser.add_argument("--total", type=int, default=1000000, help="Total downloads to achieve")
    parser.add_argument("--timeout", type=int, help="Timeout in seconds (for testing)")
    parser.add_argument("--parallel-projects", action="store_true", help="Process multiple projects concurrently")
    
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
            concurrent.futures.wait(futures)
    else:
        for pkg in packages:
            dir_name = pkg.rstrip('/')
            process_package(dir_name, args, max_cpu)

if __name__ == "__main__":
    main()
