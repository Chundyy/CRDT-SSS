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

