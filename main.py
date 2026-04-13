from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Patch-Auri backend is running"}

@app.get("/scan/{patch_id}")
def scan_patch(patch_id: str):
    return {
        "status": "ok",
        "patch_id": patch_id,
        "message": "Patch scanned successfully"
    }