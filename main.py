from datetime import datetime
from typing import Optional

from fastapi import FastAPI
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
                status="level_1",
                patch_version="v1",
                message="Patch is ready for scan.",
                label="Level 1 - Normal"
            )
        )

    if not db.query(Patch).filter(Patch.patch_id == "PATCH-002").first():
        db.add(
            Patch(
                patch_id="PATCH-002",
                status="level_2",
                patch_version="v1",
                message="Patch is ready for monitoring flow.",
                label="Level 2 - Monitor"
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
        status_styles = {
            "level_1": {
                "color": "#2e7d32",
                "icon": "🟢"
            },
            "level_2": {
                "color": "#c49000",
                "icon": "🟡"
            },
            "level_3": {
                "color": "#d32f2f",
                "icon": "🔴"
            }
        }

        style = status_styles.get(
            patch["status"],
            {
                "color": "#666666",
                "icon": "ℹ️"
            }
        )

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
            font-family:-apple-system, BlinkMacSystemFont, sans-serif;
            background:linear-gradient(135deg, #1e1e2f, #3a3a5f);
            display:flex;
            align-items:center;
            justify-content:center;
            min-height:100vh;
            padding:20px;
            box-sizing:border-box;
        ">
            <div style="
                background:white;
                padding:30px;
                border-radius:24px;
                width:90%;
                max-width:420px;
                text-align:center;
                box-shadow:0 15px 40px rgba(0,0,0,0.4);
            ">
                <div style="font-size:48px; margin-bottom:10px;">{style["icon"]}</div>

                <h1 style="
                    color:{style["color"]};
                    margin:0 0 12px 0;
                    font-size:30px;
                    line-height:1.3;
                ">
                    {patch["label"]}
                </h1>

                <p style="
                    color:#333;
                    font-size:16px;
                    line-height:1.7;
                    margin:0 0 20px 0;
                ">
                    {patch["message"]}
                </p>

                <div style="
                    background:#f5f5f5;
                    padding:15px;
                    border-radius:12px;
                    margin-bottom:10px;
                ">
                    <strong>Patch ID</strong><br>{patch["patch_id"]}
                </div>

                <div style="
                    background:#f5f5f5;
                    padding:15px;
                    border-radius:12px;
                ">
                    <strong>Version</strong><br>{patch["patch_version"]}
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
        font-family:-apple-system, BlinkMacSystemFont, sans-serif;
        background:#111;
        display:flex;
        align-items:center;
        justify-content:center;
        min-height:100vh;
        padding:20px;
        box-sizing:border-box;
    ">
        <div style="
            background:white;
            padding:30px;
            border-radius:24px;
            width:90%;
            max-width:420px;
            text-align:center;
        ">
            <div style="font-size:48px; margin-bottom:10px;">❌</div>
            <h1 style="color:#d32f2f; margin:0 0 12px 0;">Unknown Patch</h1>
            <p style="color:#333; margin:0;">Patch ID: {patch_id}</p>
        </div>
    </body>
    </html>
    """