import os
import sys
import subprocess

# Auto-switch to virtual environment if running under global python
base_dir = os.path.abspath(os.path.dirname(__file__))
venv_python = os.path.join(base_dir, ".venv", "Scripts", "python.exe")
if os.path.exists(venv_python) and sys.executable.lower() != os.path.abspath(venv_python).lower():
    try:
        proc = subprocess.run([venv_python] + sys.argv)
        sys.exit(proc.returncode)
    except KeyboardInterrupt:
        sys.exit(0)

import uvicorn

if __name__ == "__main__":
    # Ensure app directory is importable
    sys.path.insert(0, base_dir)
    
    # Initialize DB if not present
    from app.database import DB_PATH, init_db
    if not DB_PATH.exists():
        print("Database not found. Initializing and seeding...")
        from app.seed_data import seed
        seed()
    
    print("Starting ScoutMyVehicle server on http://127.0.0.1:8000 ...")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
