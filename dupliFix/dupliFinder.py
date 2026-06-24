import os
import hashlib
import shutil
from pathlib import Path

SOURCE_FOLDER = r"[YOUR_SOURCE_FOLDEDR]"
OUTPUT_FOLDER = "sorted_files"

ORIGINALS_FOLDER = Path(OUTPUT_FOLDER) / "originals"
DUPLICATES_FOLDER = Path(OUTPUT_FOLDER) / "duplicates"

ORIGINALS_FOLDER.mkdir(parents=True, exist_ok=True)
DUPLICATES_FOLDER.mkdir(parents=True, exist_ok=True)


def file_hash(file_path):
    hasher = hashlib.sha256()

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)

    return hasher.hexdigest()


def safe_move(src, dest_folder):
    dest = dest_folder / src.name

    counter = 1
    while dest.exists():
        dest = dest_folder / f"{src.stem}_{counter}{src.suffix}"
        counter += 1

    shutil.move(str(src), str(dest))


def sort_duplicates(source_folder):
    seen_hashes = {}

    for root, _, files in os.walk(source_folder):
        for filename in files:
            file_path = Path(root) / filename
            hash_value = file_hash(file_path)

            if hash_value in seen_hashes:
                safe_move(file_path, DUPLICATES_FOLDER)
            else:
                seen_hashes[hash_value] = file_path
                safe_move(file_path, ORIGINALS_FOLDER)

    print("Done.")
    print(f"Originals saved to: {ORIGINALS_FOLDER}")
    print(f"Duplicates saved to: {DUPLICATES_FOLDER}")


sort_duplicates(SOURCE_FOLDER)
