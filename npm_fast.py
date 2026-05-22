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
import tempfile

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

def worker_task(package_name, worker_id, max_retries=3):
    # Create a unique cache dir and working dir for this worker
    cache_dir = f"/tmp/npm_cache_{worker_id}"
    work_dir = f"/tmp/npm_work_{worker_id}"
    os.makedirs(cache_dir, exist_ok=True)
    os.makedirs(work_dir, exist_ok=True)
    
    for attempt in range(max_retries):
        try:
            # Run npm install in the worker's unique directory
            cmd = [
                "npm", "install", package_name,
                "--cache", cache_dir,
                "--no-save", "--no-audit", "--no-fund", "--prefer-offline", "--loglevel=error"
            ]
            result = subprocess.run(cmd, cwd=work_dir, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                # Clean up node_modules to save space
                shutil.rmtree(os.path.join(work_dir, "node_modules"), ignore_errors=True)
                return True
            else:
                # Rate limiting or other error, backoff
                time.sleep(1 * (attempt + 1))
        except Exception:
            time.sleep(1)
            
    return False

def main():
    parser = argparse.ArgumentParser(description="Fast NPM Downloader with PostgreSQL logging and Resume capability.")
    parser.add_argument("package", help="NPM package name to download")
    parser.add_argument("--fast", action="store_true", help="Enable fast mode (optimized settings)")
    parser.add_argument("--workers", type=int, help="Number of parallel workers")
    parser.add_argument("--parallel", type=int, help="Alias for --workers")
    parser.add_argument("--total", type=int, default=1000000, help="Total downloads to achieve")
    
    args = parser.parse_args()
    
    package_name = args.package.rstrip('/')
    
    # Determine workers
    max_cpu = multiprocessing.cpu_count()
    workers = args.workers or args.parallel or (max_cpu * 10 if args.fast else max_cpu * 2)
    
    print(f"🚀 Starting NPM downloads for: {package_name}")
    print(f"⚡ Optimized for Apple Silicon / MacPorts")
    print(f"💻 Max CPU Cores: {max_cpu} | Using Workers: {workers}")
    
    init_db()
    completed = get_completed_downloads(package_name)
    remaining = args.total - completed
    
    if remaining <= 0:
        print(f"✅ Package {package_name} already has {completed} downloads. Goal reached!")
        return
        
    print(f"🔄 Resuming from {completed} downloads. {remaining} remaining.")
    
    pkg_hash = hashlib.md5(package_name.encode()).hexdigest()[:8]
    
    start_time = time.time()
    batch_size = 10
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = set()
        
        # Submit initial batch
        for i in range(min(workers * 2, remaining)):
            futures.add(executor.submit(worker_task, package_name, i % workers))
            
        successful_in_batch = 0
        
        while futures and completed < args.total:
            done, futures = concurrent.futures.wait(futures, return_when=concurrent.futures.FIRST_COMPLETED)
            
            for future in done:
                if future.result():
                    completed += 1
                    successful_in_batch += 1
                    
                    # Submit a new task if we still need more
                    if completed + len(futures) < args.total:
                        futures.add(executor.submit(worker_task, package_name, completed % workers))
                else:
                    # Failed task, retry
                    if completed + len(futures) < args.total:
                        futures.add(executor.submit(worker_task, package_name, completed % workers))
                        
                # Update DB and print status periodically
                if successful_in_batch >= batch_size:
                    update_completed_downloads(package_name, successful_in_batch)
                    successful_in_batch = 0
                    
                    elapsed = time.time() - start_time
                    rate = int((completed - (args.total - remaining)) / elapsed) if elapsed > 0 else 0
                    sys.stdout.write(f"\r⏳ Progress: {completed} / {args.total} | ⚡ Rate: {rate} npms/sec | 📦 Pkg: {package_name} | 🔐 Hash: {pkg_hash} | 🔄 Instances: {workers}")
                    sys.stdout.flush()
                    
        # Final update
        if successful_in_batch > 0:
            update_completed_downloads(package_name, successful_in_batch)
            
    elapsed = time.time() - start_time
    rate = int((completed - (args.total - remaining)) / elapsed) if elapsed > 0 else 0
    print(f"\n✅ Completed {completed} downloads for {package_name} at {rate} npms/sec.")

if __name__ == "__main__":
    main()
