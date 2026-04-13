from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Patch-Auri backend is running"}

@app.get("/scan")
def scan_patch():
    return {
        "status": "ok",
        "data": "NFC patch scanned successfully"
    }