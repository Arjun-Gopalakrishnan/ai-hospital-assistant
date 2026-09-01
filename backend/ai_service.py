import re
from sqlalchemy.orm import Session
import models

# Bilingual Emergency Keywords (English + Manglish/Malayalam)
EMERGENCY_KEYWORDS = [
    "chest pain", "heart attack", "difficulty breathing", "unconscious", 
    "bleeding heavily", "severe accident", "stroke", "poisoning", "casualty",
    "nenju vedana", "shwasam muttal", "raktham", "bodham illa", "accident"
]

def check_emergency(user_query: str, lang: str) -> str | None:
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in user_query.lower():
            if lang == "ml":
                return "⚠️ **അടിയന്തര മുന്നറിയിപ്പ്**: ദയവായി ഉടൻ തന്നെ 24/7 കാഷ്വാലിറ്റി ഡെസ്കുമായി ബന്ധപ്പെടുക: **+91 484 2900000** അല്ലെങ്കിൽ **108**-ൽ വിളിക്കുക."
            return (
                "⚠️ **EMERGENCY ALERT**: If you or the patient are experiencing acute symptoms, "
                "please contact our 24/7 Casualty Desk immediately at **+91 484 2900000** or call **108**."
            )
    return None

def process_chat_message(user_message: str, db: Session, lang: str = "en") -> dict:
    msg_lower = user_message.lower()

    # 1. Emergency Safety Filter
    emergency_msg = check_emergency(user_message, lang)
    if emergency_msg:
        return {"response": emergency_msg, "intent": "emergency_alert"}

    # 2. Dynamic Appointment Booking
    # Keywords: book, appointment, booking, "book cheyyanam", "appointment venam"
    if any(k in msg_lower for k in ["book", "appointment", "booking", "cheyyanam", "venam"]) and any(char.isdigit() for char in user_message):
        doctors = db.query(models.Doctor).all()
        matched_doctor = doctors[0] # Default fallback
        for doc in doctors:
            if doc.name.split()[-1].lower() in msg_lower or doc.name.lower() in msg_lower:
                matched_doctor = doc
                break

        phone_match = re.search(r'(\+?\d[\d\s\-]{8,14}\d)', user_message)
        patient_phone = phone_match.group(1).strip() if phone_match else "Not Provided"

        name_match = re.search(r'(?:for|name|peru)\s+([A-Za-z\s]+?)(?:,|\.|\bphone|\bnumber|\bon|\bat|$)', user_message, re.IGNORECASE)
        patient_name = name_match.group(1).strip() if name_match else "Patient"

        date_match = re.search(r'(\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4})', user_message)
        appointment_date = date_match.group(1) if date_match else "2026-08-25"

        time_match = re.search(r'(\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm)?)', user_message)
        appointment_time = time_match.group(1).upper() if time_match else "10:00 AM"

        new_app = models.Appointment(
            doctor_id=matched_doctor.id, patient_name=patient_name, patient_phone=patient_phone,
            appointment_date=appointment_date, appointment_time=appointment_time, status="Confirmed"
        )
        db.add(new_app)
        db.commit()
        db.refresh(new_app)

        if lang == "ml":
            resp = (f"✅ **അപ്പോയിന്റ്മെന്റ് ഉറപ്പാക്കി!**\n\n• **ബുക്കിംഗ് ഐഡി:** #APT-{new_app.id}\n"
                    f"• **ഡോക്ടർ:** {matched_doctor.name}\n• **രോഗി:** {patient_name}\n"
                    f"• **തിയ്യതി & സമയം:** {appointment_date} at {appointment_time}\n"
                    f"• **ഫീസ്:** ₹{matched_doctor.consultation_fee}")
        else:
            resp = (f"✅ **Appointment Confirmed!**\n\n• **Booking ID:** #APT-{new_app.id}\n"
                    f"• **Doctor:** {matched_doctor.name}\n• **Patient:** {patient_name}\n"
                    f"• **Date & Slot:** {appointment_date} at {appointment_time}\n"
                    f"• **Fee:** ₹{matched_doctor.consultation_fee}")
        return {"response": resp, "intent": "book_appointment"}

    # 3. Doctor Schedules Query (Manglish: "doctorine kaanan", "samayam", "fee", "specialist")
    if any(k in msg_lower for k in ["doctor", "specialist", "timings", "available", "fee", "kaanan", "samayam", "cardiology", "neurology", "orthopedics"]):
        doctors = db.query(models.Doctor).all()
        matched_docs = [d for d in doctors if d.name.lower() in msg_lower or (d.department and d.department.name.lower() in msg_lower)]
        if not matched_docs:
            matched_docs = doctors

        if lang == "ml":
            resp = "ലഭ്യമായ ഡോക്ടർമാർ:\n\n"
            for doc in matched_docs:
                dept = doc.department.name if doc.department else "General"
                resp += f"• **{doc.name}** ({dept})\n  - സമയം: {doc.available_days} ({doc.op_timings})\n  - ഫീസ്: ₹{doc.consultation_fee}\n\n"
        else:
            resp = "Here are our available specialists:\n\n"
            for doc in matched_docs:
                dept = doc.department.name if doc.department else "General"
                resp += f"• **{doc.name}** ({dept})\n  - OP Days: {doc.available_days} ({doc.op_timings})\n  - Fee: ₹{doc.consultation_fee}\n\n"
        return {"response": resp, "intent": "get_doctors"}

    # 4. Fallback Default
    if lang == "ml":
        return {"response": "നമസ്കാരം! ഞാൻ നിങ്ങളുടെ കെയർഫസ്റ്റ് ഹോസ്പിറ്റൽ അസിസ്റ്റന്റ് ആണ്. നിങ്ങൾക്ക് ഡോക്ടർമാരുടെ സമയം ചോദിക്കാനും അപ്പോയിന്റ്മെന്റ് ബുക്ക് ചെയ്യാനും കഴിയും.", "intent": "general_inquiry"}
    
    return {"response": "Hello! I am your CareFirst Hospital Assistant. Ask me about doctor schedules, fees, or book an appointment directly here.", "intent": "general_inquiry"}