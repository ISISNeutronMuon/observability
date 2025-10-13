import os
import time
import boto3
from prometheus_client import start_http_server, Gauge

# --- Configuration ---
BUCKETS = [b for b in os.getenv("S3_BUCKETS", "").split(",") if b]
S3_ENDPOINT = os.getenv("S3_ENDPOINT")  # e.g. https://s3.echo.stfc.ac.uk
INTERVAL = int(os.getenv("SCRAPE_INTERVAL", "180"))  # seconds

# --- Metrics ---
bucket_size_bytes = Gauge(
    "s3_bucket_size_bytes",
    "Total size of S3 bucket in bytes",
    ["bucket"],
)
bucket_object_count = Gauge(
    "s3_bucket_object_count",
    "Total object count in S3 bucket",
    ["bucket"],
)

# --- S3 Client ---
session = boto3.session.Session()
s3 = session.client("s3", endpoint_url=S3_ENDPOINT)


def get_bucket_usage(bucket: str):
    """Return (object_count, total_size_bytes) for a bucket."""
    total_size = 0
    total_count = 0
    paginator = s3.get_paginator("list_objects_v2")
    try:
        for page in paginator.paginate(Bucket=bucket):
            contents = page.get("Contents", [])
            total_count += len(contents)
            total_size += sum(obj["Size"] for obj in contents)
    except Exception as e:
        print(f"[ERROR] Failed to collect {bucket}: {e}")
        return None, None

    return total_count, total_size


def collect_metrics():
    for bucket in BUCKETS:
        count, size = get_bucket_usage(bucket)
        if count is None:
            continue
        bucket_object_count.labels(bucket=bucket).set(count)
        bucket_size_bytes.labels(bucket=bucket).set(size)
        print(f"[INFO] {bucket}: {count} objects, {size} bytes ({(size / 1000000000):.2f}GB)", flush=True)


if __name__ == "__main__":
    start_http_server(8000)
    print("[INFO] S3 metrics exporter started on port 8000")
    while True:
        collect_metrics()
        print(f"[INFO] Sleeping for {INTERVAL} seconds...", flush=True)
        time.sleep(INTERVAL)
