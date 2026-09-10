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

Method,Endpoint,Description
GET,/,Health check endpoint
GET,/api/v1/doctors,Retrieve all registered specialist doctors
POST,/api/v1/doctors,Create a new specialist entry
DELETE,/api/v1/doctors/{id},Delete a specialist record
GET,/api/v1/appointments,List all booked appointments
POST,/api/v1/appointments,Create a new patient appointment
POST,/api/v1/chat,AI conversational triage & intent processing
POST,/api/v1/seed,Seed default clinical specialists and OPD slots
🚀 Local Setup & Installation
1. Clone the Repository
git clone [https://github.com/Arjun-Gopalakrishnan/ai-hospital-assistant.git](https://github.com/Arjun-Gopalakrishnan/ai-hospital-assistant.git)
cd ai-hospital-assistant
2. Backend SetupBashcd backend
python -m venv venv
.\venv\Scripts\activate   # Windows (or source venv/bin/activate on Linux/macOS)
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
Seed initial doctor data locally:
curl -X POST [http://127.0.0.1:8000/api/v1/seed](http://127.0.0.1:8000/api/v1/seed)
3. Open index.html directly in any web browser, or serve it locally from the project root:
python -m http.server 3000
Navigate to http://localhost:3000 to interact with the interface.
🧪 Testing & Verification
API Docs: Open http://127.0.0.1:8000/docs to interactively test all REST endpoints.

Chatbot Queries:

Availability: "When is the cardiologist available?"

Fees: "How much is the consultation fee for neurology?"

Emergency: "Emergency chest pain, send ambulance!"

Malayalam: "Doctor eppozha varunne?"

---
