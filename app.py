import os
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, g, render_template

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')

VALID_BLOOD_GROUPS = {"A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"}

app = Flask(__name__)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    first_run = not os.path.exists(DB_PATH)
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
    conn.commit()
    conn.close()
    return first_run


# ---------- Validation helpers ----------

def is_valid_phone(phone):
    digits = ''.join(ch for ch in phone if ch.isdigit())
    return 7 <= len(digits) <= 15


def validate_donor_payload(data):
    errors = []
    name = (data.get('name') or '').strip()
    phone = (data.get('phone') or '').strip()
    location = (data.get('location') or '').strip()
    blood_group = (data.get('blood_group') or '').strip().upper()
    age = data.get('age')

    if not name:
        errors.append('Name is required.')
    if not phone:
        errors.append('Phone number is required.')
    elif not is_valid_phone(phone):
        errors.append('Phone number format is invalid.')
    if not location:
        errors.append('Location is required.')
    if blood_group not in VALID_BLOOD_GROUPS:
        errors.append('A valid blood group is required.')

    try:
        age = int(age)
        if age < 18 or age > 65:
            errors.append('Age must be between 18 and 65.')
    except (TypeError, ValueError):
        errors.append('Age must be a number.')

    return errors


def validate_request_payload(data):
    errors = []
    for field, label in [
        ('patient_name', 'Patient name'),
        ('blood_group', 'Blood group'),
        ('hospital', 'Hospital name'),
        ('location', 'Location'),
        ('contact_number', 'Contact number'),
    ]:
        if not (data.get(field) or '').strip():
            errors.append(f'{label} is required.')

    blood_group = (data.get('blood_group') or '').strip().upper()
    if blood_group and blood_group not in VALID_BLOOD_GROUPS:
        errors.append('A valid blood group is required.')

    contact = (data.get('contact_number') or '').strip()
    if contact and not is_valid_phone(contact):
        errors.append('Contact number format is invalid.')

    return errors


# ---------- Routes ----------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/donors', methods=['GET'])
def list_donors():
    blood_group = request.args.get('blood_group', '').strip().upper()
    location = request.args.get('location', '').strip()

    query = 'SELECT * FROM donors WHERE 1=1'
    params = []
    if blood_group:
        query += ' AND blood_group = ?'
        params.append(blood_group)
    if location:
        query += ' AND location LIKE ?'
        params.append(f'%{location}%')
    query += ' ORDER BY created_at DESC'

    db = get_db()
    rows = db.execute(query, params).fetchall()
    return jsonify([dict(row) for row in rows])


@app.route('/api/donors', methods=['POST'])
def create_donor():
    data = request.get_json(silent=True) or request.form.to_dict()
    errors = validate_donor_payload(data)
    if errors:
        return jsonify({'errors': errors}), 400

    db = get_db()
    db.execute(
        '''INSERT INTO donors (name, age, blood_group, phone, location, last_donation_date, availability)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (
            data.get('name').strip(),
            int(data.get('age')),
            data.get('blood_group').strip().upper(),
            data.get('phone').strip(),
            data.get('location').strip(),
            (data.get('last_donation_date') or '').strip() or None,
            data.get('availability', 'Available').strip() or 'Available',
        )
    )
    db.commit()
    return jsonify({'message': 'Donor registered successfully.'}), 201


@app.route('/api/requests', methods=['GET'])
def list_requests():
    db = get_db()
    rows = db.execute('SELECT * FROM requests ORDER BY created_at DESC').fetchall()
    return jsonify([dict(row) for row in rows])


@app.route('/api/requests', methods=['POST'])
def create_request():
    data = request.get_json(silent=True) or request.form.to_dict()
    errors = validate_request_payload(data)
    if errors:
        return jsonify({'errors': errors}), 400

    db = get_db()
    db.execute(
        '''INSERT INTO requests (patient_name, blood_group, hospital, location, contact_number)
           VALUES (?, ?, ?, ?, ?)''',
        (
            data.get('patient_name').strip(),
            data.get('blood_group').strip().upper(),
            data.get('hospital').strip(),
            data.get('location').strip(),
            data.get('contact_number').strip(),
        )
    )
    db.commit()
    return jsonify({'message': 'Blood request submitted successfully.'}), 201


@app.route('/api/stats', methods=['GET'])
def stats():
    db = get_db()
    total_donors = db.execute('SELECT COUNT(*) c FROM donors').fetchone()['c']
    available_donors = db.execute(
        "SELECT COUNT(*) c FROM donors WHERE availability = 'Available'"
    ).fetchone()['c']
    pending_requests = db.execute('SELECT COUNT(*) c FROM requests').fetchone()['c']
    return jsonify({
        'total_donors': total_donors,
        'available_donors': available_donors,
        'pending_requests': pending_requests,
    })


if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
else:
    init_db()
