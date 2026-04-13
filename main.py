from fastapi import FastAPI

app = FastAPI()

PATCHES = {
    "PATCH-001": {
        "status": "ok",
        "patch_id": "PATCH-001",
        "patch_version": "v1",
        "message": "Patch scanned successfully"
    },
    "PATCH-002": {
        "status": "attention",
        "patch_id": "PATCH-002",
        "patch_version": "v1",
        "message": "Attention needed"
    }
}

@app.get("/")
def home():
    return {
        "message": "Patch-Auri backend is running",
        "usage": "/scan/PATCH-001"
    }

@app.get("/scan/{patch_id}")
def scan_patch(patch_id: str):
    patch = PATCHES.get(patch_id)

    if patch:
        return patch

    return {
        "status": "unknown",
        "patch_id": patch_id,
        "message": "Patch not recognized"
    }

@app.get("/simulate")
def simulate():
    return {
        "info": "Use /scan/PATCH-001 or /scan/PATCH-002 to simulate NFC scans"
    }