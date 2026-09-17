import os
import sys
import subprocess

# Auto-switch to virtual environment if running under global python on Windows
base_dir = os.path.abspath(os.path.dirname(__file__))
venv_python = os.path.join(base_dir, ".venv", "Scripts", "python.exe")
if sys.platform == "win32" and os.path.exists(venv_python) and sys.executable.lower() != os.path.abspath(venv_python).lower():
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
    
    # Cloud environments (Railway, Render, etc.) provide PORT and require binding to 0.0.0.0
    host = os.environ.get("HOST", "0.0.0.0" if (os.environ.get("PORT") or os.environ.get("RAILWAY_ENVIRONMENT")) else "127.0.0.1")
    port = int(os.environ.get("PORT", 8000))
    reload = os.environ.get("RELOAD", "false").lower() in ("true", "1", "yes") if os.environ.get("PORT") else True
    
    print(f"Starting ScoutMyVehicle server on http://{host}:{port} ...")
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)
