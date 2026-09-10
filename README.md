# CareFirst AI Hospital Assistant Platform

An intelligent healthcare web platform built with FastAPI, SQLite, and Tailwind CSS. Features bilingual AI-driven appointment triage, real-time OPD directory management, and administrative scheduling queues.

---

## 🔗 Live Deployments

* **Live Web Application:** [https://arjun-gopalakrishnan.github.io/ai-hospital-assistant/](https://arjun-gopalakrishnan.github.io/ai-hospital-assistant/)
* **Interactive API Documentation (Swagger):** [https://ai-hospital-assistant-vif4.onrender.com/docs](https://ai-hospital-assistant-vif4.onrender.com/docs)
* **Source Repository:** [https://github.com/Arjun-Gopalakrishnan/ai-hospital-assistant](https://github.com/Arjun-Gopalakrishnan/ai-hospital-assistant)

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
* **Cloud & Hosting:** Render (FastAPI Web Service), GitHub Pages (Static Frontend)

---

## 🏗️ System Architecture

```text
[ Browser / GitHub Pages ]
       │  (HTTPS / REST)
       ▼
[ FastAPI Backend (Render) ]
   ├── /api/v1/doctors      ──► [ SQLite Database ]
   ├── /api/v1/appointments ──► [ SQLite Database ]
   ├── /api/v1/seed         ──► [ Database Seeder ]
   └── /api/v1/chat         ──► [ Rule-based Bilingual NLP Engine ]
