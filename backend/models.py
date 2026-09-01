from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, Time
from sqlalchemy.orm import relationship
from database import Base

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    doctors = relationship("Doctor", back_populates="department")


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    qualification = Column(String(100), nullable=False)
    experience_years = Column(Integer, default=0)
    consultation_fee = Column(Integer, nullable=False)
    available_days = Column(String(100), nullable=False)  # e.g. "Mon, Wed, Fri"
    op_timings = Column(String(100), nullable=False)      # e.g. "09:00 AM - 01:00 PM"

    department = relationship("Department", back_populates="doctors")
    appointments = relationship("Appointment", back_populates="doctor")


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    patient_name = Column(String(150), nullable=False)
    patient_phone = Column(String(20), nullable=False)
    appointment_date = Column(String(50), nullable=False)
    appointment_time = Column(String(50), nullable=False)
    status = Column(String(50), default="Confirmed")

    doctor = relationship("Doctor", back_populates="appointments")