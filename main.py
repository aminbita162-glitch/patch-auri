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


LEVEL_CONFIG = {
    "level_1": {
        "label": "Level 1 - Normal",
        "message": "The observed change is within the normal range.",
        "guidance": "No action is required at this time.",
        "color": "#2e7d32",
        "icon": "🟢",
        "card_color": "#f3fbf4",
        "disclaimer": "This result is for awareness only and is not a medical diagnosis."
    },
    "level_2": {
        "label": "Level 2 - Monitor",
        "message": "A change was observed above the baseline.",
        "guidance": "Repeat the scan and continue monitoring.",
        "color": "#c49000",
        "icon": "🟡",
        "card_color": "#fffbe6",
        "disclaimer": "This result is for awareness and follow-up only and is not a medical diagnosis."
    },
    "level_3": {
        "label": "Level 3 - Consult Doctor",
        "message": "The observed change is above the defined threshold.",
        "guidance": "Please seek further medical review.",
        "color": "#d32f2f",
        "icon": "🔴",
        "card_color": "#fff3f3",
        "disclaimer": "This result is an early warning indication only and is not a medical diagnosis."
    }
}


def seed_default_patches():
    db = SessionLocal()

    if not db.query(Patch).filter(Patch.patch_id == "PATCH-001").first():
        db.add(
            Patch(
                patch_id="PATCH-001",
                status="level_1",
                patch_version="v1",
                message=LEVEL_CONFIG["level_1"]["message"],
                label=LEVEL_CONFIG["level_1"]["label"]
            )
        )

    if not db.query(Patch).filter(Patch.patch_id == "PATCH-002").first():
        db.add(
            Patch(
                patch_id="PATCH-002",
                status="level_2",
                patch_version="v1",
                message=LEVEL_CONFIG["level_2"]["message"],
                label=LEVEL_CONFIG["level_2"]["label"]
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
        style = LEVEL_CONFIG.get(
            patch["status"],
            {
                "label": patch["label"],
                "message": patch["message"],
                "guidance": "",
                "color": "#666666",
                "icon": "ℹ️",
                "card_color": "#f7f7f7",
                "disclaimer": "This result is for awareness only."
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
            background:linear-gradient(135deg, #0f1020, #1e1e2f);
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
                box-shadow:0 15px 40px rgba(0,0,0,0.35);
            ">
                <div style="
                    background:{style["card_color"]};
                    border-radius:18px;
                    padding:22px;
                ">
                    <div style="
                        font-size:44px;
                        margin-bottom:10px;
                    ">
                        {style["icon"]}
                    </div>

                    <h1 style="
                        color:{style["color"]};
                        margin:0 0 12px 0;
                        font-size:30px;
                        line-height:1.3;
                    ">
                        {style["label"]}
                    </h1>

                    <p style="
                        color:#333;
                        font-size:16px;
                        line-height:1.7;
                        margin:0 0 10px 0;
                    ">
                        {style["message"]}
                    </p>

                    <p style="
                        color:#333;
                        font-size:16px;
                        line-height:1.7;
                        margin:0 0 18px 0;
                    ">
                        {style["guidance"]}
                    </p>

                    <div style="
                        color:#666;
                        font-size:14px;
                        line-height:1.6;
                        margin:0 0 18px 0;
                    ">
                        Patch ID: {patch["patch_id"]}
                    </div>

                    <div style="
                        color:#777;
                        font-size:13px;
                        line-height:1.6;
                        margin:0 0 18px 0;
                    ">
                        {style["disclaimer"]}
                    </div>

                    <div style="
                        background:white;
                        padding:14px;
                        border-radius:12px;
                        color:#444;
                        font-size:14px;
                    ">
                        <strong>Version</strong><br>{patch["patch_version"]}
                    </div>
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
            box-shadow:0 15px 40px rgba(0,0,0,0.35);
        ">
            <div style="
                background:#fff5f5;
                border-radius:18px;
                padding:22px;
            ">
                <div style="font-size:44px; margin-bottom:10px;">❌</div>
                <h1 style="color:#d32f2f; margin:0 0 12px 0;">Unknown Patch</h1>
                <p style="color:#333; line-height:1.7; margin:0 0 12px 0;">
                    The requested patch could not be identified.
                </p>
                <div style="color:#666; font-size:14px; line-height:1.6;">
                    Patch ID: {patch_id}
                </div>
            </div>
        </div>
    </body>
    </html>
    """