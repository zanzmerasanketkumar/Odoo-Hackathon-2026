# Smart Attendance & Performance Tracker

A comprehensive web-based academic management system built with Django for tracking student attendance, performance, and generating automated reports.

## 🎯 Project Overview

This system replaces traditional manual attendance registers and spreadsheets used in educational institutions. It provides centralized student data management, automated calculations, and intelligent insights for academic administration.

### Key Features
- **Secure Authentication**: Admin-only access with login system
- **Automated Student ID Generation**: Dynamic year-based ID creation
- **Email ID Auto-Generation**: Institutional email format
- **Attendance Management**: Daily attendance tracking with percentage calculations
- **Performance Tracking**: Subject-wise marks and automated remarks
- **Class-Based Management**: Filter students by program and admission year
- **CSV Export**: Generate reports in CSV format
- **Real-time Statistics**: Live attendance and performance summaries

## 🏗️ Technology Stack

| Component | Technology | Version |
|-----------|-------------|---------|
| **Backend** | Python Django | 4.2.7 |
| **Database** | MySQL | 8.0+ |
| **Frontend** | HTML5, CSS3, Bootstrap 5 | 5.3.0 |
| **JavaScript** | Vanilla JS (ES6+) | Modern |
| **Icons** | Font Awesome | 6.0.0 |
| **Database Driver** | mysqlclient | 2.2.0 |

### APIs & External Services Used
- **Bootstrap CDN**: CSS framework (https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/)
- **Font Awesome CDN**: Icon library (https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/)
- **No AI/ML APIs**: All logic is implemented in Python/Django
- **No External APIs**: Self-contained system

## 🗂️ Project Structure

```
attendance_tracker/
├── attendance_tracker/          # Django project settings
│   ├── settings.py             # Project configuration
│   ├── urls.py                 # Main URL routing
│   └── wsgi.py                 # WSGI configuration
├── students/                   # Main Django app
│   ├── models.py               # Database models
│   ├── views.py                # Business logic
│   ├── forms.py                # Django forms
│   ├── urls.py                 # App URL routing
│   └── admin.py                # Django admin
├── templates/                  # HTML templates
│   ├── base.html              # Base template
│   ├── admin/                 # Admin templates
│   ├── students/              # Student templates
│   └── attendance/            # Attendance templates
├── static/                     # Static files
│   ├── css/style.css          # Custom styles
│   └── js/script.js           # Custom JavaScript
├── manage.py                   # Django management script
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🗄️ Database Schema

### Core Models

#### Student Model
```python
class Student(models.Model):
    # Personal Information
    first_name, last_name, date_of_birth, gender
    phone_number, personal_email, address
    
    # Academic Information
    program, semester, admission_year
    student_id (Auto-generated), email_id (Auto-generated)
    
    # Emergency Contact
    emergency_contact_name, emergency_contact_phone
```

#### Attendance Model
```python
class Attendance(models.Model):
    student = ForeignKey(Student)
    date = DateField()
    is_present = BooleanField()
    created_at = DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'date']
```

#### Performance Model
```python
class Performance(models.Model):
    student = ForeignKey(Student)
    subject = CharField()
    marks_obtained = IntegerField()
    total_marks = IntegerField(default=100)
    exam_date = DateField()
```

## 🔐 Authentication System

### Default Credentials
- **Username**: `admin`
- **Password**: `admin123`

### Security Features
- Django's built-in authentication system
- CSRF protection
- Session management
- Login required for all views
- Admin-only access control

## 🎓 Student ID Generation Logic

### Format: `YY + Program Code + Sequence Number`

#### Program Codes
| Program | Code | Range |
|---------|------|-------|
| MCA     | 1001 | 1001-1999 |
| MScIT   | 2001 | 2001-2999 |
| BCA     | 3001 | 3001-3999 |
| PGDCA   | 4001 | 4001-4999 |

#### Examples
- **2026 MCA Student 1**: `261001`
- **2026 MScIT Student 1**: `262001`
- **2027 MCA Student 1**: `271001`

### Email ID Generation
**Format**: `{student_id}.gvp@gujaratvidyapith.org`

**Example**: `261001.gvp@gujaratvidyapith.org`

## 📊 Features & Functionality

### 1. Student Management
- Add new students with automatic ID/email generation
- View student lists with filtering options
- Update student information
- Delete student records

### 2. Attendance Management
- Class-based attendance marking
- Date-wise attendance tracking
- Real-time attendance statistics
- Edit existing attendance records
- View attendance history

### 3. Performance Management
- Add subject-wise marks
- Automatic percentage calculation
- AI-generated performance remarks:
  - ≥ 75%: "Good"
  - 50-74%: "Average" 
  - < 50%: "Needs Improvement"

### 4. Reporting System
- Individual student reports
- Class-wise attendance reports
- Performance summaries
- CSV export functionality

### 5. Class-Based Filtering
- Filter by program (MCA, MScIT, BCA, PGDCA)
- Filter by admission year
- "All Students" option for comprehensive view
- Dynamic student count display

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- MySQL 8.0+
- pip package manager

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd attendance_tracker
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

4. **Setup MySQL Database**
   ```sql
   CREATE DATABASE attendance_tracker;
   CREATE USER 'root'@'localhost' IDENTIFIED BY 'root';
   GRANT ALL PRIVILEGES ON attendance_tracker.* TO 'root'@'localhost';
   FLUSH PRIVILEGES;
   ```

5. **Configure Database Settings**
   Update `attendance_tracker/settings.py` with your MySQL credentials:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'attendance_tracker',
           'USER': 'root',
           'PASSWORD': 'root',
           'HOST': 'localhost',
           'PORT': '3306',
       }
   }
   ```

6. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   # Follow prompts to create admin user
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - URL: `http://localhost:8000`
   - Login with admin credentials

## 📱 User Interface

### Design Principles
- **Mobile-First**: Responsive design for all devices
- **Modern UI**: Bootstrap 5 with custom styling
- **Intuitive Navigation**: Clear menu structure
- **Visual Feedback**: Color-coded status indicators
- **Professional Look**: Enterprise-ready interface

### Key UI Components
- **Dashboard**: Overview statistics and quick actions
- **Student Cards**: Comprehensive student information display
- **Attendance Interface**: Checkbox-based attendance marking
- **Performance Tables**: Subject-wise marks display
- **Report Views**: Professional report layouts

## 🔧 Development & Deployment

### Development Environment
```bash
# Development server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic
```

### Production Deployment
- **Web Server**: Apache with mod_wsgi or Nginx with Gunicorn
- **Database**: MySQL 8.0+ with optimized settings
- **Static Files**: Serve via CDN or web server
- **Environment Variables**: Use for sensitive configuration
- **SSL Certificate**: Enable HTTPS for security

## 🧪 Testing

### Test Coverage
- Model validation tests
- View functionality tests
- Form validation tests
- Integration tests

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test students
```

## 📈 Performance Optimizations

### Database Optimizations
- Indexed foreign keys
- Optimized queries with select_related/prefetch_related
- Database connection pooling

### Frontend Optimizations
- Lazy loading of data
- Efficient JavaScript event handling
- Optimized CSS with minimal reflows
- Bootstrap CDN for faster loading

## 🔒 Security Considerations

### Implemented Security
- Django's built-in CSRF protection
- SQL injection prevention via ORM
- XSS protection with template escaping
- Secure session management
- Admin-only access control

### Security Best Practices
- Regular security updates
- Strong password policies
- HTTPS in production
- Environment variable usage for secrets
- Regular database backups

## 🔄 Maintenance & Updates

### Regular Tasks
- Database backups
- Security updates
- Log monitoring
- Performance monitoring
- User activity tracking

### Update Process
1. Backup database
2. Update dependencies
3. Run migrations
4. Test functionality
5. Deploy to production

## 🐛 Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Check MySQL service
sudo systemctl status mysql

# Check database exists
mysql -u root -p -e "SHOW DATABASES;"
```

#### Migration Issues
```bash
# Reset migrations (caution: deletes data)
python manage.py migrate students zero
python manage.py makemigrations students
python manage.py migrate
```

#### Static File Issues
```bash
# Collect static files
python manage.py collectstatic --noinput
```

## 📞 Support & Contact

### Getting Help
- Check the troubleshooting section
- Review Django documentation
- Verify database configuration
- Check logs for error messages

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

### Contribution Guidelines
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Code Standards
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add comments for complex logic
- Maintain consistent formatting

## 📊 Project Statistics

- **Total Lines of Code**: ~15,000+
- **Models**: 3 (Student, Attendance, Performance)
- **Views**: 15+ main views
- **Templates**: 20+ HTML templates
- **Database Tables**: 3 main tables
- **API Endpoints**: RESTful URLs for all operations

---

**Version**: 2.0.0  
**Last Updated**: February 2026  
**Framework**: Django 4.2.7  
**Database**: MySQL 8.0+  
**Python**: 3.8+  

**Developed with ❤️ for educational institutions**
