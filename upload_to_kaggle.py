"""
Upload dataset to Kaggle using the REST API directly with username/key auth.
"""
import json
import os
import requests
import hashlib
import time
import zipfile
import tempfile

# Load credentials
with open(os.path.expanduser("~/.kaggle/kaggle.json")) as f:
    creds = json.load(f)

USERNAME = creds["username"]
API_KEY = creds["key"]
AUTH = (USERNAME, API_KEY)
BASE = "https://www.kaggle.com/api/v1"

DATASET_DIR = os.path.dirname(os.path.abspath(__file__))
SLUG = "sleep-debt-and-screen-time-late-night-phone-habits"

# Files to include in the dataset
FILES_TO_UPLOAD = [
    "sleep_debt_screen_time.csv",
]

def get_file_hash(filepath):
    """Get MD5 hash of file content."""
    h = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def upload_file(filepath):
    """Upload a single file to Kaggle and return the upload token."""
    filename = os.path.basename(filepath)
    file_size = os.path.getsize(filepath)
    content_length = file_size
    last_modified = int(os.path.getmtime(filepath))

    print(f"  Requesting upload URL for {filename} ({file_size} bytes)...")

    # Step 1: Get upload URL
    resp = requests.post(
        f"{BASE}/datasets/upload/file/{file_size}",
        json={"fileName": filename, "contentLength": content_length, "lastModifiedDateUtc": last_modified},
        auth=AUTH,
    )

    if resp.status_code != 200:
        print(f"  ERROR getting upload URL: {resp.status_code} - {resp.text}")
        return None

    upload_info = resp.json()
    upload_url = upload_info.get("createUrl")
    token = upload_info.get("token")

    if not upload_url:
        print(f"  ERROR: No upload URL in response: {upload_info}")
        return None

    print(f"  Uploading {filename}...")

    # Step 2: Upload the file
    with open(filepath, "rb") as f:
        put_resp = requests.put(
            upload_url,
            data=f,
            headers={"Content-Type": "application/octet-stream"},
        )

    if put_resp.status_code not in (200, 201):
        print(f"  ERROR uploading: {put_resp.status_code} - {put_resp.text[:500]}")
        return None

    print(f"  Upload complete. Token: {token}")
    return token

print(f"=== Kaggle Dataset Upload ===")
print(f"User: {USERNAME}")
print(f"Dataset: {SLUG}")
print()

# Upload all files
file_tokens = []
for fname in FILES_TO_UPLOAD:
    fpath = os.path.join(DATASET_DIR, fname)
    if not os.path.exists(fpath):
        print(f"WARNING: {fname} not found, skipping")
        continue
    token = upload_file(fpath)
    if token:
        file_tokens.append({
            "token": token,
            "description": f"{fname}",
        })

if not file_tokens:
    print("ERROR: No files uploaded successfully")
    exit(1)

# Create the dataset
print(f"\nCreating dataset on Kaggle...")

with open(os.path.join(DATASET_DIR, "dataset-metadata.json")) as f:
    meta = json.load(f)

create_payload = {
    "title": meta["title"],
    "slug": SLUG,
    "ownerSlug": USERNAME,
    "licenseName": "CC BY-SA 4.0",
    "subtitle": meta["subtitle"],
    "description": meta["description"],
    "files": file_tokens,
    "isPrivate": False,
    "convertToCsv": True,
    "categoryIds": ["health", "biology", "public health"],
}

resp = requests.post(
    f"{BASE}/datasets/create/new",
    json=create_payload,
    auth=AUTH,
)

print(f"Response: {resp.status_code}")
if resp.status_code == 200:
    result = resp.json()
    print(f"Dataset created successfully!")
    print(f"URL: https://www.kaggle.com/datasets/{USERNAME}/{SLUG}")
    print(f"Response: {json.dumps(result, indent=2)}")
else:
    print(f"Error: {resp.text}")
    # If dataset already exists, try to create a new version
    if "already exists" in resp.text.lower() or resp.status_code == 403:
        print("\nDataset may already exist. Trying to create a new version...")
        version_payload = {
            "versionNotes": "Fresh dataset generation with biophysical simulation",
            "subtitle": meta["subtitle"],
            "description": meta["description"],
            "files": file_tokens,
            "convertToCsv": True,
            "deleteOldVersions": False,
        }
        resp2 = requests.post(
            f"{BASE}/datasets/create/version/{USERNAME}/{SLUG}",
            json=version_payload,
            auth=AUTH,
        )
        print(f"Version Response: {resp2.status_code}")
        print(f"Response: {resp2.text}")
