from fastapi import FastAPI
from scanner import scan_directory_fast
from database import init_db, save_abilities, get_all_abilities
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Run this once when server starts
@app.on_event("startup")
def startup_event():
    init_db()
    
# Allow React to talk to Python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/scan")
def scan_mods(path: str):
    # This runs the heavy scanner
    abilities = scan_directory_fast(path)
    
    # Save to SQLite
    save_abilities(abilities)
    
    return {"status": "success", "count": len(abilities)}

@app.get("/abilities")
def get_abilities():
    return get_all_abilities()