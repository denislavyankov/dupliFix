import os
import hashlib
import shutil
from pathlib import Path


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


def sort_duplicates(source_folder, output_folder):
    source_folder = Path(source_folder).resolve()
    output_folder = Path(output_folder).resolve()

    originals_folder = output_folder / "originals"
    duplicates_folder = output_folder / "duplicates"

    originals_folder.mkdir(parents=True, exist_ok=True)
    duplicates_folder.mkdir(parents=True, exist_ok=True)

    seen_hashes = {}
    originals = []
    duplicates = []

    # PHASE 1: Scan only
    for root, dirs, files in os.walk(source_folder):
        root_path = Path(root).resolve()

        # Prevent scanning the output folder if it's inside the source folder
        dirs[:] = [
            d for d in dirs
            if (root_path / d).resolve() != output_folder
        ]

        for filename in files:
            file_path = root_path / filename

            # Extra safety: skip anything already inside the output folder
            if output_folder in file_path.parents:
                continue

            try:
                hash_value = file_hash(file_path)
            except (PermissionError, OSError) as e:
                print(f"Skipping {file_path}: {e}")
                continue

            if hash_value in seen_hashes:
                duplicates.append(file_path)
            else:
                seen_hashes[hash_value] = file_path
                originals.append(file_path)

    print(f"\nFound {len(originals)} originals")
    print(f"Found {len(duplicates)} duplicates")

    # PHASE 2: Move only after scanning is finished
    for file_path in originals:
        safe_move(file_path, originals_folder)

    for file_path in duplicates:
        safe_move(file_path, duplicates_folder)

    print("\nDone.")
    print(f"Originals saved to: {originals_folder}")
    print(f"Duplicates saved to: {duplicates_folder}")


source_folder = input("Enter the folder you want to scan: ").strip().strip('"')
output_folder = input("Enter the folder where you want the results saved: ").strip().strip('"')

if not Path(source_folder).is_dir():
    print("\nError: The source folder does not exist.")
else:
    sort_duplicates(source_folder, output_folder)