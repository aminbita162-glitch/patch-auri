# Patch-Auri

Non-medical informational system for awareness and user guidance based on the interaction between a skin patch and a smartphone through NFC scanning.

---

## Overview

Patch-Auri is a functional prototype that demonstrates how a physical skin patch can interact with a smartphone interface to provide real-time user guidance based on visual color changes.

This system is designed strictly for **awareness and informational purposes only** and does not perform any medical diagnosis.

Patch-Auri is not intended to replace professional evaluation, laboratory analysis, or clinical review. It is a concept-driven prototype that shows how a low-cost physical signal can be translated into a simple digital user experience.

---

## Core Idea

Patch-Auri is built around a simple concept:

A physical skin patch changes color based on a defined reaction or condition, and a smartphone interprets this visible change through camera-based analysis.

The goal is to bridge:

- physical signals
- digital interpretation
- user guidance

In other words, the system demonstrates how a visible physical change on a patch can be captured, interpreted, and converted into a clear user-facing result.

---

## Why This Matters

This prototype demonstrates how low-cost physical signals can be translated into actionable digital feedback without requiring complex hardware.

It also shows how a lightweight software layer can connect:

- a physical patch
- smartphone interaction
- camera-based detection
- backend storage
- simple guidance output

This makes Patch-Auri relevant as an early-stage product concept in the area of smart sensing, human-centered interfaces, and digital guidance systems.

---

## How It Works

The system simulates the interaction between a smart skin patch and a mobile interface:

1. The user scans the patch through NFC interaction with a smartphone
2. The system opens a camera interface
3. The camera captures the patch color
4. The software analyzes the observed color values
5. The system detects whether a significant color change has occurred
6. A clear and user-friendly message is displayed
7. The result is optionally stored in the backend

---

## System Flow

Skin Patch → NFC Scan → Camera → Color Analysis → Result → Backend Storage

---

## Color Analysis Logic

The system uses a simple but effective software logic:

- capture the visible patch color through the smartphone camera
- extract RGB values from the observed image
- compare detected values against expected baseline ranges
- detect deviation using threshold-based logic
- map the result to a predefined response level

This allows the system to classify the observed result into predefined levels such as:

- Normal
- Monitor
- Consult / Attention

The current prototype is intentionally lightweight and designed to demonstrate the interaction logic between a physical patch and a digital system, rather than to function as a clinical-grade analytical engine.

---

## Features

- Real-time camera-based color detection
- Smartphone interaction through NFC-triggered flow
- Simple and clean user interface
- Structured color analysis logic
- Patch identification via Patch ID
- User-facing result presentation
- Backend storage of scan results

---

## Tech Stack

- Backend: FastAPI
- Database: SQLite (via SQLAlchemy)
- Frontend: HTML, JavaScript (Camera API)

---

## Project Structure

- `main.py` → Backend logic, routing, result handling, authentication, and storage
- `camera.html` → Camera interface and client-side color detection flow
- `database.py` → Database setup
- `requirements.txt` → Project dependencies

---

## Usage

Run the server:

`uvicorn main:app --reload`

Open in browser:

`/scan/PATCH-001`

---

## Important Notice

This system:

- Is **NOT** a medical device
- Does **NOT** provide diagnosis
- Does **NOT** claim clinical accuracy
- Is intended for awareness, demonstration, and prototype validation purposes only

---

## Status

Prototype (Functional and Live)

---

## Author

Patch-Auri Project