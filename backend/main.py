from database import SessionLocal, engine, Base
import models

# Ensure tables are created
models.Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        # Check if doctors exist; if not, seed them automatically
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
            print("Auto-seeded doctors successfully on startup!")
    except Exception as e:
        print(f"Error during auto-seed: {e}")
        db.rollback()
    finally:
        db.close()