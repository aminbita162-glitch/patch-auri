# Patch-Auri

Non-medical informational system for awareness and user guidance based on the interaction between a skin patch and a smartphone through NFC scanning.

---

## Overview

Patch-Auri is a functional prototype that demonstrates how a physical skin patch can interact with a smartphone interface to provide real-time user guidance based on visual color changes.

This system is designed strictly for **awareness and informational purposes only** and does not perform any medical diagnosis.

---

## How It Works

The system simulates the interaction between a smart skin patch and a mobile interface:

1. The user scans the patch through NFC interaction with a smartphone
2. The system opens a camera interface
3. The camera captures and analyzes the patch color
4. The system detects whether a significant color change has occurred
5. A clear and user-friendly message is displayed
6. The result is optionally stored in the backend

---

## System Flow

Skin Patch → NFC Scan → Camera → Color Analysis → Result → Backend Storage

---

## Features

- Real-time camera-based color detection
- Simple and clean user interface
- Intelligent color analysis logic
- Patch identification via Patch ID
- Backend storage of scan results

---

## Tech Stack

- Backend: FastAPI
- Database: SQLite (via SQLAlchemy)
- Frontend: HTML, JavaScript (Camera API)

---

## Project Structure

- `main.py` → Backend logic and API routes
- `camera.html` → Camera interface and color detection
- `database.py` → Database setup
- `requirements.txt` → Project dependencies

---

## Usage

Run the server:

uvicorn main:app --reload

Open in browser:

/scan/PATCH-001

---

## Important Notice

This system:

- Is NOT a medical device
- Does NOT provide diagnosis
- Is intended for awareness and demonstration purposes only

---

## Status

Prototype (Functional and Live)

---

## Author

Patch-Auri Project