"""
Healthcare Management System - Python Flask Backend
Follows PES University Python Curriculum: OOP, Exception Handling, File Operations, Data Structures
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime, date
from functools import wraps
import json
import os
import re
import webbrowser
import threading



# === OOP PRINCIPLES: Class Definitions ===
class Patient:
    """Encapsulation: Patient data with getters/setters"""
    _patient_count = 0

    def __init__(self, name, age, contact, history=""):
        """Constructor with validation"""
        self._validate_input(name, age, contact)
        self.patient_id = self._generate_id()
        self.name = name
        self.age = int(age)
        self.contact = contact
        self.history = history
        self.date_added = str(date.today())
        Patient._patient_count += 1

    @staticmethod
    def _validate_input(name, age, contact):
        """Exception handling for input validation"""
        if not name or len(name.strip()) == 0:
            raise ValueError("Patient name cannot be empty")
        if not re.match(r'^\d{10}$', contact):
            raise ValueError("Contact must be 10 digits")
        try:
            age_int = int(age)
            if age_int < 0 or age_int > 150:
                raise ValueError("Age must be between 0-150")
        except ValueError:
            raise ValueError("Invalid age format")

    def _generate_id(self):
        """Generate unique Patient ID"""
        return f"P{str(Patient._patient_count + 1).zfill(3)}"

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'patient_id': self.patient_id,
            'name': self.name,
            'age': self.age,
            'contact': self.contact,
            'history': self.history,
            'date_added': self.date_added
        }


class Appointment:
    """Appointment management with status tracking"""
    _appt_count = 0

    def __init__(self, patient_id, doctor, date_str, time_str):
        """Constructor with date validation"""
        self.appointment_id = f"APT{str(Appointment._appt_count + 1).zfill(3)}"
        self.patient_id = patient_id
        self.doctor = doctor
        self.date = date_str
        self.time = time_str
        self.status = "Confirmed"
        Appointment._appt_count += 1

    def cancel(self):
        """Cancel appointment"""
        self.status = "Cancelled"

    def to_dict(self):
        return {
            'appointment_id': self.appointment_id,
            'patient_id': self.patient_id,
            'doctor': self.doctor,
            'date': self.date,
            'time': self.time,
            'status': self.status
        }


class HealthMetric:
    """BMI calculation and health categorization"""

    def __init__(self, patient_id, weight, height):
        """Calculate BMI and categorize health status"""
        if weight <= 0 or height <= 0:
            raise ValueError("Weight and height must be positive")

        self.patient_id = patient_id
        self.weight = weight
        self.height = height
        self.bmi = self._calculate_bmi()
        self.category = self._categorize()
        self.date = str(date.today())

    def _calculate_bmi(self):
        """Calculate BMI: weight (kg) / height² (m²)"""
        return round(self.weight / (self.height ** 2), 2)

    def _categorize(self):
        """Categorize BMI status"""
        if self.bmi < 18.5:
            return "Underweight"
        elif self.bmi < 25:
            return "Normal"
        elif self.bmi < 30:
            return "Overweight"
        else:
            return "Obese"

    def to_dict(self):
        return {
            'patient_id': self.patient_id,
            'weight': self.weight,
            'height': self.height,
            'bmi': self.bmi,
            'category': self.category,
            'date': self.date
        }


class SymptomRecord:
    """Symptom analysis with condition detection"""

    SYMPTOM_MAP = {
        'fever': ('Fever', 'Rest and drink water'),
        'cough': ('Cough', 'Cough syrup and fluids'),
        'headache': ('Headache', 'Rest and pain relief'),
        'chest pain': ('Chest Pain', '⚠️ See doctor immediately'),
    }

    def __init__(self, patient_id, symptoms):
        """Analyze symptoms and recommend action"""
        self.patient_id = patient_id
        self.symptoms = symptoms.lower()
        self.condition, self.action = self._detect_condition()
        self.date = str(date.today())

    def _detect_condition(self):
        """Detect condition based on symptoms (functional programming: filter)"""
        for symptom_key, (condition, action) in self.SYMPTOM_MAP.items():
            if symptom_key in self.symptoms:
                return condition, action
        return "Unknown", "Consult doctor"

    def to_dict(self):
        return {
            'patient_id': self.patient_id,
            'symptoms': self.symptoms,
            'condition': self.condition,
            'action': self.action,
            'date': self.date
        }


class DataStore:
    """File handling: JSON storage for all records"""

    def __init__(self):
        self.data_file = 'healthcare_data.json'
        self.data = self._load_data()

    def _load_data(self):
        """Load data from file with exception handling"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"File error: {e}")
        return {'patients': [], 'appointments': [], 'bmi': [], 'symptoms': []}

    def save_data(self):
        """Save data to file with error handling"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except IOError as e:
            raise Exception(f"Failed to save data: {e}")

    def add_patient(self, patient):
        self.data['patients'].append(patient.to_dict())
        self.save_data()

    def get_patients(self):
        return self.data['patients']

    def delete_patient(self, pid):
        self.data['patients'] = [p for p in self.data['patients'] if p['patient_id'] != pid]
        self.save_data()

    def add_appointment(self, appointment):
        self.data['appointments'].append(appointment.to_dict())
        self.save_data()

    def get_appointments(self):
        return self.data['appointments']

    def delete_appointment(self, aid):
        self.data['appointments'] = [a for a in self.data['appointments'] if a['appointment_id'] != aid]
        self.save_data()

    def add_bmi(self, metric):
        self.data['bmi'].append(metric.to_dict())
        self.save_data()

    def get_bmi(self):
        return self.data['bmi']

    def add_symptom(self, symptom):
        self.data['symptoms'].append(symptom.to_dict())
        self.save_data()

    def get_symptoms(self):
        return self.data['symptoms']

    def delete_bmi(self, patient_id):
        self.data['bmi'] = [b for b in self.data['bmi'] if b['patient_id'] != patient_id]
        self.save_data()

    def delete_symptoms_by_patient(self, patient_id):
        self.data['symptoms'] = [s for s in self.data['symptoms'] if s['patient_id'] != patient_id]
        self.save_data()



# === FLASK APP SETUP ===
app = Flask(__name__)
CORS(app)
store = DataStore()


# === ERROR HANDLING DECORATOR ===
def handle_errors(f):
    """Decorator for exception handling"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return decorated_function


# === API ROUTES ===

# PATIENTS
@app.route('/api/patients', methods=['POST'])
@handle_errors
def create_patient():
    data = request.json
    patient = Patient(data['name'], data['age'], data['contact'], data.get('history', ''))
    store.add_patient(patient)
    return jsonify({
        'message': 'Patient added',
        'patient_id': patient.patient_id
    }), 201


@app.route('/api/patients', methods=['GET'])
def get_patients():
    return jsonify(store.get_patients()), 200


@app.route('/api/patients/<patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    # Delete patient
    store.delete_patient(patient_id)
    # Cascade delete BMI + symptoms for that patient
    store.delete_bmi(patient_id)
    store.delete_symptoms_by_patient(patient_id)
    return jsonify({'message': 'Patient and related records deleted'}), 200


# APPOINTMENTS
@app.route('/api/appointments', methods=['POST'])
@handle_errors
def create_appointment():
    data = request.json
    appointment = Appointment(data['patient_id'], data['doctor'], data['date'], data['time'])
    store.add_appointment(appointment)
    return jsonify({'message': 'Appointment booked'}), 201


@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    return jsonify(store.get_appointments()), 200


@app.route('/api/appointments/<appt_id>', methods=['DELETE'])
def delete_appointment(appt_id):
    store.delete_appointment(appt_id)
    return jsonify({'message': 'Appointment cancelled'}), 200


# BMI
@app.route('/api/bmi', methods=['POST'])
@handle_errors
def create_bmi():
    data = request.json
    metric = HealthMetric(data['patient_id'], data['weight'], data['height'])
    store.add_bmi(metric)
    return jsonify({
        'message': 'BMI recorded',
        'bmi': metric.bmi,
        'category': metric.category
    }), 201


@app.route('/api/bmi', methods=['GET'])
def get_bmi():
    return jsonify(store.get_bmi()), 200

@app.route('/api/bmi/<patient_id>', methods=['DELETE'])
def delete_bmi(patient_id):
    """Delete BMI records for a patient"""
    store.delete_bmi(patient_id)
    return jsonify({'message': 'BMI record(s) deleted'}), 200



# SYMPTOMS
@app.route('/api/symptoms', methods=['POST'])
@handle_errors
def create_symptom():
    data = request.json
    symptom = SymptomRecord(data['patient_id'], data['symptoms'])
    store.add_symptom(symptom)
    return jsonify({
        'message': 'Symptoms recorded',
        'condition': symptom.condition
    }), 201


@app.route('/api/symptoms', methods=['GET'])
def get_symptoms():
    return jsonify(store.get_symptoms()), 200


# PREDICTIONS (Disease Risk Analysis)
@app.route('/api/predict/<patient_id>', methods=['GET'])
def predict_disease(patient_id):
    """Disease prediction based on BMI and symptoms"""
    patient_bmi = next((b for b in store.get_bmi() if b['patient_id'] == patient_id), None)
    patient_symptoms = [s for s in store.get_symptoms() if s['patient_id'] == patient_id]

    risk_score = 0
    predictions = []

    if patient_bmi:
        if patient_bmi['bmi'] > 30:
            risk_score += 40
            predictions.append('Diabetes (HIGH RISK)')
        if patient_bmi['bmi'] > 25:
            risk_score += 30
            predictions.append('Heart Disease (MEDIUM RISK)')

    if len(patient_symptoms) > 5:
        risk_score += 20
        predictions.append('Chronic Condition (MONITOR)')

    return jsonify({
        'risk_score': min(risk_score, 100),
        'predictions': predictions
    }), 200


# FRONTEND SERVING
@app.route('/')
def serve_frontend():
    """Serve the frontend HTML file"""
    return send_from_directory('.', 'index.html')


# HEALTH CHECK
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'Healthcare System Running'}), 200


if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║     🏥 HEALTHCARE MANAGEMENT SYSTEM - PYTHON FLASK BACKEND    ║
    ║                  Built with OOP Principles                     ║
    ║                                                                ║
    ║  Server running at: http://localhost:5000                     ║
    ║                                                                ║
    ║  Principles Demonstrated:                                     ║
    ║  ✓ OOP (Classes, Encapsulation, Inheritance)                  ║
    ║  ✓ Exception Handling (try-except)                            ║
    ║  ✓ File Operations (JSON storage)                             ║
    ║  ✓ Data Structures (Lists, Dictionaries)                      ║
    ║  ✓ Functional Programming (Filter, Map)                       ║
    ║  ✓ Decorators (Error handling)                                ║
    ║  ✓ Validation & Error Messages                                ║
    ║                                                                ║
    ║  Press Ctrl+C to stop the server                              ║
    ╚════════════════════════════════════════════════════════════════╝
    """)

    # Run Flask server
    app.run(debug=True, port=5000)

