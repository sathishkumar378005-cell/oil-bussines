import os
import sys
import uvicorn
from dotenv import load_dotenv

# Ensure backend directory is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, "backend"))

load_dotenv()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    print("\n" + "="*60)
    print("🌿 Starting Latha Oils Backend API Server")
    print(f"📡 API URL:        http://localhost:{port}")
    print(f"📖 Swagger Docs:   http://localhost:{port}/docs")
    print(f"🐘 Database Host:  {os.getenv('DB_HOST', 'db.dttiqptqokirducezdyp.supabase.co')}")
    print("="*60 + "\n")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True, app_dir="backend")
