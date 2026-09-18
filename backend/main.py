from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from typing import List, Optional, Any
from pydantic import BaseModel
import re

from database import SessionLocal, engine, Base
import models

# Create database tables if they do not exist
models.Base.metadata.create_all(bind=engine)


# ----------------------------------------------------
# Auto-Seeding Helper Function
# ----------------------------------------------------
def seed_doctors_if_empty(db: Session):
    """Checks if the doctor table is empty and populates default specialists matching model columns."""
    try:
        doctor_count = db.query(models.Doctor).count()
        if doctor_count == 0:
            default_doctors = [
                models.Doctor(
                    name="Dr. Jyothilakshmi",
                    qualification="MD, DM (Cardiology)",
                    department_id=1,
                    available_days="Mon, Wed, Fri",
                    op_timings="09:00 AM - 01:00 PM",
                    consultation_fee=600,
                    experience_years=11
                ),
                models.Doctor(
                    name="Dr. Sreelakshmi",
                    qualification="MBBS, MS, MCh (Neuro Surgery)",
                    department_id=2,
                    available_days="Tue, Thu, Sat",
                    op_timings="10:00 AM - 02:00 PM",
                    consultation_fee=750,
                    experience_years=14
                ),
                models.Doctor(
                    name="Dr. Mahalakshmi",
                    qualification="MS (Orthopedics), DNB",
                    department_id=3,
                    available_days="Mon, Tue, Thu",
                    op_timings="08:30 AM - 12:30 PM",
                    consultation_fee=500,
                    experience_years=9
                ),
                models.Doctor(
                    name="Dr. Anamika",
                    qualification="MD (Dermatology)",
                    department_id=4,
                    available_days="Wed, Fri, Sat",
                    op_timings="02:00 PM - 06:00 PM",
                    consultation_fee=450,
                    experience_years=7
                ),
                models.Doctor(
                    name="Dr. Ananya",
                    qualification="MBBS, DCH, MD (Pediatrics)",
                    department_id=5,
                    available_days="Mon, Wed, Fri, Sat",
                    op_timings="03:00 PM - 07:00 PM",
                    consultation_fee=400,
                    experience_years=8
                ),
            ]
            db.add_all(default_doctors)
            db.commit()
            print("Auto-seeded 5 default doctors successfully!")
    except Exception as e:
        print(f"Error during doctor auto-seed: {e}")
        db.rollback()


# ----------------------------------------------------
# Lifespan Context Manager (Startup / Shutdown)
# ----------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        seed_doctors_if_empty(db)
    finally:
        db.close()
    yield


# ----------------------------------------------------
# FastAPI App Initialization & CORS
# ----------------------------------------------------
app = FastAPI(
    title="CareFirst AI Hospital Assistant",
    description="Clinical Triage, OPD Scheduling & Hospital Management System",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------------------------------
# Database Dependency
# ----------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------------------------------------------
# Pydantic Schemas
# ----------------------------------------------------
class DoctorOut(BaseModel):
    id: int
    name: str
    qualification: Optional[str] = "Specialist"
    department_id: Optional[int] = 1
    department: Optional[str] = "General Medicine"
    available_days: Optional[str] = "Mon - Fri"
    op_timings: Optional[str] = "09:00 AM - 01:00 PM"
    consultation_fee: Optional[int] = 500
    fee: Optional[int] = 500
    experience_years: Optional[int] = 5
    initials: Optional[str] = "DR"

    class Config:
        from_attributes = True


class AppointmentCreate(BaseModel):
    patient_name: str
    patient_phone: Optional[str] = None
    phone: Optional[str] = None
    doctor_id: Optional[int] = None
    doctor_name: Optional[str] = None
    department: Optional[str] = "General OPD"
    appointment_date: Optional[str] = None
    preferred_date: Optional[str] = None
    appointment_time: Optional[str] = None
    preferred_time: Optional[str] = None


class AppointmentOut(BaseModel):
    id: int
    booking_id: Optional[str] = None
    patient_name: str
    patient_phone: Optional[str] = None
    phone: Optional[str] = None
    doctor_id: Optional[int] = None
    doctor_name: Optional[str] = None
    appointment_date: Optional[str] = None
    preferred_date: Optional[str] = None
    appointment_time: Optional[str] = None
    preferred_time: Optional[str] = None
    status: Optional[str] = "Confirmed"

    class Config:
        from_attributes = True


class ChatMessage(BaseModel):
    message: str
    language: Optional[str] = "en"


DEPARTMENT_NAMES = {
    1: "Cardiology",
    2: "Neurology",
    3: "Orthopedics",
    4: "Dermatology",
    5: "Pediatrics"
}

def format_doctor(doc):
    dept_name = DEPARTMENT_NAMES.get(getattr(doc, "department_id", 1), "Specialist")
    raw_name = getattr(doc, "name", "Doctor")
    parts = raw_name.replace("Dr.", "").strip().split(" ")
    initials = (parts[0][0] + (parts[1][0] if len(parts) > 1 else parts[0][1:2])).upper() if parts else "DR"
    fee_val = getattr(doc, "consultation_fee", 500)
    days_val = getattr(doc, "available_days", "Mon - Sat")
    timings_val = getattr(doc, "op_timings", "09:00 AM - 01:00 PM")

    return {
        "id": doc.id,
        "name": raw_name,
        "qualification": getattr(doc, "qualification", "MBBS, MD"),
        "department_id": getattr(doc, "department_id", 1),
        "department": dept_name,
        "available_days": days_val,
        "op_days": days_val,
        "op_timings": timings_val,
        "op_timing": timings_val,
        "consultation_fee": fee_val,
        "fee": fee_val,
        "experience_years": getattr(doc, "experience_years", 5),
        "initials": initials
    }


# ----------------------------------------------------
# Health Check Endpoint
# ----------------------------------------------------
@app.get("/")
def health_check():
    return {"status": "healthy", "service": "CareFirst AI Hospital Assistant"}


# ----------------------------------------------------
# Doctor Endpoints
# ----------------------------------------------------
@app.get("/api/v1/doctors")
def get_doctors(db: Session = Depends(get_db)):
    """Retrieves all doctors with automatic on-the-fly seeding if empty."""
    doctors = db.query(models.Doctor).all()
    if not doctors:
        seed_doctors_if_empty(db)
        doctors = db.query(models.Doctor).all()
    return [format_doctor(d) for d in doctors]


@app.post("/api/v1/seed")
def manual_seed(db: Session = Depends(get_db)):
    """Manual trigger to re-seed doctors."""
    seed_doctors_if_empty(db)
    count = db.query(models.Doctor).count()
    return {"status": "success", "total_doctors": count}


# ----------------------------------------------------
# Appointment Endpoints
# ----------------------------------------------------
@app.get("/api/v1/appointments")
def get_appointments(db: Session = Depends(get_db)):
    appointments = db.query(models.Appointment).order_by(models.Appointment.id.desc()).all()
    out = []
    for apt in appointments:
        out.append({
            "id": apt.id,
            "booking_id": getattr(apt, "booking_id", f"#APT-{apt.id}"),
            "patient_name": apt.patient_name,
            "patient_phone": getattr(apt, "patient_phone", getattr(apt, "phone", "N/A")),
            "phone": getattr(apt, "phone", getattr(apt, "patient_phone", "N/A")),
            "doctor_id": getattr(apt, "doctor_id", None),
            "doctor_name": getattr(apt, "doctor_name", "OPD Specialist"),
            "appointment_date": getattr(apt, "appointment_date", getattr(apt, "preferred_date", "Today")),
            "preferred_date": getattr(apt, "preferred_date", getattr(apt, "appointment_date", "Today")),
            "appointment_time": getattr(apt, "appointment_time", getattr(apt, "preferred_time", "General OPD")),
            "preferred_time": getattr(apt, "preferred_time", getattr(apt, "appointment_time", "General OPD")),
            "status": getattr(apt, "status", "Confirmed")
        })
    return out


@app.post("/api/v1/appointments", status_code=status.HTTP_201_CREATED)
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    count = db.query(models.Appointment).count() + 1
    booking_id = f"CF-2026-{count:04d}"
    phone_number = appointment.patient_phone or appointment.phone or "N/A"
    app_date = appointment.appointment_date or appointment.preferred_date or "2026-04-15"
    app_time = appointment.appointment_time or appointment.preferred_time or "09:30 AM"

    new_apt_data = {
        "patient_name": appointment.patient_name,
    }
    apt_columns = [c.name for c in models.Appointment.__table__.columns]
    if "booking_id" in apt_columns:
        new_apt_data["booking_id"] = booking_id
    if "patient_phone" in apt_columns:
        new_apt_data["patient_phone"] = phone_number
    if "phone" in apt_columns:
        new_apt_data["phone"] = phone_number
    if "doctor_id" in apt_columns:
        new_apt_data["doctor_id"] = appointment.doctor_id or 1
    if "doctor_name" in apt_columns:
        new_apt_data["doctor_name"] = appointment.doctor_name or "Dr. Jyothilakshmi"
    if "department" in apt_columns:
        new_apt_data["department"] = appointment.department or "General OPD"
    if "appointment_date" in apt_columns:
        new_apt_data["appointment_date"] = app_date
    if "preferred_date" in apt_columns:
        new_apt_data["preferred_date"] = app_date
    if "appointment_time" in apt_columns:
        new_apt_data["appointment_time"] = app_time
    if "preferred_time" in apt_columns:
        new_apt_data["preferred_time"] = app_time
    if "status" in apt_columns:
        new_apt_data["status"] = "Confirmed"

    new_apt = models.Appointment(**new_apt_data)
    db.add(new_apt)
    db.commit()
    db.refresh(new_apt)

    return {
        "id": new_apt.id,
        "booking_id": booking_id,
        "patient_name": new_apt.patient_name,
        "appointment_date": app_date,
        "appointment_time": app_time,
        "status": "Confirmed"
    }


# ----------------------------------------------------
# Bilingual AI Assistant / Triage Endpoint
# ----------------------------------------------------
@app.post("/api/v1/chat")
def hospital_ai_triage(chat: ChatMessage, db: Session = Depends(get_db)):
    user_msg = chat.message.lower().strip()

    # Emergency Detection
    emergency_keywords = [
        "emergency", "chest pain", "heart attack", "accident", "bleeding",
        "breathless", "ambulance", "oxygen", "stroke", "unconscious",
        "??????????", "?????", "??????????????"
    ]
    if any(re.search(rf"\b{re.escape(k)}\b", user_msg) for k in emergency_keywords):
        return {
            "type": "emergency",
            "reply": (
                "?? **EMERGENCY DETECTED**: Please reach our 24/7 Emergency Casualty immediately. "
                "Contact our emergency hotline: **+91 484 2900000** or call for an ambulance."
            ),
            "response": (
                "?? **EMERGENCY DETECTED**: Please reach our 24/7 Emergency Casualty immediately. "
                "Contact our emergency hotline: **+91 484 2900000** or call for an ambulance."
            )
        }

    # Department & Doctor Lookups
    doctors = db.query(models.Doctor).all()
    if not doctors:
        seed_doctors_if_empty(db)
        doctors = db.query(models.Doctor).all()

    formatted_docs = [format_doctor(d) for d in doctors]

    if any(k in user_msg for k in ["cardio", "heart", "jyothilakshmi", "?????"]):
        doc = next((d for d in formatted_docs if d["department_id"] == 1), None)
        if doc:
            txt = f"?? **{doc['name']}** ({doc['qualification']}) specializes in {doc['department']}.\n\n?? OP Days: {doc['op_days']}\n? Timings: {doc['op_timings']}\n?? Consultation Fee: ?{doc['fee']}"
            return {"type": "info", "reply": txt, "response": txt}

    if any(k in user_msg for k in ["neuro", "brain", "spine", "sreelakshmi", "??????"]):
        doc = next((d for d in formatted_docs if d["department_id"] == 2), None)
        if doc:
            txt = f"?? **{doc['name']}** ({doc['qualification']}) specializes in {doc['department']}.\n\n?? OP Days: {doc['op_days']}\n? Timings: {doc['op_timings']}\n?? Consultation Fee: ?{doc['fee']}"
            return {"type": "info", "reply": txt, "response": txt}

    if any(k in user_msg for k in ["ortho", "bone", "joint", "mahalakshmi", "?????"]):
        doc = next((d for d in formatted_docs if d["department_id"] == 3), None)
        if doc:
            txt = f"?? **{doc['name']}** ({doc['qualification']}) specializes in {doc['department']}.\n\n?? OP Days: {doc['op_days']}\n? Timings: {doc['op_timings']}\n?? Consultation Fee: ?{doc['fee']}"
            return {"type": "info", "reply": txt, "response": txt}

    if any(k in user_msg for k in ["derma", "skin", "hair", "anamika", "?????"]):
        doc = next((d for d in formatted_docs if d["department_id"] == 4), None)
        if doc:
            txt = f"? **{doc['name']}** ({doc['qualification']}) specializes in {doc['department']}.\n\n?? OP Days: {doc['op_days']}\n? Timings: {doc['op_timings']}\n?? Consultation Fee: ?{doc['fee']}"
            return {"type": "info", "reply": txt, "response": txt}

    if any(k in user_msg for k in ["pediatric", "child", "baby", "ananya", "????????"]):
        doc = next((d for d in formatted_docs if d["department_id"] == 5), None)
        if doc:
            txt = f"?? **{doc['name']}** ({doc['qualification']}) specializes in {doc['department']}.\n\n?? OP Days: {doc['op_days']}\n? Timings: {doc['op_timings']}\n?? Consultation Fee: ?{doc['fee']}"
            return {"type": "info", "reply": txt, "response": txt}

    if any(k in user_msg for k in ["doctor", "doctors", "fee", "cost", "list", "??????"]):
        summary = "\n".join([f"� **{d['name']}** ({d['department']}) � ?{d['fee']} | {d['op_days']}" for d in formatted_docs])
        txt = f"Here is our active specialist directory:\n\n{summary}\n\nYou can book an appointment directly using the booking form below!"
        return {"type": "info", "reply": txt, "response": txt}

    txt = (
        "Hello! I am your CareFirst Hospital Assistant. I can help you with:\n"
        "� Doctor schedules & OPD timings (Cardiology, Neurology, Ortho, etc.)\n"
        "� Consultation fees & department information\n"
        "� Emergency casualty support\n\n"
        "How can I assist you today?"
    )
    return {"type": "general", "reply": txt, "response": txt}