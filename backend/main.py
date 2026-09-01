from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
import ai_service
from database import engine, get_db

# Automatically create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI(
    title="AI Hospital Assistant API",
    description="Backend service for hospital appointments, doctor management, inquiries, and AI triage",
    version="1.0.0"
)

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 1. Health Check ---
@app.get("/")
def health_check():
    return {
        "status": "online",
        "service": "AI Hospital Assistant API",
        "version": "1.0.0"
    }

# --- 2. Database Seeding for 5 Doctors ---
@app.post("/api/v1/seed")
def seed_initial_data(db: Session = Depends(get_db)):
    # Clear existing sample data to re-seed cleanly
    db.query(models.Appointment).delete()
    db.query(models.Doctor).delete()
    db.query(models.Department).delete()
    db.commit()

    # Create Departments
    dept_cardio = models.Department(name="Cardiology", description="Heart & cardiovascular treatments")
    dept_neuro = models.Department(name="Neurology", description="Brain, spine & nervous system care")
    dept_ortho = models.Department(name="Orthopedics", description="Joints, bones & sports injury care")
    dept_derma = models.Department(name="Dermatology", description="Skin, hair & cosmetic care")
    dept_pedia = models.Department(name="Pediatrics", description="Child health & neonatal care")
    
    db.add_all([dept_cardio, dept_neuro, dept_ortho, dept_derma, dept_pedia])
    db.commit()

    # Add 5 Doctors
    doc1 = models.Doctor(
        name="Dr. Jyothilakshmi",
        department_id=dept_cardio.id,
        qualification="MD, DM (Cardiology)",
        experience_years=11,
        consultation_fee=600,
        available_days="Mon, Wed, Fri",
        op_timings="09:00 AM - 01:00 PM"
    )
    doc2 = models.Doctor(
        name="Dr. Sreelakshmi",
        department_id=dept_neuro.id,
        qualification="MBBS, MS, MCh (Neuro Surgery)",
        experience_years=14,
        consultation_fee=750,
        available_days="Tue, Thu, Sat",
        op_timings="10:00 AM - 02:00 PM"
    )
    doc3 = models.Doctor(
        name="Dr. Mahalakshmi",
        department_id=dept_ortho.id,
        qualification="MS (Orthopedics), DNB",
        experience_years=9,
        consultation_fee=500,
        available_days="Mon, Tue, Thu",
        op_timings="08:30 AM - 12:30 PM"
    )
    doc4 = models.Doctor(
        name="Dr. Anamika",
        department_id=dept_derma.id,
        qualification="MD (Dermatology)",
        experience_years=7,
        consultation_fee=450,
        available_days="Wed, Fri, Sat",
        op_timings="02:00 PM - 06:00 PM"
    )
    doc5 = models.Doctor(
        name="Dr. Ananya",
        department_id=dept_pedia.id,
        qualification="MBBS, DCH, MD (Pediatrics)",
        experience_years=8,
        consultation_fee=400,
        available_days="Mon, Wed, Fri, Sat",
        op_timings="03:00 PM - 07:00 PM"
    )

    db.add_all([doc1, doc2, doc3, doc4, doc5])
    db.commit()

    return {"message": "5 doctors and departments seeded successfully!"}

# --- 3. Doctor Management Routes ---
@app.get("/api/v1/doctors")
def list_doctors(db: Session = Depends(get_db)):
    return db.query(models.Doctor).all()

@app.post("/api/v1/doctors", response_model=schemas.DoctorResponse)
def create_doctor(doctor: schemas.DoctorCreate, db: Session = Depends(get_db)):
    new_doc = models.Doctor(**doctor.model_dump())
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc

@app.delete("/api/v1/doctors/{doctor_id}")
def delete_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doc = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")
    db.delete(doc)
    db.commit()
    return {"message": "Doctor deleted successfully"}

# --- 4. Appointment Booking Routes ---
@app.post("/api/v1/appointments", response_model=schemas.AppointmentResponse)
def create_appointment(appointment: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    doctor = db.query(models.Doctor).filter(models.Doctor.id == appointment.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    new_appointment = models.Appointment(
        doctor_id=appointment.doctor_id,
        patient_name=appointment.patient_name,
        patient_phone=appointment.patient_phone,
        appointment_date=appointment.appointment_date,
        appointment_time=appointment.appointment_time,
        status="Confirmed"
    )
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return new_appointment

@app.get("/api/v1/appointments", response_model=List[schemas.AppointmentResponse])
def list_appointments(db: Session = Depends(get_db)):
    return db.query(models.Appointment).all()

# --- 5. AI Chat Endpoint (Bilingual Support) ---
@app.post("/api/v1/chat")
def chat_with_assistant(req: schemas.ChatRequest, db: Session = Depends(get_db)):
    result = ai_service.process_chat_message(req.message, db, req.language)
    return result