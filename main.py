from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

PATCHES = {
    "PATCH-001": {
        "status": "ok",
        "patch_id": "PATCH-001",
        "patch_version": "v1",
        "message": "Patch scanned successfully",
        "label": "Normal status"
    },
    "PATCH-002": {
        "status": "attention",
        "patch_id": "PATCH-002",
        "patch_version": "v1",
        "message": "Attention needed",
        "label": "Please review"
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
        "message": "Patch not recognized",
        "label": "Unknown patch"
    }

@app.get("/simulate")
def simulate():
    return {
        "info": "Use /scan/PATCH-001 or /scan/PATCH-002 to simulate NFC scans"
    }

@app.get("/demo", response_class=HTMLResponse)
def demo():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Patch-Auri Demo</title>
    </head>
    <body style="font-family: Arial, sans-serif; padding: 24px;">
        <h1>Patch-Auri Demo</h1>
        <p>Manual patch scan simulation</p>
        <ul>
            <li><a href="/scan/PATCH-001">Scan PATCH-001</a></li>
            <li><a href="/scan/PATCH-002">Scan PATCH-002</a></li>
            <li><a href="/scan/PATCH-999">Scan PATCH-999</a></li>
        </ul>
    </body>
    </html>
    """