from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime, timedelta
from functools import wraps
import os
import requests
import json
from dataclasses import asdict, dataclass
from typing import Optional, Dict
from flask import send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle, Spacer
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import qrcode
from PIL import Image
import os
from sqlalchemy.orm import joinedload

from os import environ
from dotenv import load_dotenv
import base64
import tempfile
import logging
from urllib.parse import urlparse, parse_qs
import atexit

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SSLCertificateManager:
    def __init__(self):
        self.cert_file = None
        
    def setup_ssl_cert(self, ca_pem):
        try:
            # Create a directory for our cert if it doesn't exist
            cert_dir = os.path.join(tempfile.gettempdir(), 'app_certs')
            os.makedirs(cert_dir, exist_ok=True)
            
            # Create a permanent file instead of a temporary one
            self.cert_file = os.path.join(cert_dir, 'mysql_ca.pem')
            
            # Write the certificate
            with open(self.cert_file, 'wb') as f:
                f.write(base64.b64decode(ca_pem))
            
            # Set appropriate permissions
            os.chmod(self.cert_file, 0o600)
            
            logger.info(f"SSL certificate created at {self.cert_file}")
            return self.cert_file
            
        except Exception as e:
            logger.error(f"Failed to create SSL certificate: {e}")
            raise
    
    def cleanup(self):
        try:
            if self.cert_file and os.path.exists(self.cert_file):
                os.remove(self.cert_file)
                logger.info("SSL certificate cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up SSL certificate: {e}")


app = Flask(__name__)

# Setup SSL Certificate
ssl_manager = SSLCertificateManager()
ssl_ca = None

if ca_pem := os.getenv('CA_PEM'):
    ssl_ca = ssl_manager.setup_ssl_cert(ca_pem)
    # Register cleanup on application shutdown
    atexit.register(ssl_manager.cleanup)

# Database configuration
db_url = os.getenv('DATABASE_URL')
if db_url:
    parsed = urlparse(db_url)
    
    # Create the base URL without query parameters
    base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    
    # Configure SQLAlchemy with SSL
    app.config.update(
        SECRET_KEY=os.getenv('SECRET_KEY', os.urandom(24)),
        SQLALCHEMY_DATABASE_URI=base_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={
            'connect_args': {
                'ssl': {
                    'ca': ssl_ca,
                    'check_hostname': False  # Aiven specific
                }
            },
            'pool_pre_ping': True,  # Add connection health check
            'pool_size': 5,
            'pool_recycle': 1800,
            'pool_timeout': 30
        }
    )
    
    logger.info("Database configuration complete")
    logger.debug(f"Final DB URL (redacted password): {base_url.replace(parsed.password, '****')}")
else:
    raise ValueError("DATABASE_URL environment variable is not set")

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'






def generate_certificate_pdf(profile, appointment):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Margins and layout constants
    margin_left = 50
    margin_right = 50
    current_y = height - 50

    # Create standard styles and add custom ones
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=26,
        alignment=1,
        textColor=colors.HexColor("#003366"),
        spaceAfter=20,
        fontName='Helvetica-Bold'
    )
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.white,
        alignment=1,
    )
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['BodyText'],
        fontSize=12,
        leading=16,
        fontName='Helvetica'
    )
    
    # ---------------- Watermark Background ---------------- #
    p.saveState()
    p.setFillColor(colors.HexColor('#f0f0f0'))
    p.setFont("Helvetica-Bold", 60)
    p.translate(width/2, height/2)
    p.rotate(45)
    p.drawCentredString(0, 0, "VAXCARE OFFICIAL")
    p.restoreState()

    # ---------------- Header Section ---------------- #
    # Header background rectangle
    header_height = 60
    p.setFillColor(colors.HexColor("#003366"))
    p.rect(0, height - header_height, width, header_height, stroke=0, fill=1)

    # Header text (Government and Document Title)
    header_text_left = Paragraph(
        "<b>Government of India</b><br/>Ministry of Health & Family Welfare", 
        ParagraphStyle('LeftHeader', parent=normal_style, fontSize=12, textColor=colors.white, alignment=0)
    )
    header_text_right = Paragraph(
        "<b>Vaccination Record</b><br/><b>Digital Certificate</b>", 
        ParagraphStyle('RightHeader', parent=normal_style, fontSize=12, textColor=colors.white, alignment=2)
    )
    header_table = Table(
        [[header_text_left, header_text_right]],
        colWidths=[width*0.7, width*0.3],
        hAlign='LEFT'
    )
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 15),
        ('RIGHTPADDING', (0,0), (-1,-1), 15)
    ]))
    header_table.wrapOn(p, width, height)
    header_table.drawOn(p, 0, height - header_height + 5)
    
    current_y = height - header_height - 30

    # ---------------- Certificate Title ---------------- #
    title = Paragraph("DIGITAL VACCINATION CERTIFICATE", title_style)
    w, h = title.wrap(width - margin_left - margin_right, 50)
    title.drawOn(p, margin_left, current_y - h)
    current_y -= h + 20

    # ---------------- Personal Information Section ---------------- #
    # Section title background
    p.setFillColor(colors.HexColor('#e8f4fc'))
    p.rect(margin_left, current_y - 25, width - margin_left - margin_right, 25, fill=1, stroke=0)
    section_title = Paragraph("<b>Personal Information</b>", ParagraphStyle('SectionTitle', parent=normal_style, fontSize=14, textColor=colors.HexColor("#003366")))
    w, h = section_title.wrap(width - margin_left - margin_right, 25)
    section_title.drawOn(p, margin_left + 10, current_y - h - 5)
    current_y -= 35

    personal_info = [
        ["Certificate ID:", f"IND/COV/{appointment.appointment_id:08d}"],
        ["Beneficiary Name:", f"{profile.fname} {(profile.mname + ' ') if profile.mname else ''}{profile.lname}"],
        ["Date of Birth:", f"01/01/{datetime.now().year - profile.age}"],
        ["Gender:", profile.gender.upper()],
        ["Unique Health ID:", f"IN{profile.profile_id:011d}"],
    ]
    info_table = Table(personal_info, colWidths=[150, width - margin_left - margin_right - 150])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e8f4fc')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.gray),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.gray),
    ]))
    tw, th = info_table.wrap(width - margin_left - margin_right, current_y)
    info_table.drawOn(p, margin_left, current_y - th)
    current_y -= (th + 30)

    # ---------------- Vaccination Details Section ---------------- #
    # Section title background
    p.setFillColor(colors.HexColor('#e8f4fc'))
    p.rect(margin_left, current_y - 25, width - margin_left - margin_right, 25, fill=1, stroke=0)
    vacc_section_title = Paragraph(
        "<b>Vaccination Details</b>",
        ParagraphStyle('SectionTitle', parent=normal_style, fontSize=14, textColor=colors.HexColor("#003366"))
    )
    w, h = vacc_section_title.wrap(width - margin_left - margin_right, 25)
    vacc_section_title.drawOn(p, margin_left + 10, current_y - h - 5)
    current_y -= 35

    # Wrap long text fields with Paragraph to allow for proper text wrapping and handling of <br/> tags.
    description_para = Paragraph(appointment.vaccine.description, normal_style)
    center_address_text = f"{appointment.schedule.centre.address}<br/>{appointment.schedule.centre.district} - {appointment.schedule.centre.pincode}"
    center_address_para = Paragraph(center_address_text, normal_style)

    vaccine_data = [
        ["Vaccine Name:", appointment.vaccine.name],
        ["Description:", description_para],
        ["Batch Number:", "BATCH-{:04d}".format(appointment.vaccine.vaccine_id)],
        ["Dose Number:", f"Dose {appointment.schedule.dose_number}"],
        ["Date of Vaccination:", appointment.appointment_date.strftime("%d/%m/%Y")],
        ["Vaccination Center:", appointment.schedule.centre.name],
        ["Center Address:", center_address_para],
    ]

    vaccine_table = Table(vaccine_data, colWidths=[150, width - margin_left - margin_right - 150])
    vaccine_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e8f4fc')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.gray),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.gray),
    ]))
    tw, th = vaccine_table.wrap(width - margin_left - margin_right, current_y)
    vaccine_table.drawOn(p, margin_left, current_y - th)
    current_y -= (th + 40)


        # ---------------- QR Code Section ---------------- #
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=3,  # Smaller QR code
        border=2,
    )
    qr_data = f"""VACCINE CERTIFICATE
    ID: IND/COV/{appointment.appointment_id:08d}
    Name: {profile.fname} {(profile.mname + ' ') if profile.mname else ''}{profile.lname}
    DOB: 01/01/{datetime.now().year - profile.age}
    Vaccine: {appointment.vaccine.name}
    Dose: {appointment.schedule.dose_number}
    Date: {appointment.appointment_date.strftime('%d/%m/%Y')}
    Center ID: {appointment.schedule.centre.centre_id}"""
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")

    img_buffer = BytesIO()
    qr_img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    qr_image = ImageReader(img_buffer)

    # Define fixed dimensions for the QR code box
    qr_box_width = 150
    qr_box_height = 150
    # Place the QR code well above the security band.
    # For example, choose a fixed Y position (e.g., 150 points from the bottom)
    qr_box_x = width - margin_right - qr_box_width
    qr_box_y = 150

    # Draw the QR code box with a white background
    p.setFillColor(colors.white)
    p.rect(qr_box_x, qr_box_y, qr_box_width, qr_box_height, fill=1, stroke=1)

    # Draw the QR code image inside the box with a margin
    qr_img_margin = 10
    qr_img_width = qr_box_width - 2 * qr_img_margin
    qr_img_height = qr_box_height - 2 * qr_img_margin
    p.drawImage(qr_image, qr_box_x + qr_img_margin, qr_box_y + qr_img_margin, qr_img_width, qr_img_height)

    # Draw the caption below the QR code box
    p.setFont("Helvetica-Bold", 10)
    p.setFillColor(colors.HexColor("#003366"))
    p.drawCentredString(qr_box_x + qr_box_width / 2, qr_box_y - 12, "Scan to Verify Authenticity")

    # ---------------- Security Features ---------------- #
    # Draw the security band at the bottom
    security_band_y = 80  # fixed Y position for the band
    security_band_height = 30
    p.setFillColor(colors.HexColor('#d3d3d3'))
    p.rect(margin_left, security_band_y, width - margin_left - margin_right, security_band_height, fill=1, stroke=0)
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 12)
    p.drawCentredString(width / 2, security_band_y + 10, "UNOFFICIAL DOCUMENT")

    # ---------------- Footer ---------------- #
    p.setFont("Helvetica", 8)
    footer_lines = [
        "* This is a mock certificate generated for educational purposes as part of a DBMS project demonstration.",
        "Not valid for official use. For demonstration purposes only.",
        f"Certificate Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
    ]
    footer_y = security_band_y - 12
    for line in footer_lines:
        p.drawCentredString(width / 2, footer_y, line)
        footer_y -= 12


    # Finalize PDF
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer




GROQ_API_KEY = environ.get('GROQ_API_KEY')
GROQ_API_URL = 'https://api.groq.com/openai/v1/chat/completions'
GROQ_MODEL = 'llama-3.3-70b-versatile'

SYSTEM_PROMPT = """You are a helpful assistant for the VaxCare vaccination management system. You can help users by providing information about:

1. Their profiles and profile management
2. Their current and upcoming appointments
3. Available vaccines and vaccination centers
4. General scheduling information
5. Basic system navigation guidance
6. Any general assistance about vaccines based on your pre trained knowledge

You can view but not modify:
- User profiles
- Appointment details
- Vaccine information
- Schedule information
- Center information

When responding:
- Provide clear, accurate information from the database
- Give step-by-step guidance for using system features
- Direct users to appropriate pages for actions
- Format dates as YYYY-MM-DD and times in 24-hour format
- Maintain a helpful and health-focused tone
- Well structured message with proper spaces and New lines

You cannot:
- Directly modify any database records
- Access admin functions
- View sensitive system information
- Make changes to appointments or profiles"""


# User Roles Constants
ROLE_USER = 'user'
ROLE_ADMIN = 'admin'
ROLE_VACCINE_ADMIN = 'vaccine_admin'

# Admin email list 
ADMIN_EMAILS = ['admin@example.com']
VACCINE_ADMIN_EMAILS = ['vaccine_admin@example.com']

# Models
class User(UserMixin, db.Model):
    __tablename__ = 'Users'
    user_id = db.Column('user_id', db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    profiles = db.relationship('Profile', backref='user', lazy=True)

    def get_id(self):
        return str(self.user_id)

    @property
    def role(self):
        if self.email in ADMIN_EMAILS:
            return ROLE_ADMIN
        elif self.email in VACCINE_ADMIN_EMAILS:
            return ROLE_VACCINE_ADMIN
        return ROLE_USER

class Profile(db.Model):
    __tablename__ = 'Profiles'
    profile_id = db.Column('profile_id', db.Integer, primary_key=True, autoincrement=True)
    gender = db.Column(db.String(10))
    fname = db.Column(db.String(50))
    mname = db.Column(db.String(50))
    lname = db.Column(db.String(50))
    age = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'))
    appointments = db.relationship('Appointment', backref='profile', lazy=True)

class Vaccine(db.Model):
    __tablename__ = 'Vaccines'
    vaccine_id = db.Column('vaccine_id', db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.Text)
    min_age = db.Column(db.Integer)
    max_age = db.Column(db.Integer)
    name = db.Column(db.String(100))

class Inventory(db.Model):
    __tablename__ = 'Inventory'
    inventory_id = db.Column('inventory_id', db.Integer, primary_key=True, autoincrement=True)
    expiration_date = db.Column(db.Date)
    quantity = db.Column(db.Integer)
    vaccines = db.relationship('Vaccine', secondary='StoredAt')

class VaccineCentre(db.Model):
    __tablename__ = 'VaccineCentres'
    centre_id = db.Column('centre_id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    address = db.Column(db.Text)
    district = db.Column(db.String(50))
    pincode = db.Column(db.String(10))

class Schedule(db.Model):
    __tablename__ = 'Schedules'
    schedule_id = db.Column('schedule_id', db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date)
    dose_number = db.Column(db.Integer)
    centre_id = db.Column(db.Integer, db.ForeignKey('VaccineCentres.centre_id'))
    centre = db.relationship('VaccineCentre')
    vaccines = db.relationship('Vaccine', secondary='Includes')

class Appointment(db.Model):
    __tablename__ = 'Appointments'
    appointment_id = db.Column('appointment_id', db.Integer, primary_key=True, autoincrement=True)
    appointment_date = db.Column(db.Date)
    time_slot = db.Column(db.Time)
    vaccine_id = db.Column(db.Integer, db.ForeignKey('Vaccines.vaccine_id'))
    profile_id = db.Column(db.Integer, db.ForeignKey('Profiles.profile_id'))
    schedule_id = db.Column(db.Integer, db.ForeignKey('Schedules.schedule_id'))
    vaccine = db.relationship('Vaccine')
    schedule = db.relationship('Schedule')

# Association Tables
stored_at = db.Table('StoredAt',
    db.Column('inventory_id', db.Integer, db.ForeignKey('Inventory.inventory_id'), primary_key=True),
    db.Column('vaccine_id', db.Integer, db.ForeignKey('Vaccines.vaccine_id'), primary_key=True)
)

includes = db.Table('Includes',
    db.Column('vaccine_id', db.Integer, db.ForeignKey('Vaccines.vaccine_id'), primary_key=True),
    db.Column('schedule_id', db.Integer, db.ForeignKey('Schedules.schedule_id'), primary_key=True)
)

available_at = db.Table('AvailableAt',
    db.Column('vaccine_id', db.Integer, db.ForeignKey('Vaccines.vaccine_id'), primary_key=True),
    db.Column('centre_id', db.Integer, db.ForeignKey('VaccineCentres.centre_id'), primary_key=True)
)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Role-based access control decorator
def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Routes
#@app.route('/create-admin', methods=['GET'])
#def create_admin():
#    admin_email = '1343431@vx.com' 
#    admin_password = 'uydgdfausyfgawj'  

    # Check if the admin already exists
#    if User.query.filter_by(email=admin_email).first():
#        return "Admin account already exists."

 #   # Create the admin account
#    hashed_password = generate_password_hash(admin_password)
#    admin_user = User(email=admin_email, password=hashed_password)
#    db.session.add(admin_user)
#   db.session.commit()

#    return "Admin account created successfully!"

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/')
@login_required
def index():
    # Fetch profiles for the current user
    profiles = Profile.query.filter_by(user_id=current_user.user_id).all()

    # Prepare profile-wise appointments
    profile_appointments = {}
    for profile in profiles:
        appointments = Appointment.query.filter_by(profile_id=profile.profile_id).all()
        profile_appointments[profile] = appointments

    # Fetch all appointments for the current user
    all_appointments = Appointment.query.join(Profile).filter(Profile.user_id == current_user.user_id).all()

    # Pass data to the template
    return render_template('index.html', 
                           profile_appointments=profile_appointments, 
                           all_appointments=all_appointments,
                           upcoming_appointments=[appt for appt_list in profile_appointments.values() for appt in appt_list])


@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        # If user is already logged in, redirect them to dashboard
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            email = request.form.get('email').strip()
            password = request.form.get('password').strip()
            
            print(f"Login attempt for email: {email}")
            
            user = User.query.filter_by(email=email).first()
            if user:
                print(f"User found with id: {user.user_id}")
                if check_password_hash(user.password, password):
                    login_user(user)
                    flash('Login successful!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    print("Password check failed")
            else:
                print("User not found")
                
            flash('Invalid email or password', 'error')
    except Exception as e:
        print(f"Login error: {str(e)}")
        flash('An error occurred during login', 'error')
        
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
            
        hashed_password = generate_password_hash(password)
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == ROLE_ADMIN:
        # Admin-specific data
        chart_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May']  # Example data
        chart_data = [10, 20, 30, 40, 50]  # Example data
        vaccines = Vaccine.query.all()
        centres = VaccineCentre.query.all()
        today_appointments = Appointment.query.filter(
            Appointment.appointment_date == date.today()
        ).count()
        recent_activities = [
            {"description": "Vaccine stock updated", "timestamp": datetime.now()},
            {"description": "Schedules Updated", "timestamp": datetime.now()},
        ]

        return render_template(
            'admin_dashboard.html',
            vaccines=vaccines,
            centres=centres,
            today_appointments=today_appointments,
            recent_activities=recent_activities,
            chart_labels=chart_labels,
            chart_data=chart_data,
        )

    elif current_user.role == ROLE_VACCINE_ADMIN:
        return render_template('vaccine_admin_dashboard.html')
    else:
        # For regular users:
        profiles = Profile.query.filter_by(user_id=current_user.user_id).all()
        appointments = Appointment.query.join(Profile).filter(Profile.user_id == current_user.user_id).all()
        today = date.today()
        # Compute vaccination history (appointments before today)
        vaccination_history = [appt for appt in appointments if appt.appointment_date < today]
        # Compute upcoming appointments (today or in the future)
        upcoming_reminders = [appt for appt in appointments if appt.appointment_date >= today]
        return render_template(
            'user_dashboard.html',
            profiles=profiles,
            appointments=appointments,
            today=today,
            vaccination_history=vaccination_history,
            upcoming_reminders=upcoming_reminders
        )


# Profile Management
@app.route('/profile/create', methods=['GET', 'POST'])
@login_required
def create_profile():
    if request.method == 'POST':
        profile = Profile(
            gender=request.form.get('gender'),
            fname=request.form.get('fname'),
            mname=request.form.get('mname'),
            lname=request.form.get('lname'),
            age=int(request.form.get('age')),
            user_id=current_user.user_id
        )
        db.session.add(profile)
        db.session.commit()
        flash('Profile created successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('create_profile.html')

@app.route('/profile/<int:profile_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_profile(profile_id):
    profile = Profile.query.get_or_404(profile_id)
    if profile.user_id != current_user.user_id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        profile.gender = request.form.get('gender')
        profile.fname = request.form.get('fname')
        profile.mname = request.form.get('mname')
        profile.lname = request.form.get('lname')
        profile.age = int(request.form.get('age'))
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('edit_profile.html', profile=profile)

# Appointment Management

@app.route('/appointments/book', methods=['GET', 'POST'])
@login_required
def book_appointment():
    if request.method == 'POST':
        profile_id = request.form.get('profile_id')
        schedule_id = request.form.get('schedule_id')
        vaccine_id = request.form.get('vaccine_id')
        time_slot = request.form.get('time_slot')

        # Validate profile belongs to current user
        profile = Profile.query.get_or_404(profile_id)
        if profile.user_id != current_user.user_id:
            flash('Unauthorized access', 'error')
            return redirect(url_for('book_appointment'))

        # Fetch the selected schedule and validate
        schedule = Schedule.query.get_or_404(schedule_id)
        
        # Check if the vaccine is included in the schedule
        if vaccine_id not in [str(v.vaccine_id) for v in schedule.vaccines]:
            flash('Selected vaccine is not available in this schedule', 'error')
            return redirect(url_for('book_appointment'))

        # Check schedule availability
        existing_appointments = Appointment.query.filter_by(
            schedule_id=schedule_id,
            time_slot=time_slot
        ).count()

        if existing_appointments >= 10:
            flash('This time slot is full', 'error')
            return redirect(url_for('book_appointment'))

        # Create appointment
        appointment = Appointment(
            appointment_date=schedule.date,
            time_slot=time_slot,
            vaccine_id=vaccine_id,
            profile_id=profile_id,
            schedule_id=schedule_id
        )
        db.session.add(appointment)
        db.session.commit()

        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('dashboard'))

    # For GET request
    profiles = Profile.query.filter_by(user_id=current_user.user_id).all()
    
    # Only fetch future schedules
    current_date = datetime.now().date()
    schedules = Schedule.query.filter(
        Schedule.date >= current_date
    ).order_by(Schedule.date).all()

    # Get all available vaccines
    vaccines = Vaccine.query.all()

    # Create mappings for the relationships
    schedule_vaccines = {}
    vaccine_schedules = {}

    for schedule in schedules:
        schedule_vaccines[schedule.schedule_id] = [
            {
                'id': v.vaccine_id,
                'name': v.name
            } for v in schedule.vaccines
        ]

    for vaccine in vaccines:
        # Get future schedules for each vaccine
        vaccine_schedules[vaccine.vaccine_id] = [
            {
                'id': s.schedule_id,
                'date': s.date.strftime('%Y-%m-%d'),
                'centre_name': s.centre.name
            }
            for s in Schedule.query.filter(
                Schedule.date >= current_date,
                Schedule.vaccines.contains(vaccine)
            ).all()
        ]

    return render_template('book_appointment.html',
                         profiles=profiles,
                         schedules=schedules,
                         vaccines=vaccines,
                         schedule_vaccines=schedule_vaccines,
                         vaccine_schedules=vaccine_schedules,
                         today=date.today())




# API endpoints for dynamic updates
@app.route('/api/schedule/<int:schedule_id>/vaccines')
@login_required
def get_schedule_vaccines(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    available_vaccines = [{
        'id': v.vaccine_id,
        'name': v.name
    } for v in schedule.vaccines]
    return jsonify(available_vaccines)

@app.route('/api/vaccine/<int:vaccine_id>/schedules')
@login_required
def get_vaccine_schedules(vaccine_id):
    current_date = datetime.now().date()
    vaccine = Vaccine.query.get_or_404(vaccine_id)
    available_schedules = [{
        'id': s.schedule_id,
        'date': s.date.strftime('%Y-%m-%d'),
        'centre_name': s.centre.name
    } for s in Schedule.query.filter(
        Schedule.date >= current_date,
        Schedule.vaccines.contains(vaccine)
    ).order_by(Schedule.date).all()]
    return jsonify(available_schedules)


@app.route('/appointments/<int:appointment_id>/cancel')
@login_required
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    profile = Profile.query.get(appointment.profile_id)
    
    if profile.user_id != current_user.user_id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('dashboard'))
    
    if appointment.appointment_date < datetime.now().date():
        flash('Cannot cancel past appointments', 'error')
        return redirect(url_for('dashboard'))
    
    db.session.delete(appointment)
    db.session.commit()
    flash('Appointment cancelled successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/appointments/<int:appointment_id>/reschedule', methods=['GET', 'POST'])
@login_required
def reschedule_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)

    # Ensure the appointment belongs to the current user
    if appointment.profile.user_id != current_user.user_id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        new_schedule_id = request.form.get('schedule_id')
        new_time_slot = request.form.get('time_slot')

        # Validate the new schedule
        new_schedule = Schedule.query.get_or_404(new_schedule_id)
        existing_appointments = Appointment.query.filter_by(schedule_id=new_schedule_id, time_slot=new_time_slot).count()

        if existing_appointments >= 10:  # Assuming max 10 appointments per slot
            flash('This time slot is full', 'error')
        else:
            appointment.schedule_id = new_schedule_id
            appointment.time_slot = new_time_slot
            appointment.appointment_date = new_schedule.date
            db.session.commit()
            flash('Appointment rescheduled successfully!', 'success')
            return redirect(url_for('dashboard'))

    schedules = Schedule.query.filter(Schedule.date >= datetime.now()).all()
    return render_template('reschedule_appointment.html', appointment=appointment, schedules=schedules)


# Admin Routes
@app.route('/admin/vaccines', methods=['GET', 'POST'])
@login_required
@role_required([ROLE_ADMIN])
def manage_vaccines():
    if request.method == 'POST':
        vaccine = Vaccine(
            name=request.form.get('name'),
            description=request.form.get('description'),
            min_age=int(request.form.get('min_age')),
            max_age=int(request.form.get('max_age'))
        )
        db.session.add(vaccine)
        db.session.commit()
        flash('Vaccine added successfully!', 'success')
        return redirect(url_for('manage_vaccines'))
    
    vaccines = Vaccine.query.all()
    return render_template('admin/manage_vaccines.html', vaccines=vaccines)

@app.route('/admin/vaccines/edit/<int:vaccine_id>', methods=['GET', 'POST'])
@login_required
@role_required([ROLE_ADMIN])
def edit_vaccine(vaccine_id):
    vaccine = Vaccine.query.get_or_404(vaccine_id)

    if request.method == 'POST':
        vaccine.name = request.form.get('name')
        vaccine.description = request.form.get('description')
        vaccine.min_age = request.form.get('min_age')
        vaccine.max_age = request.form.get('max_age')

        db.session.commit()
        flash('Vaccine updated successfully!', 'success')
        return redirect(url_for('manage_vaccines'))

    return render_template('edit_vaccine.html', vaccine=vaccine)

@app.route('/admin/vaccines/delete/<int:vaccine_id>', methods=['POST'])
@login_required
@role_required([ROLE_ADMIN])
def delete_vaccine(vaccine_id):
    vaccine = Vaccine.query.get_or_404(vaccine_id)

    # Prevent deletion if the vaccine is referenced in schedules or inventory
    if Schedule.query.join(Schedule.vaccines).filter(Vaccine.vaccine_id == vaccine_id).count() > 0:
        flash('Cannot delete vaccine with associated schedules. Remove them first.', 'error')
        return redirect(url_for('manage_vaccines'))

    db.session.delete(vaccine)
    db.session.commit()
    flash('Vaccine deleted successfully!', 'success')
    return redirect(url_for('manage_vaccines'))


@app.route('/admin/schedules', methods=['GET', 'POST'])
@login_required
@role_required([ROLE_ADMIN, ROLE_VACCINE_ADMIN])
def manage_schedules():
    if request.method == 'POST':
        schedule = Schedule(
            date=datetime.strptime(request.form.get('date'), '%Y-%m-%d'),
            dose_number=int(request.form.get('dose_number')),
            centre_id=int(request.form.get('centre_id'))
        )
        db.session.add(schedule)
        db.session.commit()
        
        # Add selected vaccines to schedule
        vaccine_ids = request.form.getlist('vaccines')
        for vaccine_id in vaccine_ids:
            vaccine = Vaccine.query.get(vaccine_id)
            schedule.vaccines.append(vaccine)
        
        db.session.commit()
        flash('Schedule created successfully!', 'success')
        return redirect(url_for('manage_schedules'))
    
    schedules = Schedule.query.all()
    centres = VaccineCentre.query.all()
    vaccines = Vaccine.query.all()
    return render_template('admin/manage_schedules.html',
                         schedules=schedules,
                         centres=centres,
                         vaccines=vaccines)


@app.route('/admin/schedules/edit/<int:schedule_id>', methods=['GET', 'POST'])
@login_required
@role_required([ROLE_ADMIN, ROLE_VACCINE_ADMIN])
def edit_schedule(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    centres = VaccineCentre.query.all()
    vaccines = Vaccine.query.all()

    if request.method == 'POST':
        schedule.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d')
        schedule.centre_id = int(request.form.get('centre_id'))
        schedule.dose_number = int(request.form.get('dose_number'))

        # Update vaccines
        schedule.vaccines.clear()
        selected_vaccines = request.form.getlist('vaccines')
        for vaccine_id in selected_vaccines:
            vaccine = Vaccine.query.get(vaccine_id)
            schedule.vaccines.append(vaccine)

        db.session.commit()
        flash('Schedule updated successfully!', 'success')
        return redirect(url_for('manage_schedules'))

    return render_template('edit_schedule.html', schedule=schedule, centres=centres, vaccines=vaccines,)



@app.route('/admin/schedules/delete/<int:schedule_id>', methods=['POST'])
@login_required
@role_required([ROLE_ADMIN, ROLE_VACCINE_ADMIN])
def delete_schedule(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)

    # Check if there are appointments linked to this schedule
    if Appointment.query.filter_by(schedule_id=schedule_id).count() > 0:
        flash("Cannot delete schedule with existing appointments. Please cancel associated appointments first.", "error")
        return redirect(url_for('manage_schedules'))

    db.session.delete(schedule)
    db.session.commit()
    flash('Schedule deleted successfully!', 'success')
    return redirect(url_for('manage_schedules'))




@app.route('/admin/centres', methods=['GET', 'POST'])
@login_required
@role_required([ROLE_ADMIN])
def manage_centres():
    if request.method == 'POST':
        centre = VaccineCentre(
            name=request.form.get('name'),
            address=request.form.get('address'),
            district=request.form.get('district'),
            pincode=request.form.get('pincode')
        )
        db.session.add(centre)
        db.session.commit()
        flash('Vaccination centre added successfully!', 'success')
        return redirect(url_for('manage_centres'))
    
    centres = VaccineCentre.query.all()
    return render_template('admin/manage_centres.html', centres=centres)

@app.route('/admin/centres/edit/<int:centre_id>', methods=['GET', 'POST'])
@login_required
@role_required([ROLE_ADMIN])
def edit_centre(centre_id):
    centre = VaccineCentre.query.get_or_404(centre_id)

    if request.method == 'POST':
        centre.name = request.form.get('name')
        centre.address = request.form.get('address')
        centre.district = request.form.get('district')
        centre.pincode = request.form.get('pincode')
        
        db.session.commit()
        flash('Vaccination center updated successfully!', 'success')
        return redirect(url_for('manage_centres'))

    return render_template('edit_centre.html', centre=centre)

@app.route('/admin/centres/delete/<int:centre_id>', methods=['POST'])
@login_required
@role_required([ROLE_ADMIN])
def delete_centre(centre_id):
    centre = VaccineCentre.query.get_or_404(centre_id)

    # Prevent deletion if center is referenced in schedules
    if Schedule.query.filter_by(centre_id=centre_id).count() > 0:
        flash('Cannot delete center with associated schedules. Remove them first.', 'error')
        return redirect(url_for('manage_centres'))

    db.session.delete(centre)
    db.session.commit()
    flash('Vaccination center deleted successfully!', 'success')
    return redirect(url_for('manage_centres'))


@app.route('/admin/inventory', methods=['GET', 'POST'])
@login_required
@role_required([ROLE_ADMIN])
def manage_inventory():
    if request.method == 'POST':
        try:
            # Get form data
            vaccine_id = request.form.get('vaccine_id')
            expiration_date = datetime.strptime(request.form.get('expiration_date'), '%Y-%m-%d')
            quantity = int(request.form.get('quantity'))

            # Create new inventory entry
            inventory = Inventory(
                expiration_date=expiration_date,
                quantity=quantity
            )
            
            # Add vaccine relationship
            vaccine = Vaccine.query.get(vaccine_id)
            if vaccine:
                inventory.vaccines.append(vaccine)
            
            db.session.add(inventory)
            db.session.commit()
            flash('Inventory added successfully!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating inventory: {str(e)}', 'error')
        
        return redirect(url_for('manage_inventory'))
    
    # GET request handling
    inventories = Inventory.query.options(db.joinedload(Inventory.vaccines)).all()
    vaccines = Vaccine.query.all()
    return render_template(
        'admin/manage_inventory.html',
        inventories=inventories,
        vaccines=vaccines,
        current_date=date.today()
    )


@app.route('/admin/inventory/edit/<int:inventory_id>', methods=['GET', 'POST'])
@login_required
@role_required([ROLE_ADMIN])
def edit_inventory(inventory_id):
    inventory = Inventory.query.options(db.joinedload(Inventory.vaccines)).get_or_404(inventory_id)
    vaccines = Vaccine.query.all()
    
    if request.method == 'POST':
        try:
            # Update inventory details
            inventory.expiration_date = datetime.strptime(request.form.get('expiration_date'), '%Y-%m-%d')
            inventory.quantity = int(request.form.get('quantity'))
            
            # Update vaccine association
            new_vaccine = Vaccine.query.get(request.form.get('vaccine_id'))
            if new_vaccine:
                inventory.vaccines = [new_vaccine]  # Replace existing vaccines
            
            db.session.commit()
            flash('Inventory updated successfully!', 'success')
            return redirect(url_for('manage_inventory'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating inventory: {str(e)}', 'error')
    
    return render_template('admin/edit_inventory.html', 
                         inventory=inventory,
                         vaccines=vaccines)

@app.route('/admin/inventory/delete/<int:inventory_id>', methods=['POST'])
@login_required
@role_required([ROLE_ADMIN])
def delete_inventory(inventory_id):
    inventory = Inventory.query.get_or_404(inventory_id)
    try:
        db.session.delete(inventory)
        db.session.commit()
        flash('Inventory deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting inventory: {str(e)}', 'error')
    return redirect(url_for('manage_inventory'))


# API Endpoints for AJAX requests
@app.route('/api/schedules/<date>')
@login_required
def get_schedules(date):
    try:
        target_date = datetime.strptime(date, '%Y-%m-%d').date()
        schedules = Schedule.query.filter_by(date=target_date).all()
        return jsonify([{
            'id': s.schedule_id,
            'centre': s.centre.name,
            'vaccines': [{'id': v.vaccine_id, 'name': v.name} for v in s.vaccines],
            'dose_number': s.dose_number,
            'available_slots': 10 - Appointment.query.filter_by(schedule_id=s.schedule_id).count()
        } for s in schedules])
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/vaccine-availability/<int:centre_id>')
@login_required
def get_vaccine_availability(centre_id):
    centre = VaccineCentre.query.get_or_404(centre_id)
    available_vaccines = db.session.query(Vaccine)\
        .join(stored_at)\
        .join(Inventory)\
        .filter(Inventory.quantity > 0)\
        .join(available_at)\
        .filter(available_at.c.centre_id == centre_id)\
        .all()
    
    return jsonify([{
        'id': v.vaccine_id,
        'name': v.name,
        'min_age': v.min_age,
        'max_age': v.max_age
    } for v in available_vaccines])

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

@dataclass
class ChatContext:
    selected_profile_id: Optional[int] = None
    selected_vaccine_id: Optional[int] = None
    selected_date: Optional[str] = None
    selected_time: Optional[str] = None
    current_task: Optional[str] = None
    
    def to_dict(self):
        return {k: v for k, v in asdict(self).items() if v is not None}
    

# Add this route to app.py
@app.route('/admin/appointments')
@login_required
@role_required([ROLE_ADMIN])
def admin_appointments():
    # Query all appointments with related information using joins
    appointments = (
        db.session.query(
            Appointment,
            Profile,
            User,
            Vaccine,
            Schedule,
            VaccineCentre
        )
        .join(Profile, Appointment.profile_id == Profile.profile_id)
        .join(User, Profile.user_id == User.user_id)
        .join(Vaccine, Appointment.vaccine_id == Vaccine.vaccine_id)
        .join(Schedule, Appointment.schedule_id == Schedule.schedule_id)
        .join(VaccineCentre, Schedule.centre_id == VaccineCentre.centre_id)
        .order_by(Appointment.appointment_date.desc())
        .all()
    )
    
    # Group appointments by user email and profile
    grouped_appointments = {}
    for appt, profile, user, vaccine, schedule, centre in appointments:
        if user.email not in grouped_appointments:
            grouped_appointments[user.email] = {}
        
        profile_key = f"{profile.fname} {profile.lname}"
        if profile_key not in grouped_appointments[user.email]:
            grouped_appointments[user.email][profile_key] = []
            
        grouped_appointments[user.email][profile_key].append({
            'appointment_id': appt.appointment_id,
            'date': appt.appointment_date,
            'time': appt.time_slot,
            'vaccine': vaccine.name,
            'dose_number': schedule.dose_number,
            'centre': centre.name,
            'district': centre.district,
            'profile_id': profile.profile_id,
            'age': profile.age,
            'gender': profile.gender
        })
    
    return render_template('admin/appointments_overview.html', appointments=grouped_appointments)


@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat_interface():
    if current_user.role != ROLE_USER:
        flash('This feature is only available for regular users.', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        try:
            user_message = request.json.get('message', '')
            
            # Fetch comprehensive user-visible database information
            profiles = Profile.query.filter_by(user_id=current_user.user_id).all()
            profile_info = [{
                "name": f"{p.fname} {p.lname}",
                "age": p.age,
                "gender": p.gender,
                "id": p.profile_id
            } for p in profiles]

            # Get user's appointments with more details
            appointments = (Appointment.query
                          .join(Profile)
                          .filter(Profile.user_id == current_user.user_id)
                          .join(Vaccine)
                          .join(Schedule)
                          .join(VaccineCentre)
                          .all())
            
            appt_info = [{
                "date": a.appointment_date.strftime('%Y-%m-%d'),
                "time": a.time_slot.strftime('%H:%M'),
                "vaccine": a.vaccine.name,
                "centre": a.schedule.centre.name,
                "address": a.schedule.centre.address,
                "id": a.appointment_id
            } for a in appointments]

            # Get available vaccines
            vaccines = Vaccine.query.all()
            vaccine_info = [{
                "name": v.name,
                "description": v.description,
                "min_age": v.min_age,
                "max_age": v.max_age
            } for v in vaccines]

            # Get vaccination centers
            centres = VaccineCentre.query.all()
            centre_info = [{
                "name": c.name,
                "address": c.address,
                "district": c.district,
                "pincode": c.pincode
            } for c in centres]

            # Build comprehensive context message
            context = f"""Current user: {current_user.email}

User Profiles:
{json.dumps(profile_info, indent=2)}

User Appointments:
{json.dumps(appt_info, indent=2)}

Available Vaccines:
{json.dumps(vaccine_info, indent=2)}

Vaccination Centers:
{json.dumps(centre_info, indent=2)}"""

            # Make API call to Groq
            response = requests.post(
                GROQ_API_URL,
                headers={
                    'Authorization': f'Bearer {GROQ_API_KEY}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': GROQ_MODEL,
                    'messages': [
                        {'role': 'system', 'content': SYSTEM_PROMPT},
                        {'role': 'user', 'content': f"Context:\n{context}\n\nUser message: {user_message}"}
                    ],
                    'temperature': 1,
                    'max_tokens': 1024,
                    'stream': False
                }
            )
            
            if response.status_code == 200:
                ai_response = response.json()['choices'][0]['message']['content']
                return jsonify({'response': ai_response})
            else:
                return jsonify({'error': 'Failed to get response from AI'}), 500

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # GET request - render chat interface
    try:
        profiles = Profile.query.filter_by(user_id=current_user.user_id).all()
        return render_template('chat.html', profiles=profiles)
    except Exception as e:
        flash('An error occurred while loading the chat interface.', 'error')
        return redirect(url_for('dashboard'))

@app.route('/certificates')
@login_required
def view_certificates():
    profiles = Profile.query.filter_by(user_id=current_user.user_id).all()
    profile_appointments = {}
    for profile in profiles:
        appointments = (Appointment.query
                      .filter_by(profile_id=profile.profile_id)
                      .join(Vaccine)
                      .join(Schedule)
                      .join(VaccineCentre)
                      .all())
        profile_appointments[profile.profile_id] = appointments
    
    current_date_str = datetime.utcnow().strftime('%Y-%m-%d')
    return render_template('certificates.html', 
                         profiles=profiles,
                         profile_appointments=profile_appointments,
                         current_date_str=current_date_str)     # Pass to template

@app.route('/download_certificate/<int:appointment_id>')
@login_required
def download_certificate(appointment_id):
    # Get appointment with all related data
    appointment = (Appointment.query
                  .join(Profile)
                  .join(Vaccine)
                  .join(Schedule)
                  .join(VaccineCentre)
                  .filter(Appointment.appointment_id == appointment_id)
                  .first_or_404())
    
    # Verify user owns this appointment
    if appointment.profile.user_id != current_user.user_id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('view_certificates'))
    
    # Generate PDF
    pdf_buffer = generate_certificate_pdf(appointment.profile, appointment)
    
    # Send file to user
    return send_file(
        pdf_buffer,
        download_name=f'vaccination_certificate_{appointment.appointment_id}.pdf',
        mimetype='application/pdf'
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(environ.get('PORT', 10000)))