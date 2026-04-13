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

@app.get("/scan/{patch_id}", response_class=HTMLResponse)
def scan_patch(patch_id: str):
    patch = PATCHES.get(patch_id)

    if patch:
        color = "#4CAF50" if patch["status"] == "ok" else "#FF9800"

        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Patch Result</title>
        </head>
        <body style="
            margin:0;
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #1e1e2f, #3a3a5f);
            color: white;
            display:flex;
            align-items:center;
            justify-content:center;
            height:100vh;
        ">
            <div style="
                background:white;
                color:black;
                padding:30px;
                border-radius:20px;
                width:90%;
                max-width:400px;
                text-align:center;
                box-shadow:0 10px 30px rgba(0,0,0,0.3);
            ">
                <h1 style="color:{color}; margin-bottom:10px;">
                    {patch["label"]}
                </h1>

                <p style="font-size:16px; margin-bottom:20px;">
                    {patch["message"]}
                </p>

                <div style="
                    background:#f5f5f5;
                    padding:15px;
                    border-radius:10px;
                    margin-bottom:10px;
                ">
                    <strong>Patch ID:</strong><br>
                    {patch["patch_id"]}
                </div>

                <div style="
                    background:#f5f5f5;
                    padding:15px;
                    border-radius:10px;
                ">
                    <strong>Version:</strong><br>
                    {patch["patch_version"]}
                </div>
            </div>
        </body>
        </html>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Unknown Patch</title>
    </head>
    <body style="
        margin:0;
        font-family: Arial, sans-serif;
        background:#111;
        color:white;
        display:flex;
        align-items:center;
        justify-content:center;
        height:100vh;
    ">
        <div style="
            background:white;
            color:black;
            padding:30px;
            border-radius:20px;
            width:90%;
            max-width:400px;
            text-align:center;
        ">
            <h1 style="color:red;">Unknown Patch</h1>
            <p><strong>Patch ID:</strong></p>
            <p>{patch_id}</p>
        </div>
    </body>
    </html>
    """

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