import os
import subprocess
import shutil
from huggingface_hub import snapshot_download
from tenacity import retry, stop_after_attempt, wait_fixed

# Define the repository and the subdirectory path
repo_id = "ittia/wiki_dpr"
repo_type = "dataset"
dataset_folder = "/data/datasets/wiki"
dir_map = [
    {
        "repo_dir": "checkpoints/colbertv2.0",
        "local_dir": "/data/checkpoints/colbertv2.0",
    },
    {
        "repo_dir": "datasets",
        "local_dir": dataset_folder,
    },
    {
        "repo_dir": "indexes/wiki",
        "local_dir": "/data/indexes/wiki",
    },
]
revision = "main"

def check_exists(folder_path):
    # Check if the folder exists
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        # Check if the folder is not empty
        if [f for f in os.listdir(folder_path) if not f.startswith('.')]:  # Don't count items starts with `.`
            return True
    return False

def move_files_subfolders(source_folder, destination_folder):
    # Ensure the destination folder exists
    os.makedirs(destination_folder, exist_ok=True)

    # Iterate over all files and folders in the source folder
    for item in os.listdir(source_folder):
        source_path = os.path.join(source_folder, item)
        destination_path = os.path.join(destination_folder, item)

        # Move the item
        shutil.move(source_path, destination_path)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True) 
def download_hf_folder(repo_dir, local_dir):
    download_dir = os.path.join(local_dir, '.download')

    os.makedirs(download_dir, exist_ok=True)

    snapshot_download(
        repo_id=repo_id, 
        repo_type=repo_type, 
        revision=revision, 
        allow_patterns=f"{repo_dir}/*",
        local_dir=download_dir
    )

    return download_dir

for map in dir_map:
    repo_dir = map['repo_dir']
    local_dir = map['local_dir']

    if check_exists(local_dir):
        print(f"local dir '{local_dir}' exists and not empty, skip download")
        continue

    download_dir = download_hf_folder(repo_dir, local_dir)
    _source_dir = os.path.join(download_dir, repo_dir)
    move_files_subfolders(_source_dir, local_dir)

    print(f"Downloaded: {repo_dir} to {local_dir}")

# extract dataset
_file_path = os.path.join(dataset_folder, "psgs_w100.tsv.gz")
if os.path.isfile(_file_path):
    try:
        subprocess.run(['gunzip', _file_path], check=True)
        print(f"File {_file_path} extracted and replaced successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

print("All folders have been downloaded and processed.")
