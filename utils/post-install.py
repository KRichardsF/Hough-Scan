from pathlib import Path
import shutil

# Paths
ROOT_DIR = Path(__file__).resolve().parent.parent  # Go up to project root
DIST_DIR = ROOT_DIR / "dist"  # Path to dist directory
CONFIG_FILE = ROOT_DIR / "utils" / "move_config.txt"  # Path to config file

def copy_files():
    if not CONFIG_FILE.exists():
        print(f"Config file '{CONFIG_FILE}' not found. Skipping file copy.")
        return

    with CONFIG_FILE.open("r", encoding="utf-8") as f:
        paths = [line.strip() for line in f.readlines() if line.strip()]

    for path in paths:
        src_path = ROOT_DIR / path  # Full source path
        dest_path = DIST_DIR / path  # Destination inside dist

        if src_path.exists():
            try:
                # Ensure the destination directory exists
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                # Copy file or folder
                if src_path.is_dir():
                    shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
                    print(f"Copied folder: {src_path} → {dest_path}")
                else:
                    shutil.copy2(src_path, dest_path)
                    print(f"Copied file: {src_path} → {dest_path}")

            except Exception as e:
                print(f"Error copying {src_path}: {e}")
        else:
            print(f"Warning: {src_path} does not exist. Skipping.")

if __name__ == "__main__":
    copy_files()
