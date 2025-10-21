import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.crdt_types.two_phase_set import TwoPhaseSet

# Initialize
crdt = TwoPhaseSet("node_b", "../sync_folder/two_phase_set")

# Check files in the sync folder
sync_folder_path = Path("../sync_folder/two_phase_set")
if sync_folder_path.exists() and sync_folder_path.is_dir():
    files_in_sync_folder = {file.name for file in sync_folder_path.iterdir() if file.is_file()}
    print("Files in sync folder:", files_in_sync_folder)
    # Add each file in the sync folder to the CRDT
    for file_name in files_in_sync_folder:
        crdt.remove(file_name)

    # Check if a specific file is in the set (e.g., "document.txt")
    print(crdt.lookup(files_in_sync_folder))

    # Get all active elements
    active_elements = crdt.get_active_elements()
    print(active_elements)
else:
    print("Sync folder does not exist or is not a directory.")

if files_in_sync_folder:
    for file_name in files_in_sync_folder:
        crdt.remove(file_name)

    # Check if a specific file is in the set (e.g., "document.txt")
    print(crdt.lookup(files_in_sync_folder))

    # Get all active elements
    active_elements = crdt.get_active_elements()
    print(active_elements)

if files_in_sync_folder:
    for file_name in files_in_sync_folder:
        crdt.add(file_name)
    # Check if a specific file is in the set (e.g., "document.txt")
    print(crdt.lookup(files_in_sync_folder))
    # Get all active elements
    active_elements = crdt.get_active_elements()
    print(active_elements)