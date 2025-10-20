import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.crdt_types.two_phase_set import TwoPhaseSet

# Initialize
crdt = TwoPhaseSet("node_b", "sync_folder/two_phase_set")

# ADD elements explicitly
crdt.add("document.txt")
crdt.add("image.png")
crdt.add("data.json")

# REMOVE elements explicitly
crdt.remove("image.png")

# CHECK what's in the set
print(crdt.lookup("document.txt"))  # True - still in set
print(crdt.lookup("image.png"))     # False - was removed
print(crdt.lookup("data.json"))     # True - still in set

# GET all active elements
active_elements = crdt.get_active_elements()
print(active_elements)  # {"document.txt", "data.json"}

# Check files in the sync folder
sync_folder_path = Path("sync_folder/two_phase_set")
if sync_folder_path.exists() and sync_folder_path.is_dir():
    files_in_sync_folder = {file.name for file in sync_folder_path.iterdir() if file.is_file()}
    print("Files in sync folder:", files_in_sync_folder)
    crdt.add(files_in_sync_folder)
    print(active_elements)
else:
    print("Sync folder does not exist or is not a directory.")
