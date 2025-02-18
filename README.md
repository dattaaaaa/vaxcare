# VaxCare - Vaccination Management System

A comprehensive web-based vaccination management system built with Flask, allowing users to schedule vaccinations, manage profiles, and generate digital certificates. The system includes user, admin, and vaccine administrator roles with different privileges.

[View the latest deployment of this flask web application here](https://vaxincare.onrender.com/)

## Features

### User Features
- User registration and authentication
- Profile management for multiple family members
- Vaccination appointment booking and management
- Real-time AI chat support and insights
- Digital certificate generation and download
- Appointment rescheduling and cancellation
- View vaccination history and upcoming appointments

### Admin Features
- Vaccine inventory management
- Vaccination center management
- Schedule management
- Appointment oversight
- User management
- System monitoring and analytics

### Technical Features
- Secure password hashing
- Role-based access control
- SSL certificate management
- Database connection pooling
- PDF certificate generation
- QR code generation for certificates
- Real-time AI chat support
- Responsive web interface

## Technologies Used

- **Backend**: Python Flask
- **Database**: MySQL (with SSL support)
- **ORM**: SQLAlchemy
- **Authentication**: Flask-Login
- **PDF Generation**: ReportLab
- **QR Code**: qrcode
- **AI Integration**: Groq API
- **Frontend**: HTML, CSS, JavaScript
- **Security**: Werkzeug security
- **Environment Management**: python-dotenv

## Relational Database Creation with MySQL

- Relational Schema:
![Relational Schema](Relational_Schema.png)


1. **Install MySQL**  
   Ensure MySQL is installed on your system. You can download it from [MySQL's official website](https://dev.mysql.com/downloads/installer/) or use a package manager like `apt` (Linux) or `brew` (Mac).  

2. **Create a Database and User**  
   Log into MySQL and create a database for the application. Also, create a dedicated user with the necessary privileges.  

3. **Enable SSL (If you are using an online instance of MySQL from providers like Aiven.io)**  
    (Ignore this step if you are using a local MySQL database)
   If using an online database or requiring encrypted connections, configure SSL and obtain the CA certificate.
   - Encode the ca.pem (and client-cert.pem and client-key.pem if you have them) to Base64 string for compatibility with the given code.
   ```bash
    [Convert]::ToBase64String((Get-Content -Path "ca.pem" -Raw -Encoding Byte)) | Set-Content -Path "ca_base64.txt"
    [Convert]::ToBase64String((Get-Content -Path "client-cert.pem" -Raw -Encoding Byte)) | Set-Content -Path "cert_base64.txt"
    [Convert]::ToBase64String((Get-Content -Path "client-key.pem" -Raw -Encoding Byte)) | Set-Content -Path "key_base64.txt"
   ```
   - Add CA_PEM=your_base64_encoded_ca to your environent variables.

4. **Update `.env` Configuration**  
   Add your MySQL connection details to the `.env` file, including the `DATABASE_URL` and SSL certificate (that can be done by).  

5. **Initialize the Database**  
   Run migrations to set up the required tables and relationships.  

6. **Verify Connection**  
   Ensure the Flask application connects successfully to the MySQL database before running the server. 

## Installation

1. Clone the repository:
```bash
git clone https://github.com/dattaaaa/vaxcare.git
cd vaxcare
```

2. Create and activate a virtual environment:
```bash
python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with the following variables:
```
DATABASE_URL=mysql://username:password@host:port/database_name
SECRET_KEY=your_secret_key
GROQ_API_KEY=your_groq_api_key
CA_PEM=your_ssl_certificate_in_base64
```

5. Initialize the database:
```bash
flask db upgrade
```

## Running the Application

### Development Server
```bash
python app.py
```

### Production Server
```bash
gunicorn -c gunicorn_config.py app:app
```

## Project Structure

```
vaxcare/
|   .env
|   .gitignore
|   app.py
|   Create_tables.sql
|   Entity-Relationship(ER)-diagram.png
|   guincorn_config.py
|   LICENSE
|   Populate_all.sql
|   project_structure.txt
|   README.md
|   Relational_Schema.png
|   requirements.txt
|   
+---Documents
|       Report.pdf
|       
+---static
|       android-chrome-192x192.png
|       android-chrome-512x512.png
|       apple-touch-icon.png
|       favicon-16x16.png
|       favicon-32x32.png
|       favicon.ico
|       
\---templates
    |   admin_dashboard.html
    |   base.html
    |   book_appointment.html
    |   certificates.html
    |   chat.html
    |   create_profile.html
    |   edit_centre.html
    |   edit_profile.html
    |   edit_schedule.html
    |   edit_vaccine.html
    |   home.html
    |   index.html
    |   login.html
    |   register.html
    |   reschedule_appointment.html
    |   temp.html
    |   user_dashboard.html
    |   vaccine_admin_dashboard.html
    |   
    +---admin
    |       appointments_overview.html
    |       edit_inventory.html
    |       manage_centres.html
    |       manage_inventory.html
    |       manage_schedules.html
    |       manage_vaccines.html
    |       
    \---errors
            404.html
            500.html
```

## Configuration

### Database Configuration
The application uses MySQL with SSL encryption. Make sure your database server supports SSL connections and provide the CA certificate in the `.env` file.
If you want an online MySQL database, login to [Aiven Console](https://console.aiven.io/) to get your credentials and CA certificate.
You can as well remove the CA certificate part from the app if you are using a local MySQL database instance.

### Gunicorn Configuration
The application includes a `gunicorn_config.py` with the following settings:
- 4 worker processes
- Binding to 0.0.0.0:10000
- 120-second timeout

## Security Features

- Password hashing using Werkzeug
- SSL/TLS database connections
- Role-based access control
- Session management
- CSRF protection
- Secure cookie handling

## API Endpoints

The application provides several API endpoints for:
- Schedule management
- Vaccine availability checking
- Appointment management
- Certificate generation
- Chat functionality

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

Vishnu Datta - kvishnudatta.ai22@rvce.edu.in
Project Link: https://github.com/dattaaaaa/vaxcare

## Acknowledgments

- Flask framework and its extensions
- ReportLab for PDF generation
- Groq AI for chat support
- All other open-source libraries used in this project
