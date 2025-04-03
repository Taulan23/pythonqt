from datetime import datetime, date
from enum import Enum, auto

class UserRole(Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    LAB_TECHNICIAN = "lab_technician"

class User:
    def __init__(self, id=None, username=None, role=None, full_name=None):
        self.id = id
        self.username = username
        self.role = role
        self.full_name = full_name
    
    @staticmethod
    def from_dict(data):
        if not data:
            return None
        return User(
            id=data.get('id'),
            username=data.get('username'),
            role=data.get('role'),
            full_name=data.get('full_name')
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'full_name': self.full_name
        }
    
    def is_admin(self):
        return self.role == UserRole.ADMIN.value
    
    def is_doctor(self):
        return self.role == UserRole.DOCTOR.value
    
    def is_lab_technician(self):
        return self.role == UserRole.LAB_TECHNICIAN.value

class Patient:
    def __init__(self, id=None, full_name=None, birth_date=None, gender=None, 
                 phone_number=None, email=None, address=None):
        self.id = id
        self.full_name = full_name
        self.birth_date = birth_date
        self.gender = gender
        self.phone_number = phone_number
        self.email = email
        self.address = address
    
    @staticmethod
    def from_tuple(data):
        if not data:
            return None
        return Patient(
            id=data[0],
            full_name=data[1],
            birth_date=data[2],
            gender=data[3],
            phone_number=data[4],
            email=data[5],
            address=data[6]
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'birth_date': self.birth_date,
            'gender': self.gender,
            'phone_number': self.phone_number,
            'email': self.email,
            'address': self.address
        }

class AnalysisType:
    def __init__(self, id=None, name=None, description=None):
        self.id = id
        self.name = name
        self.description = description
    
    @staticmethod
    def from_tuple(data):
        if not data:
            return None
        return AnalysisType(
            id=data[0],
            name=data[1],
            description=data[2]
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

class AnalysisParameter:
    def __init__(self, id=None, analysis_type_id=None, name=None, unit=None, 
                 normal_range_min=None, normal_range_max=None):
        self.id = id
        self.analysis_type_id = analysis_type_id
        self.name = name
        self.unit = unit
        self.normal_range_min = normal_range_min
        self.normal_range_max = normal_range_max
    
    @staticmethod
    def from_tuple(data):
        if not data:
            return None
        return AnalysisParameter(
            id=data[0],
            name=data[1],
            unit=data[2],
            normal_range_min=data[3],
            normal_range_max=data[4]
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'analysis_type_id': self.analysis_type_id,
            'name': self.name,
            'unit': self.unit,
            'normal_range_min': self.normal_range_min,
            'normal_range_max': self.normal_range_max
        }

class AnalysisStatus(Enum):
    NEW = "новый"
    PROCESSING = "в обработке"
    COMPLETED = "завершен"
    SENT = "отправлен"

class AnalysisResult:
    def __init__(self, id=None, patient_id=None, analysis_type_id=None, date_taken=None, 
                 lab_technician_id=None, status=AnalysisStatus.NEW.value):
        self.id = id
        self.patient_id = patient_id
        self.analysis_type_id = analysis_type_id
        self.date_taken = date_taken
        self.lab_technician_id = lab_technician_id
        self.status = status
        self.parameters = []  # Список значений параметров
    
    def add_parameter_value(self, parameter_id, value):
        self.parameters.append({
            'parameter_id': parameter_id,
            'value': value
        })
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'analysis_type_id': self.analysis_type_id,
            'date_taken': self.date_taken,
            'lab_technician_id': self.lab_technician_id,
            'status': self.status,
            'parameters': self.parameters
        }

class AppointmentStatus(Enum):
    SCHEDULED = "запланирован"
    COMPLETED = "завершен"
    CANCELLED = "отменен"

class Appointment:
    def __init__(self, id=None, patient_id=None, doctor_id=None, appointment_date=None, 
                 appointment_time=None, status=AppointmentStatus.SCHEDULED.value, notes=None):
        self.id = id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.appointment_date = appointment_date
        self.appointment_time = appointment_time
        self.status = status
        self.notes = notes
    
    @staticmethod
    def from_tuple(data):
        if not data:
            return None
        return Appointment(
            id=data[0],
            patient_id=data[1],
            doctor_id=data[3],
            appointment_date=data[5],
            appointment_time=data[6],
            status=data[7],
            notes=data[8]
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'appointment_date': self.appointment_date,
            'appointment_time': self.appointment_time,
            'status': self.status,
            'notes': self.notes
        } 