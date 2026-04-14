from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base

from database import SessionLocal, engine

app = FastAPI()
Base = declarative_base()


class Patch(Base):
    __tablename__ = "patches"

    id = Column(Integer, primary_key=True, index=True)
    patch_id = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, nullable=False)
    patch_version = Column(String, nullable=False)
    message = Column(String, nullable=False)
    label = Column(String, nullable=False)


class ScanResultRecord(Base):
    __tablename__ = "scan_results"

    id = Column(Integer, primary_key=True, index=True)
    patch_id = Column(String, index=True, nullable=True)
    status = Column(String, nullable=False)
    label = Column(String, nullable=False)
    message = Column(String, nullable=False)
    red = Column(Integer, nullable=False)
    green = Column(Integer, nullable=False)
    blue = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class PatchCreate(BaseModel):
    patch_id: str
    status: str
    patch_version: str
    message: str
    label: str


class ScanResultCreate(BaseModel):
    patch_id: Optional[str] = None
    status: str
    label: str
    message: str
    red: int
    green: int
    blue: int


Base.metadata.create_all(bind=engine)


def seed_default_patches():
    db = SessionLocal()

    if not db.query(Patch).filter(Patch.patch_id == "PATCH-001").first():
        db.add(
            Patch(
                patch_id="PATCH-001",
                status="ok",
                patch_version="v1",
                message="Patch scanned successfully",
                label="Normal status"
            )
        )

    if not db.query(Patch).filter(Patch.patch_id == "PATCH-002").first():
        db.add(
            Patch(
                patch_id="PATCH-002",
                status="attention",
                patch_version="v1",
                message="Attention needed",
                label="Please review"
            )
        )

    db.commit()
    db.close()


seed_default_patches()


def get_patch_from_db(patch_id: str):
    db = SessionLocal()
    patch = db.query(Patch).filter(Patch.patch_id == patch_id).first()

    if patch:
        result = {
            "status": patch.status,
            "patch_id": patch.patch_id,
            "patch_version": patch.patch_version,
            "message": patch.message,
            "label": patch.label
        }
        db.close()
        return result

    db.close()
    return None


@app.get("/")
def home():
    return {
        "message": "Patch-Auri backend is running",
        "usage": "/scan/PATCH-001",
        "camera": "/camera"
    }


@app.get("/patches")
def list_patches():
    db = SessionLocal()
    patches = db.query(Patch).all()

    result = []
    for patch in patches:
        result.append(
            {
                "patch_id": patch.patch_id,
                "status": patch.status,
                "patch_version": patch.patch_version,
                "message": patch.message,
                "label": patch.label
            }
        )

    db.close()
    return result


@app.post("/patches")
def create_patch(patch_data: PatchCreate):
    db = SessionLocal()

    if db.query(Patch).filter(Patch.patch_id == patch_data.patch_id).first():
        db.close()
        raise HTTPException(status_code=400, detail="Patch ID already exists")

    new_patch = Patch(**patch_data.dict())

    db.add(new_patch)
    db.commit()
    db.refresh(new_patch)
    db.close()

    return {
        "message": "Patch created successfully",
        "patch_id": new_patch.patch_id
    }


@app.delete("/patches/{patch_id}")
def delete_patch(patch_id: str):
    db = SessionLocal()
    patch = db.query(Patch).filter(Patch.patch_id == patch_id).first()

    if not patch:
        db.close()
        raise HTTPException(status_code=404, detail="Patch not found")

    db.delete(patch)
    db.commit()
    db.close()

    return {
        "message": "Patch deleted successfully",
        "patch_id": patch_id
    }


@app.post("/scan-result")
def save_scan_result(scan_result: ScanResultCreate):
    db = SessionLocal()

    new_result = ScanResultRecord(
        patch_id=scan_result.patch_id,
        status=scan_result.status,
        label=scan_result.label,
        message=scan_result.message,
        red=scan_result.red,
        green=scan_result.green,
        blue=scan_result.blue
    )

    db.add(new_result)
    db.commit()
    db.refresh(new_result)
    db.close()

    return {
        "message": "Scan result saved successfully",
        "result_id": new_result.id
    }


@app.get("/camera", response_class=HTMLResponse)
def camera_page():
    return FileResponse("camera.html")


@app.get("/scan/{patch_id}")
def scan_patch(patch_id: str):
    patch = get_patch_from_db(patch_id)

    if not patch:
        return RedirectResponse(url=f"/result/{patch_id}", status_code=302)

    return RedirectResponse(url=f"/camera?patch_id={patch_id}", status_code=302)


@app.get("/result/{patch_id}", response_class=HTMLResponse)
def result_page(patch_id: str):
    patch = get_patch_from_db(patch_id)

    if patch:
        if patch["status"] == "ok":
            color = "#4CAF50"
            icon = "✔"
        else:
            color = "#FF9800"
            icon = "⚠"

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
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #1e1e2f, #3a3a5f);
            display:flex;
            align-items:center;
            justify-content:center;
            height:100vh;
        ">
            <div style="
                background:white;
                padding:30px;
                border-radius:24px;
                width:90%;
                max-width:400px;
                text-align:center;
                box-shadow:0 15px 40px rgba(0,0,0,0.4);
            ">
                <div style="font-size:50px; color:{color};">{icon}</div>

                <h1 style="color:{color};">{patch["label"]}</h1>

                <p style="color:#333;">{patch["message"]}</p>

                <div style="background:#f5f5f5; padding:15px; border-radius:12px;">
                    <strong>Patch ID</strong><br>{patch["patch_id"]}
                </div>

                <div style="background:#f5f5f5; padding:15px; border-radius:12px; margin-top:10px;">
                    <strong>Version</strong><br>{patch["patch_version"]}
                </div>
            </div>
        </body>
        </html>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <body style="background:#111; color:white; text-align:center; padding:50px;">
        <h1>Unknown Patch</h1>
        <p>{patch_id}</p>
    </body>
    </html>
    """


@app.get("/simulate")
def simulate():
    return {"info": "Use /scan/PATCH-001"}


@app.get("/demo", response_class=HTMLResponse)
def demo():
    return """
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial; padding:20px;">
        <h1>Patch-Auri Demo</h1>
        <ul>
            <li><a href="/scan/PATCH-001">Scan PATCH-001</a></li>
            <li><a href="/scan/PATCH-002">Scan PATCH-002</a></li>
            <li><a href="/scan/PATCH-999">Scan PATCH-999</a></li>
        </ul>
    </body>
    </html>
    """