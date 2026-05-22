# app.py - Fixed Profile Management
import streamlit as st
import pandas as pd
import hashlib
import uuid
from datetime import datetime, date, timedelta
from PIL import Image
import re
import json
import io
import base64
from typing import Dict, List, Optional
import plotly.express as px
import plotly.graph_objects as go

# Configure page
st.set_page_config(
    page_title="Gombe SHSMB Locum Portal",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-badge {
        padding: 0.25rem 0.5rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
    }
    .status-submitted { background: #fbbf24; color: #78350f; }
    .status-verified { background: #10b981; color: white; }
    .status-rejected { background: #ef4444; color: white; }
    .status-shortlisted { background: #3b82f6; color: white; }
    .status-approved { background: #8b5cf6; color: white; }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        text-align: center;
    }
    .facility-badge {
        background: #e0e7ff;
        color: #3730a3;
        padding: 0.25rem 0.5rem;
        border-radius: 5px;
        font-size: 0.8rem;
        display: inline-block;
        margin: 0.1rem;
    }
    .stButton button {
        width: 100%;
    }
    .facility-card {
        background: white;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        border-left: 4px solid #2a5298;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .vacancy-count {
        background: #10b981;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 20px;
        font-size: 0.75rem;
        display: inline-block;
        margin-left: 0.5rem;
    }
    .warning-box {
        background: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Gombe State Facilities Data
GOMBE_FACILITIES = {
    "fac_001": {
        "name": "Gombe State Specialist Hospital Gombe",
        "facility_code": "GSSH001",
        "type": "Specialist Hospital",
        "lga": "Gombe",
        "address": "Along Bauchi Road, Gombe, Gombe State",
        "is_active": True,
        "departments": ["Obstetrics & Gynaecology", "Paediatrics", "General Surgery", "Internal Medicine", 
                       "Radiology", "Laboratory Services", "Pharmacy", "Emergency Medicine"]
    },
    "fac_002": {
        "name": "Zainab Bulkashuwa Women and Children Hospital Gombe",
        "facility_code": "ZBWCH002",
        "type": "Specialist Hospital",
        "lga": "Gombe",
        "address": "Gombe, Gombe State",
        "is_active": True,
        "departments": ["Obstetrics", "Gynaecology", "Paediatrics", "Neonatology", "Family Planning", "Nutrition"]
    },
    "fac_003": {
        "name": "General Hospital Bajoga",
        "facility_code": "GHB003",
        "type": "General Hospital",
        "lga": "Funakaye",
        "address": "Bajoga Town, Funakaye LGA, Gombe State",
        "is_active": True,
        "departments": ["General Medicine", "Surgery", "Paediatrics", "Obstetrics", "Outpatient"]
    },
    "fac_004": {
        "name": "Cottage Hospital Malamsidi",
        "facility_code": "CHM004",
        "type": "Cottage Hospital",
        "lga": "Akko",
        "address": "Malamsidi, Akko LGA, Gombe State",
        "is_active": True,
        "departments": ["Primary Care", "Maternity", "Immunization", "Outpatient"]
    },
    "fac_005": {
        "name": "General Hospital Nafada",
        "facility_code": "GHN005",
        "type": "General Hospital",
        "lga": "Nafada",
        "address": "Nafada Town, Nafada LGA, Gombe State",
        "is_active": True,
        "departments": ["General Medicine", "Surgery", "Paediatrics", "Obstetrics", "Laboratory"]
    },
    "fac_006": {
        "name": "General Hospital Dukku",
        "facility_code": "GHD006",
        "type": "General Hospital",
        "lga": "Dukku",
        "address": "Dukku Town, Dukku LGA, Gombe State",
        "is_active": True,
        "departments": ["General Medicine", "Surgery", "Paediatrics", "Maternity", "Emergency"]
    },
    "fac_007": {
        "name": "Cottage Hospital Bojude",
        "facility_code": "CHB007",
        "type": "Cottage Hospital",
        "lga": "Kwami",
        "address": "Bojude, Kwami LGA, Gombe State",
        "is_active": True,
        "departments": ["Primary Care", "Maternity", "Immunization", "Pharmacy"]
    },
    "fac_008": {
        "name": "General Hospital Deba",
        "facility_code": "GHD008",
        "type": "General Hospital",
        "lga": "Deba",
        "address": "Deba Town, Deba LGA, Gombe State",
        "is_active": True,
        "departments": ["General Medicine", "Surgery", "Paediatrics", "Obstetrics", "Laboratory"]
    },
    "fac_009": {
        "name": "Infectious Disease Hospital Zambuk",
        "facility_code": "IDHZ009",
        "type": "Specialist Hospital",
        "lga": "Yamaltu/Deba",
        "address": "Zambuk, Yamaltu/Deba LGA, Gombe State",
        "is_active": True,
        "departments": ["Infectious Diseases", "Isolation Unit", "Laboratory", "Public Health", "Epidemiology"]
    },
    "fac_010": {
        "name": "General Hospital Talasse",
        "facility_code": "GHT010",
        "type": "General Hospital",
        "lga": "Balanga",
        "address": "Talasse Town, Balanga LGA, Gombe State",
        "is_active": True,
        "departments": ["General Medicine", "Surgery", "Paediatrics", "Maternity", "Outpatient"]
    },
    "fac_011": {
        "name": "Cottage Hospital Putoki",
        "facility_code": "CHP011",
        "type": "Cottage Hospital",
        "lga": "Balanga",
        "address": "Putoki, Balanga LGA, Gombe State",
        "is_active": True,
        "departments": ["Primary Care", "Maternity", "Immunization", "Community Health"]
    },
    "fac_012": {
        "name": "Cottage Hospital Bambam",
        "facility_code": "CHB012",
        "type": "Cottage Hospital",
        "lga": "Balanga",
        "address": "Bambam, Balanga LGA, Gombe State",
        "is_active": True,
        "departments": ["Primary Care", "Maternity", "Immunization", "Health Education"]
    },
    "fac_013": {
        "name": "Cottage Hospital Tula",
        "facility_code": "CHT013",
        "type": "Cottage Hospital",
        "lga": "Kaltungo",
        "address": "Tula, Kaltungo LGA, Gombe State",
        "is_active": True,
        "departments": ["Primary Care", "Maternity", "Immunization", "Outpatient"]
    },
    "fac_014": {
        "name": "General Hospital Kaltungo",
        "facility_code": "GHK014",
        "type": "General Hospital",
        "lga": "Kaltungo",
        "address": "Kaltungo Town, Kaltungo LGA, Gombe State",
        "is_active": True,
        "departments": ["General Medicine", "Surgery", "Paediatrics", "Obstetrics", "Laboratory", "Radiology"]
    },
    "fac_015": {
        "name": "Cottage Hospital Filiya",
        "facility_code": "CHF015",
        "type": "Cottage Hospital",
        "lga": "Shongom",
        "address": "Filiya, Shongom LGA, Gombe State",
        "is_active": True,
        "departments": ["Primary Care", "Maternity", "Immunization", "Community Health"]
    },
    "fac_016": {
        "name": "General Hospital Billiri",
        "facility_code": "GHB016",
        "type": "General Hospital",
        "lga": "Billiri",
        "address": "Billiri Town, Billiri LGA, Gombe State",
        "is_active": True,
        "departments": ["General Medicine", "Surgery", "Paediatrics", "Obstetrics", "Laboratory"]
    },
    "fac_017": {
        "name": "General Hospital Kumo",
        "facility_code": "GHK017",
        "type": "General Hospital",
        "lga": "Akko",
        "address": "Kumo Town, Akko LGA, Gombe State",
        "is_active": True,
        "departments": ["General Medicine", "Surgery", "Paediatrics", "Obstetrics", "Emergency", "Laboratory"]
    },
    "fac_018": {
        "name": "Snakebite Hospital Kaltungo",
        "facility_code": "SHK018",
        "type": "Specialist Hospital",
        "lga": "Kaltungo",
        "address": "Kaltungo Town, Kaltungo LGA, Gombe State",
        "is_active": True,
        "departments": ["Emergency Medicine", "Toxicology", "Internal Medicine", "Intensive Care", "Antivenom Unit"]
    },
    "fac_019": {
        "name": "Cottage Hospital Tumu",
        "facility_code": "CHT019",
        "type": "Cottage Hospital",
        "lga": "Akko",
        "address": "Tumu, Akko LGA, Gombe State",
        "is_active": True,
        "departments": ["Primary Care", "Maternity", "Immunization", "Outpatient"]
    },
    "fac_020": {
        "name": "Cottage Hospital Pindiga",
        "facility_code": "CHP020",
        "type": "Cottage Hospital",
        "lga": "Akko",
        "address": "Pindiga, Akko LGA, Gombe State",
        "is_active": True,
        "departments": ["Primary Care", "Maternity", "Immunization", "Community Health"]
    },
    "fac_021": {
        "name": "General Hospital Kashere",
        "facility_code": "GHK021",
        "type": "General Hospital",
        "lga": "Akko",
        "address": "Kashere, Akko LGA, Gombe State",
        "is_active": True,
        "departments": ["General Medicine", "Surgery", "Paediatrics", "Obstetrics", "Outpatient"]
    }
}

# LGAs in Gombe State
GOMBE_LGAS = ["Gombe", "Funakaye", "Akko", "Nafada", "Dukku", "Kwami", "Deba", 
              "Yamaltu/Deba", "Balanga", "Kaltungo", "Shongom", "Billiri"]

# Medical Specialties
MEDICAL_SPECIALTIES = [
    "General Medicine", "Family Medicine", "Internal Medicine", 
    "Paediatrics", "Obstetrics & Gynaecology", "General Surgery", 
    "Orthopaedics", "Ophthalmology", "Otorhinolaryngology (ENT)",
    "Radiology", "Pathology", "Anaesthesiology", "Psychiatry",
    "Emergency Medicine", "Public Health", "Community Medicine",
    "Dermatology", "Cardiology", "Neurology", "Nephrology",
    "Infectious Diseases", "Toxicology"
]

# Initialize session state
def init_session_state():
    """Initialize all session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'profile_updated' not in st.session_state:
        st.session_state.profile_updated = False
    
    # Data stores (simulating database)
    if 'users' not in st.session_state:
        # Preload demo data
        st.session_state.users = {
            "admin@shsmb.gov.ng": {
                "password": hashlib.sha256("admin123".encode()).hexdigest(),
                "role": "system_admin",
                "name": "System Administrator",
                "created_at": datetime.now()
            },
            "hr@shsmb.gov.ng": {
                "password": hashlib.sha256("hr123".encode()).hexdigest(),
                "role": "hr_reviewer",
                "name": "HR Officer",
                "created_at": datetime.now()
            },
            "manager@specialist.gov.ng": {
                "password": hashlib.sha256("manager123".encode()).hexdigest(),
                "role": "hospital_manager",
                "name": "Dr. Musa Ibrahim",
                "facility_id": "fac_001",
                "created_at": datetime.now()
            },
            "doctor@example.com": {
                "password": hashlib.sha256("doctor123".encode()).hexdigest(),
                "role": "applicant",
                "name": "Dr. Amina Bello",
                "created_at": datetime.now()
            }
        }
    
    if 'applicants' not in st.session_state:
        # Initialize with some default data for demo doctor
        st.session_state.applicants = {
            "doctor@example.com": {
                "name": "Dr. Amina Bello",
                "email": "doctor@example.com",
                "phone": "08012345678",
                "mdcn_number": "MDCN123456",
                "date_of_birth": date(1985, 6, 15),
                "gender": "Female",
                "state_of_origin": "Gombe",
                "license_number": "MDCN/2024/12345",
                "license_expiry": date(2025, 12, 31),
                "specialization": "General Medicine",
                "years_experience": 8,
                "profile_completion": 85,
                "created_at": datetime.now()
            }
        }
    
    if 'facilities' not in st.session_state:
        st.session_state.facilities = GOMBE_FACILITIES
    
    if 'vacancies' not in st.session_state:
        # Create vacancies for ALL facilities (same as before)
        st.session_state.vacancies = {}
        
        vacancy_data = [
            ("fac_001", "Obstetrics & Gynaecology", "Locum Consultant Obstetrician", "Obstetrics & Gynaecology", 5, 3, 3, "Seeking experienced consultant", "Fellowship in ObGyn, MDCN license"),
            ("fac_001", "Paediatrics", "Locum Paediatrician", "Paediatrics", 3, 4, 6, "Paediatrician needed", "MDCN license, residency in Paediatrics"),
            ("fac_002", "Obstetrics", "Locum Medical Officer", "Obstetrics & Gynaecology", 2, 5, 4, "Medical officers needed", "MDCN license, maternal health experience"),
            ("fac_003", "General Medicine", "Locum Medical Officer", "General Medicine", 2, 4, 3, "General medical officer", "MDCN license, NYSC completion"),
            ("fac_014", "General Medicine", "Locum Medical Officer", "General Medicine", 2, 4, 3, "Medical officer needed", "MDCN license"),
            ("fac_018", "Emergency Medicine", "Locum Emergency Physician", "Emergency Medicine", 3, 3, 3, "Emergency physician needed", "Emergency experience"),
        ]
        
        for i, data in enumerate(vacancy_data, 1):
            vac_id = f"vac_{i:03d}"
            st.session_state.vacancies[vac_id] = {
                "facility_id": data[0],
                "department": data[1],
                "job_title": data[2],
                "specialty": data[3],
                "min_experience": data[4],
                "slots": data[5],
                "duration_months": data[6],
                "description": data[7],
                "requirements": data[8],
                "closing_date": date(2025, 7, 30),
                "status": "published",
                "created_at": datetime.now()
            }
    
    if 'applications' not in st.session_state:
        st.session_state.applications = {}
    
    if 'documents' not in st.session_state:
        st.session_state.documents = {}
    
    if 'notifications' not in st.session_state:
        st.session_state.notifications = []

# Helper functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

def generate_id(prefix=""):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def send_notification(user_email, title, message, notification_type="system"):
    st.session_state.notifications.append({
        "user_email": user_email,
        "title": title,
        "message": message,
        "type": notification_type,
        "created_at": datetime.now(),
        "is_read": False
    })

def get_notifications(user_email):
    return [n for n in st.session_state.notifications if n["user_email"] == user_email]

def calculate_profile_completion(applicant_data):
    """Calculate profile completion percentage"""
    required_fields = [
        'name', 'phone', 'mdcn_number', 'date_of_birth', 
        'gender', 'state_of_origin', 'specialization', 'years_experience'
    ]
    
    filled = 0
    for field in required_fields:
        if applicant_data.get(field):
            filled += 1
    
    # Check if license info is complete
    if applicant_data.get('license_number') and applicant_data.get('license_expiry'):
        filled += 1
    
    total = len(required_fields) + 1
    percentage = int((filled / total) * 100)
    
    # Update the profile_completion field
    applicant_data['profile_completion'] = percentage
    
    return percentage

# Authentication UI
def login_page():
    st.markdown("""
    <div class="main-header">
        <h1>🏥 Gombe State Hospital Service Management Board</h1>
        <h2>Locum Application Portal</h2>
        <p>Connecting qualified doctors with locum opportunities across 21 healthcare facilities in Gombe State</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Login to Your Account")
        
        email = st.text_input("Email Address", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("Login", type="primary", use_container_width=True):
                if email in st.session_state.users:
                    stored_user = st.session_state.users[email]
                    if verify_password(password, stored_user["password"]):
                        st.session_state.authenticated = True
                        st.session_state.user = email
                        st.session_state.role = stored_user["role"]
                        st.session_state.user_name = stored_user["name"]
                        if "facility_id" in stored_user:
                            st.session_state.user_facility = stored_user["facility_id"]
                        st.rerun()
                    else:
                        st.error("Invalid password")
                else:
                    st.error("User not found")
        
        with col_btn2:
            if st.button("Create Account", use_container_width=True):
                st.session_state.show_registration = True
                st.rerun()
        
        st.markdown("---")
        st.markdown("""
        **Demo Accounts:**
        - Doctor: doctor@example.com / doctor123
        - Hospital Manager: manager@specialist.gov.ng / manager123
        - HR Officer: hr@shsmb.gov.ng / hr123
        - Admin: admin@shsmb.gov.ng / admin123
        """)

def registration_page():
    st.markdown("### 📝 Create New Account")
    
    with st.form("registration_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        phone = st.text_input("Phone Number")
        mdcn_number = st.text_input("MDCN Registration Number")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        role = st.selectbox("Account Type", ["applicant", "hospital_manager"])
        
        if role == "hospital_manager":
            facility = st.selectbox("Assigned Facility", 
                                   [f["name"] for f in st.session_state.facilities.values()])
        
        submitted = st.form_submit_button("Register")
        
        if submitted:
            if not all([name, email, phone, mdcn_number, password]):
                st.error("Please fill all required fields")
            elif password != confirm_password:
                st.error("Passwords do not match")
            elif email in st.session_state.users:
                st.error("Email already registered")
            else:
                user_data = {
                    "password": hash_password(password),
                    "role": role,
                    "name": name,
                    "phone": phone,
                    "mdcn_number": mdcn_number,
                    "created_at": datetime.now()
                }
                
                if role == "hospital_manager":
                    facility_id = None
                    for fid, f in st.session_state.facilities.items():
                        if f["name"] == facility:
                            facility_id = fid
                            break
                    user_data["facility_id"] = facility_id
                
                st.session_state.users[email] = user_data
                
                # Create applicant profile if doctor
                if role == "applicant":
                    st.session_state.applicants[email] = {
                        "name": name,
                        "email": email,
                        "phone": phone,
                        "mdcn_number": mdcn_number,
                        "profile_completion": 30,
                        "created_at": datetime.now()
                    }
                
                st.success("Registration successful! Please login.")
                st.session_state.show_registration = False
                st.rerun()
    
    if st.button("Back to Login"):
        st.session_state.show_registration = False
        st.rerun()

# Profile Management Function
def profile_management(applicant_data):
    """Handle profile management with proper saving"""
    st.markdown("### 👤 Edit Your Profile")
    st.markdown("Please complete all required fields to increase your profile completion score.")
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name *", value=applicant_data.get("name", ""))
            phone = st.text_input("Phone Number *", value=applicant_data.get("phone", ""))
            date_of_birth = st.date_input("Date of Birth *", 
                                         value=applicant_data.get("date_of_birth", date(1980, 1, 1)))
            gender = st.selectbox("Gender *", 
                                 ["Male", "Female", "Other"],
                                 index=["Male", "Female", "Other"].index(applicant_data.get("gender", "Male")) if applicant_data.get("gender") in ["Male", "Female", "Other"] else 0)
            state_of_origin = st.selectbox("State of Origin *", 
                                          ["Gombe", "Adamawa", "Bauchi", "Borno", "Yobe", "Taraba", "Other"],
                                          index=0)
        
        with col2:
            mdcn_number = st.text_input("MDCN Number *", value=applicant_data.get("mdcn_number", ""))
            license_number = st.text_input("Annual Practicing License Number *", 
                                          value=applicant_data.get("license_number", ""))
            license_expiry = st.date_input("License Expiry Date *", 
                                          value=applicant_data.get("license_expiry", date(2025, 12, 31)))
            specialization = st.selectbox("Specialization *", MEDICAL_SPECIALTIES,
                                         index=MEDICAL_SPECIALTIES.index(applicant_data.get("specialization", "General Medicine")) if applicant_data.get("specialization") in MEDICAL_SPECIALTIES else 0)
            years_experience = st.number_input("Years of Experience *", 
                                              min_value=0, max_value=50, 
                                              value=applicant_data.get("years_experience", 0))
        
        st.markdown("---")
        st.markdown("*Required fields")
        
        submitted = st.form_submit_button("💾 Save Profile", use_container_width=True)
        
        if submitted:
            # Validate required fields
            if not all([name, phone, mdcn_number, license_number, specialization]):
                st.error("Please fill all required fields marked with *")
            else:
                # Update applicant data
                applicant_data.update({
                    "name": name,
                    "phone": phone,
                    "date_of_birth": date_of_birth,
                    "gender": gender,
                    "state_of_origin": state_of_origin,
                    "mdcn_number": mdcn_number,
                    "license_number": license_number,
                    "license_expiry": license_expiry,
                    "specialization": specialization,
                    "years_experience": years_experience,
                    "updated_at": datetime.now()
                })
                
                # Recalculate profile completion
                completion = calculate_profile_completion(applicant_data)
                applicant_data["profile_completion"] = completion
                
                # Save back to session state
                st.session_state.applicants[st.session_state.user] = applicant_data
                
                st.success(f"✅ Profile updated successfully! Completion: {completion}%")
                st.balloons()
                st.rerun()

# Dashboard Components
def applicant_dashboard():
    st.markdown(f"## Welcome, {st.session_state.user_name}")
    
    # Get applicant data
    applicant_data = st.session_state.applicants.get(st.session_state.user, {})
    
    # Calculate and display profile completion
    if applicant_data:
        completion = calculate_profile_completion(applicant_data)
    else:
        completion = 0
    
    # Show warning if profile is incomplete
    if completion < 80:
        st.markdown(f"""
        <div class="warning-box">
            ⚠️ <strong>Profile Incomplete: {completion}%</strong><br>
            Please complete your profile to apply for vacancies. You need at least 80% completion to submit applications.
        </div>
        """, unsafe_allow_html=True)
    
    # Display progress bar
    st.progress(completion / 100, text=f"Profile Completion: {completion}%")
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/150x150?text=Doctor", use_container_width=True)
        st.markdown(f"### Dr. {applicant_data.get('name', st.session_state.user_name)}")
        st.markdown(f"📧 {st.session_state.user}")
        st.markdown(f"📱 {applicant_data.get('phone', 'Not provided')}")
        st.markdown(f"🆔 MDCN: {applicant_data.get('mdcn_number', 'Not provided')}")
        st.markdown(f"📊 Profile: {completion}% complete")
        
        st.markdown("---")
        menu = st.radio(
            "Navigation",
            ["Dashboard", "My Profile", "Browse Vacancies", "My Applications", "Documents", "Notifications", "Facilities Map"]
        )
    
    if menu == "Dashboard":
        # Statistics
        col1, col2, col3, col4 = st.columns(4)
        
        my_apps = [app for app in st.session_state.applications.values() 
                   if app.get("applicant_email") == st.session_state.user]
        
        with col1:
            st.metric("Total Applications", len(my_apps))
        with col2:
            active = len([a for a in my_apps if a.get("status") in ["submitted", "under_review", "shortlisted"]])
            st.metric("Active Applications", active)
        with col3:
            shortlisted = len([a for a in my_apps if a.get("status") == "shortlisted"])
            st.metric("Shortlisted", shortlisted)
        with col4:
            approved = len([a for a in my_apps if a.get("status") == "approved"])
            st.metric("Approved", approved)
        
        # Profile completion checklist
        st.markdown("### ✅ Profile Completion Checklist")
        
        checklist_items = {
            "Full Name": applicant_data.get("name"),
            "Phone Number": applicant_data.get("phone"),
            "MDCN Number": applicant_data.get("mdcn_number"),
            "License Number": applicant_data.get("license_number"),
            "License Expiry": applicant_data.get("license_expiry"),
            "Specialization": applicant_data.get("specialization"),
            "Years of Experience": applicant_data.get("years_experience") is not None,
            "Date of Birth": applicant_data.get("date_of_birth"),
            "Gender": applicant_data.get("gender"),
            "State of Origin": applicant_data.get("state_of_origin")
        }
        
        col1, col2 = st.columns(2)
        for i, (item, completed) in enumerate(checklist_items.items()):
            with col1 if i % 2 == 0 else col2:
                if completed:
                    st.markdown(f"✅ {item}")
                else:
                    st.markdown(f"❌ {item}")
        
        if completion < 80:
            st.info("👆 Click on 'My Profile' in the sidebar to complete your profile.")
        
        # Recent vacancies
        st.markdown("### 📢 Current Locum Opportunities")
        vacancies_df = []
        for vac_id, vac in st.session_state.vacancies.items():
            if vac["status"] == "published":
                facility = st.session_state.facilities.get(vac["facility_id"], {})
                if facility:
                    vacancies_df.append({
                        "Facility": facility.get("name", "Unknown"),
                        "Type": facility.get("type", "Unknown"),
                        "LGA": facility.get("lga", "Unknown"),
                        "Position": vac["job_title"],
                        "Slots": vac["slots"],
                        "Closing Date": vac["closing_date"].strftime("%d %b, %Y")
                    })
        
        if vacancies_df:
            df = pd.DataFrame(vacancies_df)
            st.dataframe(df, use_container_width=True, hide_index=True)
    
    elif menu == "My Profile":
        profile_management(applicant_data)
    
    elif menu == "Browse Vacancies":
        st.markdown("### 🔍 Browse Locum Vacancies")
        
        if completion < 80:
            st.warning(f"⚠️ Your profile is only {completion}% complete. Please complete your profile to at least 80% before applying for vacancies.")
        
        st.markdown(f"**Total Available Vacancies:** {len(st.session_state.vacancies)}")
        
        # Filters
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            facility_filter = st.multiselect("Facility", 
                                            [f["name"] for f in st.session_state.facilities.values()])
        with col2:
            lga_filter = st.multiselect("LGA", GOMBE_LGAS)
        with col3:
            specialty_filter = st.multiselect("Specialty", MEDICAL_SPECIALTIES)
        with col4:
            facility_type_filter = st.multiselect("Facility Type", 
                                                 ["Specialist Hospital", "General Hospital", "Cottage Hospital"])
        
        # Display vacancies
        vacancy_found = False
        for vac_id, vac in st.session_state.vacancies.items():
            if vac["status"] != "published":
                continue
            
            facility = st.session_state.facilities.get(vac["facility_id"], {})
            if not facility:
                continue
            
            # Apply filters
            if facility_filter and facility.get("name") not in facility_filter:
                continue
            if lga_filter and facility.get("lga") not in lga_filter:
                continue
            if facility_type_filter and facility.get("type") not in facility_type_filter:
                continue
            if specialty_filter and vac["specialty"] not in specialty_filter:
                continue
            
            vacancy_found = True
            
            with st.expander(f"🏥 {facility.get('name', 'Unknown')} - {vac['job_title']}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Facility Type:** {facility.get('type', 'Unknown')}")
                    st.markdown(f"**LGA:** {facility.get('lga', 'Unknown')}")
                    st.markdown(f"**Department:** {vac['department']}")
                    st.markdown(f"**Specialty Required:** {vac['specialty']}")
                    st.markdown(f"**Slots Available:** {vac['slots']}")
                    st.markdown(f"**Duration:** {vac['duration_months']} months")
                    st.markdown(f"**Minimum Experience:** {vac['min_experience']} years")
                    st.markdown(f"**Closing Date:** {vac['closing_date'].strftime('%d %B, %Y')}")
                    st.markdown(f"**Description:** {vac['description']}")
                    st.markdown(f"**Requirements:** {vac['requirements']}")
                
                with col2:
                    st.markdown("### ")
                    apply_disabled = completion < 80
                    button_text = "Apply Now" if not apply_disabled else "Complete Profile First"
                    
                    if st.button(button_text, key=f"apply_{vac_id}", disabled=apply_disabled):
                        if completion >= 80:
                            # Check if already applied
                            existing = [app for app in st.session_state.applications.values() 
                                       if app.get("applicant_email") == st.session_state.user 
                                       and app.get("vacancy_id") == vac_id]
                            
                            if existing:
                                st.warning("You have already applied for this position")
                            else:
                                # Create application
                                app_id = generate_id("APP")
                                st.session_state.applications[app_id] = {
                                    "application_id": app_id,
                                    "applicant_email": st.session_state.user,
                                    "vacancy_id": vac_id,
                                    "status": "submitted",
                                    "submitted_at": datetime.now(),
                                    "screening_score": None
                                }
                                
                                send_notification(
                                    st.session_state.user,
                                    "Application Submitted",
                                    f"Your application for {vac['job_title']} at {facility.get('name')} has been submitted.",
                                    "application_update"
                                )
                                
                                st.success("Application submitted successfully!")
                                st.rerun()
        
        if not vacancy_found:
            st.info("No vacancies match your filters. Try adjusting your search criteria.")
    
    elif menu == "My Applications":
        st.markdown("### 📋 My Applications")
        
        my_apps = [app for app in st.session_state.applications.values() 
                   if app.get("applicant_email") == st.session_state.user]
        
        if my_apps:
            for app in my_apps:
                vacancy = st.session_state.vacancies.get(app["vacancy_id"], {})
                facility = st.session_state.facilities.get(vacancy.get("facility_id"), {})
                
                status_colors = {
                    "submitted": "🔵 Submitted",
                    "under_review": "🟡 Under Review",
                    "shortlisted": "🟢 Shortlisted",
                    "rejected": "🔴 Rejected",
                    "approved": "🟣 Approved",
                    "interview_scheduled": "📅 Interview Scheduled"
                }
                
                st.markdown(f"""
                <div style="border:1px solid #ddd; padding:1rem; margin:0.5rem 0; border-radius:10px">
                    <h4>{vacancy.get('job_title', 'Unknown')}</h4>
                    <p><strong>Facility:</strong> {facility.get('name', 'Unknown')} ({facility.get('type', 'Unknown')})</p>
                    <p><strong>LGA:</strong> {facility.get('lga', 'Unknown')}</p>
                    <p><strong>Status:</strong> <span class="status-badge">{status_colors.get(app['status'], app['status'])}</span></p>
                    <p><strong>Submitted:</strong> {app['submitted_at'].strftime('%d %B, %Y %H:%M')}</p>
                    <p><strong>Application ID:</strong> {app['application_id']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("You haven't submitted any applications yet")
    
    elif menu == "Facilities Map":
        st.markdown("### 🗺️ Healthcare Facilities in Gombe State")
        
        # Display facilities by LGA
        facilities_by_lga = {}
        for fac in st.session_state.facilities.values():
            lga = fac["lga"]
            if lga not in facilities_by_lga:
                facilities_by_lga[lga] = []
            facilities_by_lga[lga].append(fac)
        
        for lga in sorted(facilities_by_lga.keys()):
            with st.expander(f"📍 {lga} LGA ({len(facilities_by_lga[lga])} facilities)"):
                for fac in facilities_by_lga[lga]:
                    st.markdown(f"""
                    <div class="facility-card">
                        <strong>🏥 {fac['name']}</strong><br>
                        <span class="facility-badge">{fac['type']}</span>
                        <span class="facility-badge">Code: {fac['facility_code']}</span><br>
                        📍 {fac['address']}
                    </div>
                    """, unsafe_allow_html=True)
    
    elif menu == "Documents":
        st.markdown("### 📄 Document Management")
        
        doc_types = [
            "CV/Resume", "MDCN Certificate", "Annual Practicing License", 
            "Medical Degree", "Internship Certificate", "NYSC Certificate",
            "Specialist Certificate", "Passport Photo", "Government ID"
        ]
        
        for doc_type in doc_types:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{doc_type}**")
            with col2:
                uploaded = st.file_uploader(f"Upload {doc_type}", type=['pdf', 'jpg', 'png'], 
                                           key=f"doc_{doc_type}", label_visibility="collapsed")
                if uploaded:
                    doc_id = generate_id("DOC")
                    st.session_state.documents[doc_id] = {
                        "applicant_email": st.session_state.user,
                        "type": doc_type,
                        "filename": uploaded.name,
                        "uploaded_at": datetime.now(),
                        "status": "uploaded"
                    }
                    st.success(f"{doc_type} uploaded successfully!")
        
        # Show uploaded documents
        st.markdown("### 📎 Uploaded Documents")
        my_docs = [doc for doc in st.session_state.documents.values() 
                  if doc.get("applicant_email") == st.session_state.user]
        
        if my_docs:
            df_docs = pd.DataFrame(my_docs)
            st.dataframe(df_docs[["type", "filename", "uploaded_at"]], use_container_width=True)
        else:
            st.info("No documents uploaded yet")
    
    elif menu == "Notifications":
        st.markdown("### 🔔 Notifications")
        
        notifications = get_notifications(st.session_state.user)
        
        if notifications:
            for notif in reversed(notifications):
                icon = "📧" if notif["type"] == "application_update" else "⚠️" if notif["type"] == "verification_alert" else "ℹ️"
                st.info(f"{icon} **{notif['title']}**\n\n{notif['message']}\n\n*{notif['created_at'].strftime('%d %B, %Y %H:%M')}*")
        else:
            st.info("No notifications")

def hospital_manager_dashboard():
    st.markdown(f"## Welcome, {st.session_state.user_name}")
    
    # Get manager's facility
    manager_facility_id = st.session_state.users[st.session_state.user].get("facility_id")
    manager_facility = st.session_state.facilities.get(manager_facility_id, {})
    
    with st.sidebar:
        st.markdown(f"### 🏥 {manager_facility.get('name', 'Unknown Facility')}")
        st.markdown(f"**Type:** {manager_facility.get('type', 'N/A')}")
        st.markdown(f"**LGA:** {manager_facility.get('lga', 'N/A')}")
        st.markdown(f"📧 {st.session_state.user}")
        
        menu = st.radio("Navigation", ["Dashboard", "Review Applications"])
    
    if menu == "Dashboard":
        facility_vacancies = [v for v in st.session_state.vacancies.values() 
                             if v.get("facility_id") == manager_facility_id]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Active Vacancies", len([v for v in facility_vacancies if v["status"] == "published"]))
        with col2:
            total_apps = len([app for app in st.session_state.applications.values() 
                             if app.get("vacancy_id") in [v_id for v_id, v in st.session_state.vacancies.items() 
                                                         if v.get("facility_id") == manager_facility_id]])
            st.metric("Total Applications", total_apps)
        with col3:
            pending_review = len([app for app in st.session_state.applications.values() 
                                 if app.get("status") in ["submitted", "under_review"]])
            st.metric("Pending Review", pending_review)
    
    elif menu == "Review Applications":
        st.markdown("### 👥 Applications Pending Review")
        
        facility_vacancies = [vid for vid, v in st.session_state.vacancies.items() 
                             if v.get("facility_id") == manager_facility_id]
        
        pending_apps = [app for app in st.session_state.applications.values() 
                       if app.get("vacancy_id") in facility_vacancies 
                       and app.get("status") in ["submitted", "under_review"]]
        
        if pending_apps:
            for app in pending_apps:
                vacancy = st.session_state.vacancies.get(app["vacancy_id"], {})
                applicant = st.session_state.applicants.get(app["applicant_email"], {})
                
                with st.expander(f"📋 {applicant.get('name', 'Unknown')} - {vacancy.get('job_title', 'Unknown')}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**Email:** {app['applicant_email']}")
                        st.markdown(f"**MDCN:** {applicant.get('mdcn_number', 'N/A')}")
                        st.markdown(f"**Experience:** {applicant.get('years_experience', 'N/A')} years")
                        st.markdown(f"**Submitted:** {app['submitted_at'].strftime('%d %B, %Y')}")
                    
                    with col2:
                        action = st.selectbox("Action", ["Select Action", "Shortlist", "Reject"], 
                                             key=f"action_{app['application_id']}")
                        
                        if st.button("Submit", key=f"submit_{app['application_id']}"):
                            if action == "Shortlist":
                                app["status"] = "shortlisted"
                                send_notification(
                                    app["applicant_email"],
                                    "Application Shortlisted",
                                    f"Your application for {vacancy.get('job_title')} has been shortlisted!",
                                    "application_update"
                                )
                                st.success("Applicant shortlisted!")
                            elif action == "Reject":
                                app["status"] = "rejected"
                                send_notification(
                                    app["applicant_email"],
                                    "Application Update",
                                    f"Your application for {vacancy.get('job_title')} has been reviewed.",
                                    "application_update"
                                )
                                st.success("Application rejected")
                            
                            st.rerun()
        else:
            st.info("No pending applications to review")

def hr_dashboard():
    st.markdown(f"## Welcome, {st.session_state.user_name}")
    
    with st.sidebar:
        menu = st.radio("Navigation", ["Dashboard", "All Applications"])
    
    if menu == "Dashboard":
        col1, col2, col3, col4 = st.columns(4)
        
        total_apps = len(st.session_state.applications)
        total_vacancies = len(st.session_state.vacancies)
        total_applicants = len(st.session_state.applicants)
        
        with col1:
            st.metric("Total Applications", total_apps)
        with col2:
            st.metric("Active Vacancies", total_vacancies)
        with col3:
            st.metric("Registered Doctors", total_applicants)
        with col4:
            pending_verification = len([doc for doc in st.session_state.documents.values() 
                                       if doc.get("status") == "uploaded"])
            st.metric("Pending Verification", pending_verification)
    
    elif menu == "All Applications":
        st.markdown("### 📋 All Applications")
        
        if st.session_state.applications:
            apps_list = []
            for app_id, app in st.session_state.applications.items():
                vacancy = st.session_state.vacancies.get(app["vacancy_id"], {})
                facility = st.session_state.facilities.get(vacancy.get("facility_id"), {})
                applicant = st.session_state.applicants.get(app["applicant_email"], {})
                
                apps_list.append({
                    "Application ID": app_id[:8],
                    "Applicant": applicant.get("name", "Unknown"),
                    "Position": vacancy.get("job_title", "Unknown"),
                    "Facility": facility.get("name", "Unknown"),
                    "Status": app.get("status", "unknown"),
                    "Submitted": app.get("submitted_at", datetime.now()).strftime("%Y-%m-%d")
                })
            
            df = pd.DataFrame(apps_list)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No applications yet")

def admin_dashboard():
    st.markdown(f"## System Administration - {st.session_state.user_name}")
    
    with st.sidebar:
        menu = st.radio("Navigation", ["System Overview", "User Management"])
    
    if menu == "System Overview":
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Users", len(st.session_state.users))
        with col2:
            st.metric("Total Facilities", len(st.session_state.facilities))
        with col3:
            st.metric("Active Vacancies", len(st.session_state.vacancies))
        with col4:
            st.metric("Total Applications", len(st.session_state.applications))
        
        # User distribution
        user_roles = {}
        for user in st.session_state.users.values():
            role = user.get("role", "unknown")
            user_roles[role] = user_roles.get(role, 0) + 1
        
        fig = px.bar(x=list(user_roles.keys()), y=list(user_roles.values()), title="User Distribution by Role")
        st.plotly_chart(fig, use_container_width=True)
    
    elif menu == "User Management":
        st.markdown("### 👥 System Users")
        
        users_df = []
        for email, user in st.session_state.users.items():
            users_df.append({
                "Email": email,
                "Name": user.get("name", "N/A"),
                "Role": user.get("role", "N/A"),
                "Created": user.get("created_at", datetime.now()).strftime("%Y-%m-%d")
            })
        
        df = pd.DataFrame(users_df)
        st.dataframe(df, use_container_width=True, hide_index=True)

# Main app logic
def main():
    init_session_state()
    
    # Check if showing registration
    if st.session_state.get('show_registration', False):
        registration_page()
        return
    
    # Authentication check
    if not st.session_state.authenticated:
        login_page()
        return
    
    # Role-based routing
    role = st.session_state.role
    
    if role == "applicant":
        applicant_dashboard()
    elif role == "hospital_manager":
        hospital_manager_dashboard()
    elif role == "hr_reviewer":
        hr_dashboard()
    elif role in ["board_admin", "system_admin"]:
        admin_dashboard()
    else:
        st.error("Unknown role. Please contact administrator.")
    
    # Logout button in sidebar
    with st.sidebar:
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.role = None
            st.rerun()

if __name__ == "__main__":
    main()