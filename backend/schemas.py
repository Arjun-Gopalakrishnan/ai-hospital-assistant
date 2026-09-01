from pydantic import BaseModel
from typing import Optional

# Doctor Schemas
class DoctorCreate(BaseModel):
    name: str
    department_id: int
    qualification: str
    experience_years: int
    consultation_fee: int
    available_days: str
    op_timings: str

class DoctorResponse(BaseModel):
    id: int
    name: str
    department_id: int
    qualification: str
    experience_years: int
    consultation_fee: int
    available_days: str
    op_timings: str

    class Config:
        from_attributes = True

# Appointment Schemas
class AppointmentCreate(BaseModel):
    doctor_id: int
    patient_name: str
    patient_phone: str
    appointment_date: str
    appointment_time: str

class AppointmentResponse(BaseModel):
    id: int
    doctor_id: int
    patient_name: str
    patient_phone: str
    appointment_date: str
    appointment_time: str
    status: str

    class Config:
        from_attributes = True

# Chatbot Schema
class ChatRequest(BaseModel):
    message: str
    language: str = "en"