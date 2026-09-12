from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from typing import List, Optional
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
    """Checks if the doctor table is empty and populates default specialists."""
    try:
        doctor_count = db.query(models.Doctor).count()
        if doctor_count == 0:
            default_doctors = [
                models.Doctor(
                    name="Dr. Jyothilakshmi",
                    qualification="MD, DM (Cardiology)",
                    department="Cardiology",
                    op_days="Mon, Wed, Fri",
                    op_timing="09:00 AM - 01:00 PM",
                    fee=600,
                    initials="JY"
                ),
                models.Doctor(
                    name="Dr. Sreelakshmi",
                    qualification="MBBS, MS, MCh (Neuro Surgery)",
                    department="Neurology",
                    op_days="Tue, Thu, Sat",
                    op_timing="10:00 AM - 02:00 PM",
                    fee=750,
                    initials="SR"
                ),
                models.Doctor(
                    name="Dr. Mahalakshmi",
                    qualification="MS (Orthopedics), DNB",
                    department="Orthopedics",
                    op_days="Mon, Tue, Thu",
                    op_timing="08:30 AM - 12:30 PM",
                    fee=500,
                    initials="MA"
                ),
                models.Doctor(
                    name="Dr. Anamika",
                    qualification="MD (Dermatology)",
                    department="Dermatology",
                    op_days="Wed, Fri, Sat",
                    op_timing="02:00 PM - 06:00 PM",
                    fee=450,
                    initials="AN"
                ),
                models.Doctor(
                    name="Dr. Ananya",
                    qualification="MBBS, DCH, MD (Pediatrics)",
                    department="Pediatrics",
                    op_days="Mon, Wed, Fri, Sat",
                    op_timing="03:00 PM - 07:00 PM",
                    fee=400,
                    initials="AN"
                ),
            ]
            db.add_all(default_doctors)
            db.commit()
            print("Auto-seeded 5 default doctors successfully!")
    except Exception as e:
        print(f"Error during doctor auto-seed: {e}")
        db.rollback()


# ----------------------------------------------------
# Lifespan Context Manager (Modern FastAPI Startup)
# ----------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs automatically on application boot
    db = SessionLocal()
    try:
        seed_doctors_if_empty(db)
    finally:
        db.close()
    yield
    # Code below yield runs on application shutdown (if needed)


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
    qualification: str
    department: str
    op_days: str
    op_timing: str
    fee: int
    initials: str

    class Config:
        from_attributes = True


class AppointmentCreate(BaseModel):
    patient_name: str
    phone: str
    department: str
    doctor_name: Optional[str] = None
    preferred_date: str
    preferred_time: Optional[str] = None


class AppointmentOut(BaseModel):
    id: int
    booking_id: str
    patient_name: str
    phone: str
    department: str
    doctor_name: Optional[str]
    preferred_date: str
    preferred_time: Optional[str]
    status: str

    class Config:
        from_attributes = True


class ChatMessage(BaseModel):
    message: str
    language: Optional[str] = "en"


# ----------------------------------------------------
# Health Check Endpoint
# ----------------------------------------------------
@app.get("/")
def health_check():
    return {"status": "healthy", "service": "CareFirst AI Hospital Assistant"}


# ----------------------------------------------------
# Doctor Endpoints
# ----------------------------------------------------
@app.get("/api/v1/doctors", response_model=List[DoctorOut])
def get_doctors(db: Session = Depends(get_db)):
    """
    Retrieves all doctors. If the database was reset or empty,
    it automatically seeds the default doctors before returning.
    """
    doctors = db.query(models.Doctor).all()
    if not doctors:
        seed_doctors_if_empty(db)
        doctors = db.query(models.Doctor).all()
    return doctors


@app.post("/api/v1/seed")
def manual_seed(db: Session = Depends(get_db)):
    """Manual trigger to re-seed doctors if needed."""
    seed_doctors_if_empty(db)
    count = db.query(models.Doctor).count()
    return {"status": "success", "total_doctors": count}


# ----------------------------------------------------
# Appointment Endpoints
# ----------------------------------------------------
@app.get("/api/v1/appointments", response_model=List[AppointmentOut])
def get_appointments(db: Session = Depends(get_db)):
    """Retrieves all confirmed appointments for the admin queue."""
    appointments = db.query(models.Appointment).order_by(models.Appointment.id.desc()).all()
    return appointments


@app.post("/api/v1/appointments", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    """Creates a new appointment with an auto-generated CF booking ID."""
    count = db.query(models.Appointment).count() + 1
    generated_id = f"CF-2026-{count:04d}"

    new_appointment = models.Appointment(
        booking_id=generated_id,
        patient_name=appointment.patient_name,
        phone=appointment.phone,
        department=appointment.department,
        doctor_name=appointment.doctor_name,
        preferred_date=appointment.preferred_date,
        preferred_time=appointment.preferred_time or "General OPD",
        status="Confirmed"
    )
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return new_appointment


# ----------------------------------------------------
# Bilingual AI Assistant / Triage Endpoint
# ----------------------------------------------------
@app.post("/api/v1/chat")
def hospital_ai_triage(chat: ChatMessage, db: Session = Depends(get_db)):
    """
    Handles natural language queries in English and Malayalam/Manglish.
    Covers emergency triage, doctor lookups, fees, and OP timings.
    """
    user_msg = chat.message.lower().strip()

    # Emergency Detection
    emergency_keywords = [
        "emergency", "chest pain", "heart attack", "accident", "bleeding",
        "breathless", "ambulance", "oxygen", "stroke", "unconscious",
        "നെഞ്ചുവേദന", "അപകടം", "ശ്വാസമെടുക്കാൻ"
    ]
    if any(re.search(rf"\b{re.escape(k)}\b", user_msg) for k in emergency_keywords):
        return {
            "type": "emergency",
            "reply": (
                "🚨 **EMERGENCY DETECTED**: Please reach our 24/7 Emergency Casualty immediately. "
                "Contact our emergency hotline: **+91 484 2800 911** or call for an ambulance."
            )
        }

    # Department & Doctor Lookups
    doctors = db.query(models.Doctor).all()
    if not doctors:
        seed_doctors_if_empty(db)
        doctors = db.query(models.Doctor).all()

    # Match cardiology
    if any(k in user_msg for k in ["cardio", "heart", "jyothilakshmi", "ഹൃദയം"]):
        doc = next((d for d in doctors if "Cardiology" in d.department), None)
        if doc:
            return {
                "type": "info",
                "reply": f"❤️ **{doc.name}** ({doc.qualification}) specializes in {doc.department}.\n\n📅 OP Days: {doc.op_days}\n⏰ Timings: {doc.op_timing}\n💵 Consultation Fee: ₹{doc.fee}"
            }

    # Match neurology
    if any(k in user_msg for k in ["neuro", "brain", "spine", "sreelakshmi", "തലവേദന"]):
        doc = next((d for d in doctors if "Neurology" in d.department), None)
        if doc:
            return {
                "type": "info",
                "reply": f"🧠 **{doc.name}** ({doc.qualification}) specializes in {doc.department}.\n\n📅 OP Days: {doc.op_days}\n⏰ Timings: {doc.op_timing}\n💵 Consultation Fee: ₹{doc.fee}"
            }

    # Match orthopedics
    if any(k in user_msg for k in ["ortho", "bone", "joint", "mahalakshmi", "അസ്ഥി"]):
        doc = next((d for d in doctors if "Orthopedics" in d.department), None)
        if doc:
            return {
                "type": "info",
                "reply": f"🦴 **{doc.name}** ({doc.qualification}) specializes in {doc.department}.\n\n📅 OP Days: {doc.op_days}\n⏰ Timings: {doc.op_timing}\n💵 Consultation Fee: ₹{doc.fee}"
            }

    # Match dermatology
    if any(k in user_msg for k in ["derma", "skin", "hair", "anamika", "ചർമ്മ"]):
        doc = next((d for d in doctors if "Dermatology" in d.department), None)
        if doc:
            return {
                "type": "info",
                "reply": f"✨ **{doc.name}** ({doc.qualification}) specializes in {doc.department}.\n\n📅 OP Days: {doc.op_days}\n⏰ Timings: {doc.op_timing}\n💵 Consultation Fee: ₹{doc.fee}"
            }

    # Match pediatrics
    if any(k in user_msg for k in ["pediatric", "child", "baby", "ananya", "കുട്ടികൾ"]):
        doc = next((d for d in doctors if "Pediatrics" in d.department), None)
        if doc:
            return {
                "type": "info",
                "reply": f"👶 **{doc.name}** ({doc.qualification}) specializes in {doc.department}.\n\n📅 OP Days: {doc.op_days}\n⏰ Timings: {doc.op_timing}\n💵 Consultation Fee: ₹{doc.fee}"
            }

    # Match general doctor list / fees query
    if any(k in user_msg for k in ["doctor", "doctors", "fee", "cost", "list", "ഡോക്ടർ"]):
        summary = "\n".join([f"• **{d.name}** ({d.department}) — ₹{d.fee} | {d.op_days}" for d in doctors])
        return {
            "type": "info",
            "reply": f"Here is our active specialist directory:\n\n{summary}\n\nYou can book an appointment directly using the booking form below!"
        }

    # Default fallback response
    return {
        "type": "general",
        "reply": (
            "Hello! I am your CareFirst Hospital Assistant. I can help you with:\n"
            "• Doctor schedules & OPD timings (Cardiology, Neurology, Ortho, etc.)\n"
            "• Consultation fees & department information\n"
            "• Emergency casualty support\n\n"
            "How can I assist you today?"
        )
    }