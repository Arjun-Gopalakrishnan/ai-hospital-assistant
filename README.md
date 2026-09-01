# CareFirst AI Hospital Assistant Platform

An intelligent healthcare web platform built with FastAPI, SQLite, and Tailwind CSS. Features bilingual AI-driven appointment triage, real-time OPD directory management, and administrative scheduling queues.

---

## 🌟 Key Features

* **Bilingual AI Clinical Assistant:** Supports voice and text interactions in English and Malayalam/Manglish.
* **Specialist Directory:** Comprehensive scheduling, qualifications, and consultation fee tracking for clinical doctors.
* **Interactive Booking:** Dual-channel booking via natural conversational triage or modal appointment forms.
* **Admin Management Queue:** Real-time synchronization of patient queues and appointment confirmation workflows.
* **Safety Protocols:** Automated 24/7 casualty routing and emergency keyword detection.

---

## 🛠️ Tech Stack

* **Backend:** FastAPI, Python 3, SQLAlchemy, Pydantic, Uvicorn
* **Database:** SQLite
* **Frontend:** HTML5, Tailwind CSS, Lucide Icons, Web Speech API

---

## 🚀 Local Setup & Installation

### 1. Backend Setup
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate   # Windows (or source venv/bin/activate on Linux/Mac)
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
