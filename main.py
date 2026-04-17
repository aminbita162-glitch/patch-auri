from datetime import datetime
from hashlib import sha256
from typing import Optional

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base

from database import SessionLocal, engine

app = FastAPI()
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


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


def hash_password(password: str) -> str:
    return sha256(password.encode("utf-8")).hexdigest()


def get_current_user_email(request: Request) -> Optional[str]:
    return request.cookies.get("patch_auri_user")


def get_user_by_email(email: str) -> Optional[User]:
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    db.close()
    return user


def require_login(request: Request):
    user_email = get_current_user_email(request)
    if not user_email:
        return None
    return get_user_by_email(user_email)


def render_auth_page(title: str, subtitle: str, action: str, button_text: str, alt_text: str, alt_link: str, error: str = "") -> str:
    error_html = ""
    if error:
        error_html = f"""
        <div style="
            background:#fff5f5;
            color:#d32f2f;
            border-radius:14px;
            padding:12px;
            margin-bottom:16px;
            font-size:14px;
            line-height:1.6;
        ">
            {error}
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
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
            width:90%;
            max-width:420px;
            background:white;
            color:black;
            border-radius:24px;
            padding:28px;
            box-shadow:0 15px 40px rgba(0,0,0,0.35);
        ">
            <h1 style="
                margin:0 0 10px 0;
                font-size:34px;
                text-align:center;
            ">
                {title}
            </h1>

            <p style="
                margin:0 0 22px 0;
                color:#555;
                font-size:15px;
                line-height:1.6;
                text-align:center;
            ">
                {subtitle}
            </p>

            {error_html}

            <form method="post" action="{action}">
                <label style="display:block; font-size:14px; color:#444; margin-bottom:8px;">Email</label>
                <input
                    type="email"
                    name="email"
                    required
                    style="
                        width:100%;
                        box-sizing:border-box;
                        padding:14px 16px;
                        border:1px solid #ddd;
                        border-radius:12px;
                        font-size:16px;
                        margin-bottom:16px;
                    "
                >

                <label style="display:block; font-size:14px; color:#444; margin-bottom:8px;">Password</label>
                <input
                    type="password"
                    name="password"
                    required
                    minlength="6"
                    style="
                        width:100%;
                        box-sizing:border-box;
                        padding:14px 16px;
                        border:1px solid #ddd;
                        border-radius:12px;
                        font-size:16px;
                        margin-bottom:18px;
                    "
                >

                <button
                    type="submit"
                    style="
                        width:100%;
                        background:#1e1e2f;
                        color:white;
                        border:none;
                        padding:14px 18px;
                        border-radius:12px;
                        font-size:16px;
                        cursor:pointer;
                    "
                >
                    {button_text}
                </button>
            </form>

            <div style="
                margin-top:18px;
                text-align:center;
                font-size:14px;
                color:#555;
                line-height:1.6;
            ">
                {alt_text}
                <a href="{alt_link}" style="color:#1e1e2f; font-weight:600; text-decoration:none;">
                    Open
                </a>
            </div>
        </div>
    </body>
    </html>
    """


def render_dashboard(email: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Patch-Auri Dashboard</title>
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
            width:90%;
            max-width:420px;
            background:white;
            color:black;
            border-radius:24px;
            padding:28px;
            box-shadow:0 15px 40px rgba(0,0,0,0.35);
            text-align:center;
        ">
            <h1 style="
                margin:0 0 10px 0;
                font-size:34px;
            ">
                Patch-Auri
            </h1>

            <p style="
                margin:0 0 18px 0;
                color:#555;
                font-size:15px;
                line-height:1.6;
            ">
                Signed in as
            </p>

            <div style="
                background:#f5f5f5;
                border-radius:14px;
                padding:14px;
                font-size:15px;
                color:#333;
                margin-bottom:18px;
                word-break:break-word;
            ">
                {email}
            </div>

            <a
                href="/scan/PATCH-001"
                style="
                    display:block;
                    background:#1e1e2f;
                    color:white;
                    text-decoration:none;
                    padding:14px 18px;
                    border-radius:12px;
                    font-size:16px;
                    margin-bottom:12px;
                "
            >
                Start Scan
            </a>

            <a
                href="/camera?patch_id=PATCH-001"
                style="
                    display:block;
                    background:#f5f5f5;
                    color:#1e1e2f;
                    text-decoration:none;
                    padding:14px 18px;
                    border-radius:12px;
                    font-size:16px;
                    margin-bottom:12px;
                "
            >
                Open Camera
            </a>

            <a
                href="/logout"
                style="
                    display:block;
                    color:#d32f2f;
                    text-decoration:none;
                    font-size:15px;
                    margin-top:8px;
                "
            >
                Log out
            </a>
        </div>
    </body>
    </html>
    """


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
def home(request: Request):
    user = require_login(request)
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return RedirectResponse(url="/login", status_code=302)


@app.get("/register", response_class=HTMLResponse)
def register_page():
    return render_auth_page(
        title="Create account",
        subtitle="Register with your email and password to use Patch-Auri.",
        action="/register",
        button_text="Register",
        alt_text="Already have an account?",
        alt_link="/login"
    )


@app.post("/register")
def register_user(
    email: str = Form(...),
    password: str = Form(...)
):
    clean_email = email.strip().lower()
    clean_password = password.strip()

    if not clean_email or not clean_password:
        return HTMLResponse(
            render_auth_page(
                title="Create account",
                subtitle="Register with your email and password to use Patch-Auri.",
                action="/register",
                button_text="Register",
                alt_text="Already have an account?",
                alt_link="/login",
                error="Email and password are required."
            ),
            status_code=400
        )

    if len(clean_password) < 6:
        return HTMLResponse(
            render_auth_page(
                title="Create account",
                subtitle="Register with your email and password to use Patch-Auri.",
                action="/register",
                button_text="Register",
                alt_text="Already have an account?",
                alt_link="/login",
                error="Password must be at least 6 characters long."
            ),
            status_code=400
        )

    db = SessionLocal()
    existing_user = db.query(User).filter(User.email == clean_email).first()

    if existing_user:
        db.close()
        return HTMLResponse(
            render_auth_page(
                title="Create account",
                subtitle="Register with your email and password to use Patch-Auri.",
                action="/register",
                button_text="Register",
                alt_text="Already have an account?",
                alt_link="/login",
                error="An account with this email already exists."
            ),
            status_code=400
        )

    new_user = User(
        email=clean_email,
        password_hash=hash_password(clean_password)
    )
    db.add(new_user)
    db.commit()
    db.close()

    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(
        key="patch_auri_user",
        value=clean_email,
        httponly=True,
        samesite="lax"
    )
    return response


@app.get("/login", response_class=HTMLResponse)
def login_page():
    return render_auth_page(
        title="Sign in",
        subtitle="Enter your email and password to continue.",
        action="/login",
        button_text="Log in",
        alt_text="Need a new account?",
        alt_link="/register"
    )


@app.post("/login")
def login_user(
    email: str = Form(...),
    password: str = Form(...)
):
    clean_email = email.strip().lower()
    clean_password = password.strip()

    db = SessionLocal()
    user = db.query(User).filter(User.email == clean_email).first()
    db.close()

    if not user or user.password_hash != hash_password(clean_password):
        return HTMLResponse(
            render_auth_page(
                title="Sign in",
                subtitle="Enter your email and password to continue.",
                action="/login",
                button_text="Log in",
                alt_text="Need a new account?",
                alt_link="/register",
                error="Invalid email or password."
            ),
            status_code=400
        )

    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(
        key="patch_auri_user",
        value=clean_email,
        httponly=True,
        samesite="lax"
    )
    return response


@app.get("/logout")
def logout_user():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("patch_auri_user")
    return response


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request):
    user = require_login(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return render_dashboard(user.email)


@app.post("/scan-result")
def save_scan_result(request: Request, scan_result: ScanResultCreate):
    user = require_login(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

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
def camera_page(request: Request):
    user = require_login(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return FileResponse("camera.html")


@app.get("/scan/{patch_id}")
def scan_patch(request: Request, patch_id: str):
    user = require_login(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    patch = get_patch_from_db(patch_id)

    if not patch:
        return RedirectResponse(url=f"/result/{patch_id}", status_code=302)

    return RedirectResponse(url=f"/camera?patch_id={patch_id}", status_code=302)


@app.get("/result/{patch_id}", response_class=HTMLResponse)
def result_page(request: Request, patch_id: str):
    user = require_login(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

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