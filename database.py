
import sqlite3
from datetime import datetime

# Connect to the database.
# If it doesn't exist, SQLite will create it.
conn = sqlite3.connect("hospitals.db")
conn.execute("PRAGMA foreign_keys = ON")

cursor = conn.cursor()

# Store hospital information
cursor.execute("""
CREATE TABLE IF NOT EXISTS hospitals (
    hospital_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    area TEXT NOT NULL
)
""")

# Store bed availability
cursor.execute("""
CREATE TABLE IF NOT EXISTS beds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hospital_id TEXT NOT NULL,
    bed_type TEXT NOT NULL,
    total_beds INTEGER NOT NULL,
    available_beds INTEGER NOT NULL,
    last_updated TEXT NOT NULL,
    FOREIGN KEY (hospital_id)
        REFERENCES hospitals(hospital_id),
    UNIQUE (hospital_id, bed_type)
)
""")

# Store doctor availability
cursor.execute("""
CREATE TABLE IF NOT EXISTS doctors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hospital_id TEXT NOT NULL,
    specialty TEXT NOT NULL,
    status TEXT NOT NULL,
    last_updated TEXT NOT NULL,
    FOREIGN KEY (hospital_id)
        REFERENCES hospitals(hospital_id),
    UNIQUE (hospital_id, specialty)
)
""")

# Fictional demo hospitals
hospitals = [
    ("H001", "CareBridge Demo Hospital", "Barrackpore"),
    ("H002", "CityCare Demo Centre", "Shyambazar"),
    ("H003", "HealthFirst Demo Hospital", "Salt Lake"),
    ("H004", "Lifeline Demo Centre", "Dum Dum"),
    ("H005", "Unity Demo Hospital", "New Town")
]

cursor.executemany("""
INSERT OR IGNORE INTO hospitals
(hospital_id, name, area)
VALUES (?, ?, ?)
""", hospitals)

# Fictional demo bed data
beds = [
    ("H001", "General", 20, 5),
    ("H001", "ICU", 8, 2),
    ("H002", "General", 30, 0),
    ("H002", "ICU", 10, 3),
    ("H003", "General", 25, 7),
    ("H003", "CCU", 6, 1),
    ("H004", "ICU", 12, 0),
    ("H004", "CCU", 5, 2),
    ("H005", "General", 40, 10),
    ("H005", "ICU", 10, 4)
]

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

cursor.executemany("""
INSERT OR IGNORE INTO beds
(hospital_id, bed_type, total_beds,
 available_beds, last_updated)
VALUES (?, ?, ?, ?, ?)
""", [(*bed, now) for bed in beds])

# Fictional demo doctor data
doctors = [
    ("H001", "Cardiologist", "Available"),
    ("H001", "Neurologist", "Unavailable"),
    ("H002", "Neurologist", "Available"),
    ("H002", "Orthopaedic", "Available"),
    ("H003", "Cardiologist", "Unavailable"),
    ("H003", "General Physician", "Available"),
    ("H004", "Neurologist", "Available"),
    ("H004", "General Physician", "Available"),
    ("H005", "Cardiologist", "Available"),
    ("H005", "Orthopaedic", "Unavailable")
]

cursor.executemany("""
INSERT OR IGNORE INTO doctors
(hospital_id, specialty, status, last_updated)
VALUES (?, ?, ?, ?)
""", [(*doctor, now) for doctor in doctors])

conn.commit()

print("CareBridge AI database created successfully!")
print("5 demo hospitals added.")
print("10 bed records added.")
print("10 doctor records added.")

conn.close()