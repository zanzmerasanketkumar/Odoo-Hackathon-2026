from django.db import models
from django.utils import timezone
import datetime

class Student(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    
    PROGRAM_CHOICES = [
        ('MCA', 'Master of Computer Applications'),
        ('MScIT', 'Master of Science in Information Technology'),
        ('BCA', 'Bachelor of Computer Applications'),
        ('PGDCA', 'Post Graduate Diploma in Computer Applications'),
    ]
    
    SEMESTER_CHOICES = [
        (1, 'Semester 1'),
        (2, 'Semester 2'),
        (3, 'Semester 3'),
        (4, 'Semester 4'),
        (5, 'Semester 5'),
        (6, 'Semester 6'),
    ]
    
    # Basic Information
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    
    # Contact Information
    phone_number = models.CharField(max_length=15, help_text="Include country code")
    personal_email = models.EmailField(max_length=100, help_text="Personal email address")
    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=50, default='India')
    
    # Academic Information
    program = models.CharField(max_length=10, choices=PROGRAM_CHOICES)
    semester = models.IntegerField(choices=SEMESTER_CHOICES)
    
    # Physical Information
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True, null=True)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_relation = models.CharField(max_length=50)
    emergency_contact_phone = models.CharField(max_length=15)
    
    # System Generated Fields
    student_id = models.CharField(max_length=10, unique=True, editable=False)
    email_id = models.EmailField(max_length=50, unique=True, editable=False)
    admission_year = models.IntegerField(editable=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-student_id']
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def name(self):
        return self.full_name
    
    def __str__(self):
        return f"{self.full_name} ({self.student_id})"
    
    def save(self, *args, **kwargs):
        if not self.student_id:
            self.student_id = self.generate_student_id()
            self.admission_year = datetime.datetime.now().year
        
        # Always ensure email_id matches the student_id
        self.email_id = self.generate_email_id()
        
        super().save(*args, **kwargs)
    
    def generate_student_id(self):
        # Use current year dynamically (changes every year)
        current_year = datetime.datetime.now().year
        year_suffix = str(current_year)[-2:]
        
        program_codes = {
            'MCA': 1001,    # Changed from 101 to 1001
            'MScIT': 2001,   # Changed from 201 to 2001
            'BCA': 3001,     # Changed from 301 to 3001
            'PGDCA': 4001,    # Changed from 401 to 4001
        }
        
        base_code = program_codes.get(self.program, 1001)
        
        last_student = Student.objects.filter(
            program=self.program,
            admission_year=current_year
        ).order_by('-student_id').first()
        
        if last_student:
            last_number = int(last_student.student_id[-3:])
            new_number = last_number + 1
        else:
            new_number = 0  # Changed from 1 to 0
        
        return f"{year_suffix}{base_code + new_number:03d}"
    
    def generate_email_id(self):
        return f"{self.student_id}.gvp@gujaratvidyapith.org"
    
    def clean(self):
        # Ensure email_id matches student_id
        expected_email = self.generate_email_id()
        if self.email_id != expected_email:
            self.email_id = expected_email
    
    @classmethod
    def fix_email_id_mismatches(cls):
        """Fix all students where email_id doesn't match student_id"""
        mismatches = cls.objects.raw("""
            SELECT s.id, s.student_id, s.email_id 
            FROM students_student s 
            WHERE s.email_id != CONCAT(s.student_id, '.gvp@gujaratvidyapith.org')
        """)
        
        fixed_count = 0
        for student in mismatches:
            student_obj = cls.objects.get(id=student.id)
            student_obj.email_id = student_obj.generate_email_id()
            student_obj.save(update_fields=['email_id'])
            fixed_count += 1
        
        return fixed_count


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    is_present = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.student.name} - {self.date} - {'Present' if self.is_present else 'Absent'}"


class Performance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='performances')
    subject = models.CharField(max_length=100)
    marks_obtained = models.IntegerField()
    total_marks = models.IntegerField(default=100)
    exam_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-exam_date']
    
    def __str__(self):
        return f"{self.student.name} - {self.subject} - {self.marks_obtained}/{self.total_marks}"
    
    @property
    def percentage(self):
        if self.total_marks > 0:
            return round((self.marks_obtained / self.total_marks) * 100, 2)
        return 0
    
    @property
    def remark(self):
        percentage = self.percentage
        if percentage >= 75:
            return "Good"
        elif percentage >= 50:
            return "Average"
        else:
            return "Needs Improvement"


class TerminatedStudent(models.Model):
    """Model to store backup of deleted/terminated students for potential restoration"""
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    
    PROGRAM_CHOICES = [
        ('MCA', 'Master of Computer Applications'),
        ('MScIT', 'Master of Science in Information Technology'),
        ('BCA', 'Bachelor of Computer Applications'),
        ('PGDCA', 'Post Graduate Diploma in Computer Applications'),
    ]
    
    SEMESTER_CHOICES = [
        (1, 'Semester 1'),
        (2, 'Semester 2'),
        (3, 'Semester 3'),
        (4, 'Semester 4'),
        (5, 'Semester 5'),
        (6, 'Semester 6'),
    ]
    
    # Original student data (all fields from Student model)
    original_student_id = models.CharField(max_length=10, help_text="Original student ID")
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=15)
    personal_email = models.EmailField(max_length=100)
    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=50, default='India')
    program = models.CharField(max_length=10, choices=PROGRAM_CHOICES)
    semester = models.IntegerField(choices=SEMESTER_CHOICES)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_relation = models.CharField(max_length=50)
    emergency_contact_phone = models.CharField(max_length=15)
    email_id = models.EmailField(max_length=50)
    admission_year = models.IntegerField()
    
    # Deletion/termination specific fields
    termination_reason = models.TextField(help_text="Reason for student termination/deletion")
    termination_date = models.DateTimeField(auto_now_add=True)
    terminated_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, help_text="Admin who terminated the student")
    
    # Original timestamps
    created_at = models.DateTimeField(help_text="Original student creation date")
    updated_at = models.DateTimeField(help_text="Original student last update date")
    
    # Additional metadata
    is_restored = models.BooleanField(default=False, help_text="Whether this student has been restored")
    restored_date = models.DateTimeField(null=True, blank=True, help_text="Date when student was restored")
    restored_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='restored_students', help_text="Admin who restored the student")
    
    class Meta:
        ordering = ['-termination_date']
        verbose_name = "Terminated Student"
        verbose_name_plural = "Terminated Students"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def name(self):
        return self.full_name
    
    def __str__(self):
        return f"{self.full_name} ({self.original_student_id}) - Terminated on {self.termination_date.strftime('%Y-%m-%d')}"
    
    def restore_student(self, restored_by_user):
        """Restore this terminated student back to active students"""
        if self.is_restored:
            raise ValueError("This student has already been restored")
        
        # Check if the original student_id or email_id already exists in active students
        if Student.objects.filter(student_id=self.original_student_id).exists():
            raise ValueError(f"Student ID {self.original_student_id} already exists in active students")
        
        if Student.objects.filter(email_id=self.email_id).exists():
            raise ValueError(f"Email ID {self.email_id} already exists in active students")
        
        # Create new student record
        student = Student.objects.create(
            first_name=self.first_name,
            last_name=self.last_name,
            date_of_birth=self.date_of_birth,
            gender=self.gender,
            phone_number=self.phone_number,
            personal_email=self.personal_email,
            address=self.address,
            city=self.city,
            state=self.state,
            postal_code=self.postal_code,
            country=self.country,
            program=self.program,
            semester=self.semester,
            blood_group=self.blood_group,
            emergency_contact_name=self.emergency_contact_name,
            emergency_contact_relation=self.emergency_contact_relation,
            emergency_contact_phone=self.emergency_contact_phone,
            student_id=self.original_student_id,
            email_id=self.email_id,
            admission_year=self.admission_year,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
        
        # Mark this record as restored
        self.is_restored = True
        self.restored_date = timezone.now()
        self.restored_by = restored_by_user
        self.save(update_fields=['is_restored', 'restored_date', 'restored_by'])
        
        return student
