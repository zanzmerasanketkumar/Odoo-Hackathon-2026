from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db.models import Avg, Count, Q
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
import csv
import io
from datetime import datetime, timedelta
from .models import Student, Attendance, Performance, TerminatedStudent
from .forms import StudentForm, AttendanceForm, PerformanceForm


def admin_login(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    
    return render(request, 'admin_login.html')


def fix_email_mismatches(request):
    """Utility view to fix email ID mismatches in database"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('admin_login')
    
    if request.method == 'POST':
        try:
            fixed_count = Student.fix_email_id_mismatches()
            messages.success(request, f'Fixed {fixed_count} student email ID mismatches.')
        except Exception as e:
            messages.error(request, f'Error fixing mismatches: {str(e)}')
    
    return render(request, 'admin/fix_mismatches.html')


def admin_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('admin_login')


@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('admin_login')
    
    total_students = Student.objects.count()
    total_attendance_today = Attendance.objects.filter(date=timezone.now().date()).count()
    recent_students = Student.objects.order_by('-created_at')[:5]
    
    # Additional admin statistics
    total_attendance_records = Attendance.objects.count()
    total_performance_records = Performance.objects.count()
    terminated_students_count = TerminatedStudent.objects.filter(is_restored=False).count()
    
    # Program-wise student count
    program_stats = Student.objects.values('program').annotate(count=Count('id'))
    
    context = {
        'total_students': total_students,
        'total_attendance_today': total_attendance_today,
        'recent_students': recent_students,
        'total_attendance_records': total_attendance_records,
        'total_performance_records': total_performance_records,
        'terminated_students_count': terminated_students_count,
        'program_stats': program_stats,
    }
    return render(request, 'admin_dashboard.html', context)


def student_list(request):
    students = Student.objects.all().order_by('-student_id')
    return render(request, 'students/student_list.html', {'students': students})


def student_update(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('admin_login')
    
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            try:
                updated_student = form.save()
                messages.success(request, f'Student {updated_student.full_name} updated successfully!')
                return redirect('student_detail', pk=updated_student.pk)
            except Exception as e:
                # Handle specific duplicate email error
                error_str = str(e)
                if 'Duplicate entry' in error_str and 'email_id' in error_str:
                    # Extract the email from the error message to check if it's a real duplicate
                    import re
                    email_match = re.search(r"'([^']*)' for key 'students_student\.email_id'", error_str)
                    if email_match:
                        duplicate_email = email_match.group(1)
                        # Check if this email actually exists in the database (excluding current student)
                        from .models import Student
                        if Student.objects.filter(email_id=duplicate_email).exclude(pk=student.pk).exists():
                            form.add_error(None, f'The email {duplicate_email} is already registered to another student.')
                            messages.error(request, f'Student update failed: Email {duplicate_email} already exists in the system.')
                        else:
                            # This might be a system error, not a real duplicate
                            messages.error(request, f'Student update failed: System error occurred. Please try again.')
                    else:
                        form.add_error(None, 'Email address conflict detected. Please try again.')
                        messages.error(request, 'Failed to update student: Email conflict occurred.')
                else:
                    messages.error(request, f'Failed to update student: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StudentForm(instance=student)
    
    return render(request, 'students/student_form_detailed.html', {'form': form, 'title': 'Update Student', 'student': student})


def student_delete(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('admin_login')
    
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        termination_reason = request.POST.get('termination_reason', 'No reason provided')
        
        # Create backup record in TerminatedStudent
        terminated_student = TerminatedStudent.objects.create(
            original_student_id=student.student_id,
            first_name=student.first_name,
            last_name=student.last_name,
            date_of_birth=student.date_of_birth,
            gender=student.gender,
            phone_number=student.phone_number,
            personal_email=student.personal_email,
            address=student.address,
            city=student.city,
            state=student.state,
            postal_code=student.postal_code,
            country=student.country,
            program=student.program,
            semester=student.semester,
            blood_group=student.blood_group,
            emergency_contact_name=student.emergency_contact_name,
            emergency_contact_relation=student.emergency_contact_relation,
            emergency_contact_phone=student.emergency_contact_phone,
            email_id=student.email_id,
            admission_year=student.admission_year,
            termination_reason=termination_reason,
            terminated_by=request.user,
            created_at=student.created_at,
            updated_at=student.updated_at,
        )
        
        # Delete the original student
        student_name = student.full_name
        student.delete()
        
        messages.success(request, f'Student {student_name} has been terminated and backed up successfully! Reason: {termination_reason}')
        return redirect('student_list')
    
    return render(request, 'students/student_confirm_delete.html', {'student': student})


def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            try:
                student = form.save()
                messages.success(request, f'Student {student.full_name} created successfully!')
                return redirect('student_detail', pk=student.pk)
            except Exception as e:
                # Handle specific duplicate email error
                error_str = str(e)
                if 'Duplicate entry' in error_str and 'email_id' in error_str:
                    # Extract the email from the error message to check if it's a real duplicate
                    import re
                    email_match = re.search(r"'([^']*)' for key 'students_student\.email_id'", error_str)
                    if email_match:
                        duplicate_email = email_match.group(1)
                        # Check if this email actually exists in the database
                        from .models import Student
                        if Student.objects.filter(email_id=duplicate_email).exists():
                            form.add_error(None, f'The email {duplicate_email} is already registered to another student.')
                            messages.error(request, f'Student creation failed: Email {duplicate_email} already exists in the system.')
                        else:
                            # This might be a system error, not a real duplicate
                            messages.error(request, f'Student creation failed: System error occurred. Please try again.')
                    else:
                        form.add_error(None, 'Email address conflict detected. Please try again.')
                        messages.error(request, 'Failed to create student: Email conflict occurred.')
                else:
                    messages.error(request, f'Failed to create student: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StudentForm()
    return render(request, 'students/student_form_detailed.html', {'form': form, 'title': 'Add Student'})


def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    
    attendance_data = student.attendances.all().order_by('-date')
    total_classes = attendance_data.count()
    present_classes = attendance_data.filter(is_present=True).count()
    absent_classes = total_classes - present_classes
    attendance_percentage = (present_classes / total_classes * 100) if total_classes > 0 else 0
    
    performances = student.performances.all().order_by('-exam_date')
    average_marks = performances.aggregate(Avg('marks_obtained'))['marks_obtained__avg'] or 0
    
    context = {
        'student': student,
        'attendance_data': attendance_data,
        'total_classes': total_classes,
        'present_classes': present_classes,
        'absent_classes': absent_classes,
        'attendance_percentage': attendance_percentage,
        'performances': performances,
        'average_marks': round(average_marks, 2),
    }
    return render(request, 'students/student_detail.html', context)


def attendance_history(request, student_id):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('admin_login')
    
    student = get_object_or_404(Student, pk=student_id)
    
    # Get all attendance records for this student
    attendance_records = Attendance.objects.filter(student=student).order_by('-date')
    
    # Calculate statistics
    total_classes = attendance_records.count()
    present_classes = attendance_records.filter(is_present=True).count()
    absent_classes = total_classes - present_classes
    attendance_percentage = (present_classes / total_classes * 100) if total_classes > 0 else 0
    
    context = {
        'student': student,
        'attendance_records': attendance_records,
        'total_classes': total_classes,
        'present_classes': present_classes,
        'absent_classes': absent_classes,
        'attendance_percentage': round(attendance_percentage, 1),
    }
    return render(request, 'attendance/attendance_history.html', context)


def attendance_edit(request, student_id):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('admin_login')
    
    student = get_object_or_404(Student, pk=student_id)
    
    # Get date from query parameter
    date_param = request.GET.get('date')
    if not date_param:
        messages.error(request, 'Date parameter is required.')
        return redirect('attendance_management')
    
    try:
        selected_date = datetime.strptime(date_param, '%Y-%m-%d').date()
    except ValueError:
        messages.error(request, 'Invalid date format. Please use YYYY-MM-DD format.')
        return redirect('attendance_management')
    
    # Get existing attendance for this student and date
    try:
        attendance = Attendance.objects.get(student=student, date=selected_date)
    except Attendance.DoesNotExist:
        attendance = None
    
    if request.method == 'POST':
        is_present = request.POST.get('is_present') == 'true'
        
        if attendance:
            attendance.is_present = is_present
            attendance.save()
            messages.success(request, f'Attendance updated for {student.full_name} on {selected_date}')
        else:
            Attendance.objects.create(
                student=student,
                date=selected_date,
                is_present=is_present
            )
            messages.success(request, f'Attendance marked for {student.full_name} on {selected_date}')
        
        return redirect('attendance_management')
    
    context = {
        'student': student,
        'selected_date': selected_date,
        'attendance': attendance,
    }
    return render(request, 'attendance/attendance_edit.html', context)


def attendance_management(request):
    # Group students by batch (program + admission year)
    students = Student.objects.all().order_by('program', 'admission_year', 'student_id')
    batches = {}
    
    for student in students:
        batch_key = f"{student.program}{student.admission_year}"
        batch_name = f"{student.get_program_display()} {student.admission_year}"
        
        if batch_key not in batches:
            batches[batch_key] = {
                'code': batch_key,
                'name': batch_name,
                'program': student.program,
                'year': student.admission_year,
                'count': 0
            }
        batches[batch_key]['count'] += 1
    
    # Convert to list and sort by program and year
    batch_list = list(batches.values())
    batch_list.sort(key=lambda x: (x['program'], x['year']))
    
    # Get existing attendance for today (if available)
    today = timezone.now().date()
    existing_attendance = {}
    for attendance in Attendance.objects.filter(date=today):
        existing_attendance[attendance.student.pk] = attendance.is_present
    
    if request.method == 'POST':
        date = request.POST.get('date')
        if not date:
            messages.error(request, 'Please select a date')
            return redirect('attendance_management')
        
        selected_date = datetime.strptime(date, '%Y-%m-%d').date()
        students = Student.objects.all()
        
        for student in students:
            attendance_key = f'attendance_{student.pk}'
            is_present = request.POST.get(attendance_key) == 'present'
            
            Attendance.objects.update_or_create(
                student=student,
                date=selected_date,
                defaults={'is_present': is_present}
            )
        
        messages.success(request, f'Attendance for {selected_date} has been marked successfully!')
        return redirect('attendance_management')
    
    context = {
        'students': students,
        'batches': batch_list,
        'existing_attendance': existing_attendance
    }
    return render(request, 'attendance/attendance_management.html', context)


def performance_management(request):
    if request.method == 'POST':
        form = PerformanceForm(request.POST)
        if form.is_valid():
            performance = form.save()
            messages.success(request, f'Performance record for {performance.student.name} added successfully!')
            return redirect('student_detail', pk=performance.student.pk)
    else:
        form = PerformanceForm()
    
    performances = Performance.objects.all().order_by('-exam_date')
    return render(request, 'performance/performance_management.html', {
        'form': form,
        'performances': performances
    })


def student_report_csv(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('admin_login')
    
    student = get_object_or_404(Student, pk=pk)
    
    # Get attendance data - get only the latest record for each date
    all_attendance = student.attendances.all().order_by('-date', '-created_at')
    
    # Group by date and get the latest record for each date
    latest_attendance = {}
    for attendance in all_attendance:
        if attendance.date not in latest_attendance:
            latest_attendance[attendance.date] = attendance
    
    # Convert back to list ordered by date
    attendance_data = list(latest_attendance.values())
    attendance_data.sort(key=lambda x: x.date, reverse=True)
    
    total_classes = len(attendance_data)
    present_classes = sum(1 for attendance in attendance_data if attendance.is_present)
    absent_classes = total_classes - present_classes
    attendance_percentage = (present_classes / total_classes * 100) if total_classes > 0 else 0
    
    performances = student.performances.all().order_by('-exam_date')
    average_marks = performances.aggregate(Avg('marks_obtained'))['marks_obtained__avg'] or 0
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="student_report_{student.student_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    
    # Header row - all student information horizontally
    header_row = [
        'Student ID', 'Full Name', 'Program', 'Semester', 'Gender', 'Date of Birth',
        'Phone Number', 'Email ID', 'Admission Year', 'Total Classes', 'Present Classes',
        'Absent Classes', 'Attendance %', 'Attendance Status', 'Total Exams',
        'Average Marks', 'Good Performance', 'Average Performance', 'Needs Improvement'
    ]
    writer.writerow(header_row)
    
    # Student data row - all information horizontally
    student_row = [
        student.student_id,
        student.full_name,
        student.get_program_display(),
        student.get_semester_display(),
        student.get_gender_display(),
        student.date_of_birth.strftime('%Y-%m-%d'),
        student.phone_number,
        student.email_id,
        student.admission_year,
        total_classes,
        present_classes,
        absent_classes,
        f'{attendance_percentage:.2f}%',
        'Good' if attendance_percentage >= 75 else 'Needs Attention',
        performances.count(),
        f'{average_marks:.2f}',
        sum(1 for p in performances if p.remark == 'Good'),
        sum(1 for p in performances if p.remark == 'Average'),
        sum(1 for p in performances if p.remark == 'Needs Improvement')
    ]
    writer.writerow(student_row)
    
    # Add empty row for separation
    writer.writerow([])
    
    # Detailed attendance records vertically (correct format)
    if attendance_data:
        writer.writerow([])
        writer.writerow(['Attendance Records'])
        writer.writerow(['Date', 'Status', 'Marked On'])
        for attendance in attendance_data:
            writer.writerow([
                attendance.date.strftime('%Y-%m-%d'),
                'Present' if attendance.is_present else 'Absent',
                attendance.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
    
    # Detailed performance records horizontally
    if performances.exists():
        writer.writerow([])
        writer.writerow(['Performance Records (Exam Date, Subject, Marks, Total, %, Remark)'])
        
        # Group performance records in rows of 2 records per line
        performance_records = []
        for performance in performances:
            percentage = (performance.marks_obtained / performance.total_marks * 100) if performance.total_marks > 0 else 0
            performance_records.extend([
                performance.exam_date.strftime('%Y-%m-%d'),
                performance.subject,
                str(performance.marks_obtained),
                str(performance.total_marks),
                f'{percentage:.2f}%',
                performance.remark
            ])
        
        # Write performance data in chunks of 12 (2 records × 6 columns)
        for i in range(0, len(performance_records), 12):
            writer.writerow(performance_records[i:i+12])
    
    return response


def all_students_csv(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('admin_login')
    
    # Get all students
    students = Student.objects.all().order_by('student_id')
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="all_students_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    
    # Header row - all student information horizontally
    header_row = [
        'Student ID', 'Full Name', 'Program', 'Semester', 'Gender', 'Date of Birth',
        'Phone Number', 'Email ID', 'Admission Year', 'Total Classes', 'Present Classes',
        'Absent Classes', 'Attendance %', 'Average Marks', 'Performance Status'
    ]
    writer.writerow(header_row)
    
    # Write student data horizontally
    for student in students:
        # Get attendance data - get only the latest record for each date
        all_attendance = student.attendances.all().order_by('-date', '-created_at')
        
        # Group by date and get the latest record for each date
        latest_attendance = {}
        for attendance in all_attendance:
            if attendance.date not in latest_attendance:
                latest_attendance[attendance.date] = attendance
        
        # Convert back to list
        attendance_data = list(latest_attendance.values())
        
        total_classes = len(attendance_data)
        present_classes = sum(1 for attendance in attendance_data if attendance.is_present)
        attendance_percentage = (present_classes / total_classes * 100) if total_classes > 0 else 0
        
        # Get performance data
        performances = student.performances.all()
        average_marks = performances.aggregate(Avg('marks_obtained'))['marks_obtained__avg'] or 0
        
        # Determine performance status
        if average_marks >= 80:
            performance_status = 'Excellent'
        elif average_marks >= 60:
            performance_status = 'Good'
        elif average_marks >= 40:
            performance_status = 'Average'
        else:
            performance_status = 'Needs Improvement'
        
        # Student data row - all information horizontally
        student_row = [
            student.student_id,
            student.full_name,
            student.get_program_display(),
            student.get_semester_display(),
            student.get_gender_display(),
            student.date_of_birth.strftime('%Y-%m-%d'),
            student.phone_number,
            student.email_id,
            student.admission_year,
            total_classes,
            present_classes,
            total_classes - present_classes,
            f'{attendance_percentage:.2f}%',
            f'{average_marks:.2f}',
            performance_status
        ]
        writer.writerow(student_row)
    
    return response


def attendance_csv(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('admin_login')
    
    # Get date filter from request
    date_filter = request.GET.get('date')
    program_filter = request.GET.get('program')
    
    # Build query
    attendances = Attendance.objects.all().order_by('-date')
    
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            attendances = attendances.filter(date=filter_date)
        except ValueError:
            pass
    
    if program_filter:
        attendances = attendances.filter(student__program=program_filter)
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    filename = f"attendance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    if date_filter:
        filename = f"attendance_{date_filter}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    
    # Header row - all attendance information horizontally
    header_row = [
        'Date', 'Student ID', 'Student Name', 'Program', 'Semester', 'Status', 'Marked On'
    ]
    writer.writerow(header_row)
    
    # Write attendance data horizontally
    for attendance in attendances:
        attendance_row = [
            attendance.date.strftime('%Y-%m-%d'),
            attendance.student.student_id,
            attendance.student.full_name,
            attendance.student.get_program_display(),
            attendance.student.get_semester_display(),
            'Present' if attendance.is_present else 'Absent',
            attendance.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ]
        writer.writerow(attendance_row)
    
    return response


def student_report(request, pk):
    student = get_object_or_404(Student, pk=pk)
    
    # Get attendance data - get only the latest record for each date
    attendance_data = student.attendances.all().order_by('-date', '-created_at')
    
    # Group by date and get the latest record for each date
    latest_attendance = {}
    for attendance in attendance_data:
        if attendance.date not in latest_attendance:
            latest_attendance[attendance.date] = attendance
    
    # Convert back to queryset-like list ordered by date
    attendance_data = list(latest_attendance.values())
    attendance_data.sort(key=lambda x: x.date, reverse=True)
    
    total_classes = len(attendance_data)
    present_classes = sum(1 for attendance in attendance_data if attendance.is_present)
    absent_classes = total_classes - present_classes
    attendance_percentage = (present_classes / total_classes * 100) if total_classes > 0 else 0
    
    performances = student.performances.all().order_by('-exam_date')
    average_marks = performances.aggregate(Avg('marks_obtained'))['marks_obtained__avg'] or 0
    
    # Calculate performance counts using remark property
    good_count = sum(1 for p in performances if p.remark == 'Good')
    average_count = sum(1 for p in performances if p.remark == 'Average')
    needs_improvement_count = sum(1 for p in performances if p.remark == 'Needs Improvement')
    
    attendance_warning = attendance_percentage < 75
    
    context = {
        'student': student,
        'attendance_data': attendance_data,
        'total_classes': total_classes,
        'present_classes': present_classes,
        'absent_classes': absent_classes,
        'attendance_percentage': attendance_percentage,
        'performances': performances,
        'average_marks': round(average_marks, 2),
        'attendance_warning': attendance_warning,
        'good_count': good_count,
        'average_count': average_count,
        'needs_improvement_count': needs_improvement_count,
    }
    return render(request, 'reports/student_report.html', context)


def terminated_students_list(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('admin_login')
    
    terminated_students = TerminatedStudent.objects.filter(is_restored=False).order_by('-termination_date')
    return render(request, 'students/terminated_students_list.html', {'terminated_students': terminated_students})


def restore_student(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('admin_login')
    
    terminated_student = get_object_or_404(TerminatedStudent, pk=pk)
    
    if terminated_student.is_restored:
        messages.error(request, 'This student has already been restored.')
        return redirect('terminated_students_list')
    
    if request.method == 'POST':
        try:
            restored_student = terminated_student.restore_student(request.user)
            messages.success(request, f'Student {restored_student.full_name} has been restored successfully!')
            return redirect('student_detail', pk=restored_student.pk)
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error restoring student: {str(e)}')
    
    return render(request, 'students/restore_student_confirm.html', {'terminated_student': terminated_student})


def terminated_student_detail(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('admin_login')
    
    terminated_student = get_object_or_404(TerminatedStudent, pk=pk)
    return render(request, 'students/terminated_student_detail.html', {'terminated_student': terminated_student})
