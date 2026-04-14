# Project Structure

This document describes the architecture and structure of the Patch-Auri project.

---

## Overview

Patch-Auri is a minimal and focused prototype designed to demonstrate the interaction between a skin patch and a smartphone interface.

The project follows a simple structure to keep the system clear, maintainable, and easy to understand.

---

## Architecture

The system is composed of two main parts:

- Backend (API and data handling)
- Frontend (camera interface and user interaction)

---

## Flow

Skin Patch → NFC Scan → Camera Interface → Color Analysis → Result → Backend Storage

---

## File Structure

patch-auri/
│
├── main.py
├── camera.html
├── database.py
├── requirements.txt
├── README.md
├── project-structure.md
│
└── patches.db

---

## File Descriptions

### main.py
Core backend application built with FastAPI.

Handles:
- Routing
- Scan entry (`/scan/{patch_id}`)
- Camera page serving
- Scan result storage
- Result display

---

### camera.html
Frontend interface responsible for:

- Accessing the device camera
- Capturing patch image
- Performing color analysis
- Displaying results to the user
- Sending data to backend

---

### database.py
Defines database connection and session management using SQLAlchemy.

---

### requirements.txt
Lists project dependencies required to run the application.

---

### README.md
Provides a complete overview of the project, including purpose, usage, and technical details.

---

### project-structure.md
Documents the internal architecture and structure of the project.

---

### patches.db
SQLite database file used to store:

- Patch data
- Scan results

---

## Design Principles

- Minimal and focused architecture
- Clear separation between frontend and backend
- Real-time interaction simulation
- Easy to understand and extend

---

## Notes

This project is a prototype and focuses on demonstrating system behavior rather than production-level architecture.