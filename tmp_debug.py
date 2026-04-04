import sys, os
from pathlib import Path
print(f"EXE: {sys.executable}")
print(f"FILE: {os.path.abspath('app/cli.py')}")
print(f"JOIN: {' '.join(['evolve', 'status'])}")
full_cmd = f'"{sys.executable}" "{os.path.abspath("app/cli.py")}" {" ".join(["evolve", "status"])}'
print(f"CMD: {full_cmd}")
