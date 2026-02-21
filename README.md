# FleetFlow - Fleet & Logistics Management System

A comprehensive fleet management web application built with Django that helps businesses manage their vehicle fleets, drivers, trips, maintenance, fuel expenses, and operational analytics.

## 🚀 Features

### 🔐 Authentication & Role Management
- User registration and login system
- Role-based access control (Fleet Manager, Dispatcher, Safety Officer, Financial Analyst)
- Session management and security

### 📊 Command Center Dashboard
- Real-time KPIs and metrics
- Fleet utilization statistics
- Interactive charts and graphs
- Recent activities and system alerts

### 🚛 Vehicle Registry
- Complete vehicle information management
- Vehicle status tracking (Available, On Trip, In Shop, Retired)
- Document management (registration, insurance, permits)
- Maintenance scheduling integration

### 🧭 Trip Dispatcher System
- Trip creation and management
- Automated capacity validation
- Driver and vehicle assignment
- Trip status tracking (Draft → Dispatched → In Progress → Completed)

### 🔧 Maintenance & Service Logs
- Maintenance scheduling and tracking
- Service history and parts management
- Automated reminders and alerts
- Cost tracking and reporting

### ⛽ Fuel & Expense Tracking
- Fuel consumption monitoring
- Expense categorization and approval
- Budget management
- Receipt and document management

### 👨‍✈️ Driver Performance & Safety
- Driver profile management
- License expiry tracking
- Performance metrics and safety scoring
- Attendance and scheduling

### 📈 Analytics & Financial Reports
- Comprehensive reporting system
- Fuel efficiency analysis
- Cost per kilometer tracking
- Export capabilities (PDF, Excel, CSV)

## 🛠 Technology Stack

### Backend
- **Python 3**
- **Django 4.2.7**
- **Django REST Framework**
- **MySQL Database**

### Frontend
- **HTML5**
- **CSS3**
- **Bootstrap 5**
- **JavaScript (Vanilla)**
- **Chart.js** (Analytics)
- **DataTables.js** (Data Tables)

### Tools & Libraries
- **Django Admin Panel**
- **django-import-export** (Data import/export)
- **django-crispy-forms** (Form styling)
- **Pillow** (Image handling)
- **ReportLab** (PDF generation)

## 📦 Installation

### Prerequisites
- Python 3.8+
- MySQL 5.7+
- pip

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fleetflow
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and settings
   ```

5. **Set up the database**
   ```bash
   # Create MySQL database
   mysql -u root -p
   CREATE DATABASE fleetflow;
   
   # Run migrations
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - Web Interface: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin

## 🗄 Database Schema

The application uses the following core tables:

- **users** - User accounts and authentication
- **vehicles** - Vehicle information and status
- **drivers** - Driver profiles and performance
- **trips** - Trip management and tracking
- **maintenance_logs** - Maintenance records
- **fuel_logs** - Fuel consumption data
- **expenses** - Expense tracking
- **analytics_reports** - Report generation

## 🎯 Usage

### Demo Credentials
- **Admin**: admin / admin123
- **Manager**: manager / manager123
- **Dispatcher**: dispatcher / dispatch123

### Getting Started

1. **Login** with your credentials
2. **Add Vehicles** to your fleet
3. **Register Drivers** in the system
4. **Create Trips** and assign vehicles/drivers
5. **Track Expenses** and fuel consumption
6. **Schedule Maintenance** as needed
7. **Generate Reports** for analysis

## 🔧 Configuration

### Environment Variables

Key environment variables in `.env`:

```bash
# Django Settings
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=fleetflow
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

## 📱 API Endpoints

The system provides REST API endpoints for mobile integration:

- `/api/vehicles/` - Vehicle management
- `/api/drivers/` - Driver management
- `/api/trips/` - Trip operations
- `/api/fuel-logs/` - Fuel tracking
- `/api/expenses/` - Expense management

## 🔒 Security Features

- Role-based access control
- Session authentication
- CSRF protection
- SQL injection prevention
- XSS protection
- Secure password hashing

## 📊 Reporting

The system supports various report types:

- **Trip Summary Reports**
- **Vehicle Performance Reports**
- **Driver Performance Reports**
- **Fuel Consumption Reports**
- **Maintenance Reports**
- **Financial Reports**

Reports can be exported in:
- PDF format
- Excel spreadsheets
- CSV files

## 🚀 Deployment

### Production Deployment

1. **Set environment variables** for production
2. **Configure static file serving**
3. **Set up database** with proper credentials
4. **Configure email backend**
5. **Enable HTTPS**
6. **Set up monitoring and logging**

### Docker Deployment

```bash
# Build Docker image
docker build -t fleetflow .

# Run with Docker Compose
docker-compose up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🔄 Updates

The system is regularly updated with:
- New features and improvements
- Security patches
- Performance optimizations
- Bug fixes

---

**FleetFlow** - Streamlining Fleet Management for Modern Businesses
