"""
Seed script for the Blood Donor Management MVP.
Run standalone with: python seed.py
Populates the donors table with 12 sample donors covering all 8 blood
groups, spread across 5 Indian cities, with mixed availability.
"""
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')

SAMPLE_DONORS = [
    ("Arjun Sharma", 28, "A+", "9876543210", "Mumbai", "2025-03-12", "Available"),
    ("Priya Iyer", 34, "O-", "9123456780", "Chennai", "2025-05-01", "Available"),
    ("Rohan Verma", 41, "B+", "9988776655", "Delhi", "2024-11-20", "Unavailable"),
    ("Sneha Reddy", 25, "AB+", "9012345678", "Bangalore", "2025-06-15", "Available"),
    ("Karan Mehta", 37, "O+", "9765432109", "Pune", "2025-01-08", "Available"),
    ("Ananya Nair", 22, "A-", "9345678901", "Chennai", "2025-04-22", "Available"),
    ("Vikram Singh", 45, "B-", "9871234560", "Delhi", "2024-09-30", "Unavailable"),
    ("Meera Joshi", 30, "AB-", "9456123780", "Mumbai", "2025-02-14", "Available"),
    ("Aditya Kulkarni", 52, "O+", "9234567810", "Pune", "2025-05-28", "Available"),
    ("Divya Krishnan", 27, "A+", "9678901234", "Bangalore", "2024-12-05", "Unavailable"),
    ("Rahul Gupta", 33, "B+", "9812345670", "Delhi", "2025-06-30", "Available"),
    ("Kavya Pillai", 24, "O-", "9567890123", "Chennai", "2025-03-19", "Available"),
]


def seed():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS donors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            blood_group TEXT NOT NULL,
            phone TEXT NOT NULL,
            location TEXT NOT NULL,
            last_donation_date TEXT,
            availability TEXT NOT NULL DEFAULT 'Available',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            blood_group TEXT NOT NULL,
            hospital TEXT NOT NULL,
            location TEXT NOT NULL,
            contact_number TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cur.execute('SELECT COUNT(*) FROM donors')
    existing = cur.fetchone()[0]
    if existing > 0:
        print(f"Donors table already has {existing} rows. Skipping seed to avoid duplicates.")
        print("Delete database.db first if you want a fresh seed.")
        conn.close()
        return

    cur.executemany(
        '''INSERT INTO donors (name, age, blood_group, phone, location, last_donation_date, availability)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        SAMPLE_DONORS
    )
    conn.commit()
    print(f"Seeded {len(SAMPLE_DONORS)} donors into {DB_PATH}")
    conn.close()


if __name__ == '__main__':
    seed()
