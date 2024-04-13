
from datetime import datetime
import json
from time import strptime
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from result_module.models import (

    Announcement,
    AnnouncementForStudents,
    Attendance,
    AttendanceReport,
    ClassAttendance,
    CustomUser,
    ExamMetrics,
    FeedBackStudent,
    LeaveReportStudent,
    StudentClassAttendance,
   
    Students, 
    Subject,
    ExamType,
    Result,
    StudentExamInfo,
    StudentPositionInfo,

)
from result_module.templatetags.custom_filters import strftime

def student_dologin(request):
    if request.method == 'POST':
        registration_number = request.POST.get('registration_number')
        first_name = request.POST.get('first_name')

        try:
            student = Students.objects.get(registration_number=registration_number, full_name=first_name)
            if student.is_active:
                # Set session variable to track logged-in student
                request.session['student_id'] = student.id                
                # Redirect to student home page (replace 'student_home' with the actual URL name)
                return redirect('student_home')
            else:
                messages.error(request, 'This student is not active.')
        except Students.DoesNotExist:
            messages.error(request, 'Invalid registration number or first name.')

    return render(request, 'student_template/student_login.html')


def student_login(request):  
  return render(request,'student_template/student_login.html')


def student_announcements(request):
    student_id = request.session.get('student_id')
    if student_id:
        try:
            student = Students.objects.get(id=student_id)
            announcements = Announcement.objects.filter(current_class=student.current_class)
            
            # Mark announcements as read for the logged-in student
            unread_announcements = AnnouncementForStudents.objects.filter(student=student, read=False)
            for announcement in unread_announcements:
                announcement.read = True
                announcement.save()

            return render(request, 'student_template/student_announcements.html', {'announcements': announcements,'student':student})
        except Students.DoesNotExist:
            return HttpResponseBadRequest("Student does not exist")
    else:
        return HttpResponseBadRequest("Unauthorized access")



def fetch_unread_announcement_count(request):
    student_id = request.session.get('student_id')
    if student_id:
        try:
            student = Students.objects.get(pk=student_id)
            announcements = Announcement.objects.filter(current_class=student.current_class)
            unread_count = 0
            
            for announcement in announcements:
                # Check if the announcement exists for the student
                if not AnnouncementForStudents.objects.filter(announcement=announcement, student=student).exists():
                    # If the announcement doesn't exist, create a new entry
                    AnnouncementForStudents.objects.create(announcement=announcement, student=student)
                    unread_count += 1
                elif not AnnouncementForStudents.objects.get(announcement=announcement, student=student).read:
                    # If the announcement exists but is unread, increment the count
                    unread_count += 1
                    
            return JsonResponse({'unread_count': unread_count})
        except Students.DoesNotExist:
            pass
    
    return JsonResponse({'error': 'Unauthorized'}, status=401)


def single_student_details(request):
    # Retrieve logged-in student's ID from session variable
    student_id = request.session.get('student_id')
    if student_id:
        try:
            # Fetch the logged-in student's information
            student = Students.objects.get(id=student_id)       
            context = {
                'student': student,
               
            }
            return render(request, "student_template/student_details.html", context)
        except Students.DoesNotExist:
            messages.error(request, 'Student not found.')
    else:
        messages.error(request, 'Please log in to view student details.')

    # Redirect to login page if not logged in or if student not found
    return redirect('student_login')


def student_subject_wise_result_pages(request):
    # Retrieve logged-in student's ID from session variable
    student_id = request.session.get('student_id')
    if student_id:
        try:
            # Fetch the logged-in student's information
            student = Students.objects.get(id=student_id)

            # Fetch exam types and distinct exam dates
            exam_types = ExamType.objects.all()
            distinct_dates = Result.objects.filter().order_by('date_of_exam').values_list('date_of_exam', flat=True).distinct()
            print(distinct_dates)
            return render(request, 'student_template/subject_wise_results.html', {
                'student': student,
                'exam_types': exam_types,
                'distinct_dates': distinct_dates,
            })
        except Students.DoesNotExist:
            messages.error(request, 'Student not found.')
    else:
        messages.error(request, 'Please log in to view results.')
    # Redirect to login page if not logged in or if student not found
    return redirect('student_login')
    
def students_subject_wise_results(request):
    if request.method == 'POST' and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        # Get the student based on the provided student_id
        student_id = request.POST.get('student_id')
        exam_type_id = request.POST.get('exam_type_id')
        year = request.POST.get('year')

        student = Students.objects.get(id=student_id)
        # Replace 'Students' with your actual student model
        
        form_i_students = Students.objects.filter(current_class=student.current_class)
        total_students = form_i_students.count()
        # Query the results for the specific student
        exam_type = get_object_or_404(ExamType, id=exam_type_id)

        results = Result.objects.filter(student=student, exam_type_id=exam_type,date_of_exam=year)
        exam_info = StudentExamInfo.objects.filter(
            student=student,
            exam_type=exam_type,
            selected_class=student.current_class
        ).first()

        # Retrieve the StudentPositionInfo for the specified student, exam type, and current class
        position_info = StudentPositionInfo.objects.filter(
            student=student,
            exam_type=exam_type,
            current_class=student.current_class
        ).first()
        
        exam_metrics, created = ExamMetrics.objects.get_or_create(
                    student=student,
                    exam_type=exam_type,
                    selected_class=student.current_class,
                )
        total_marks = exam_metrics.total_marks
        average = exam_metrics.average
        grademetrics = exam_metrics.grade
        remark = exam_metrics.remark    
        if exam_info:
            division = exam_info.division
            total_grade_points = exam_info.total_grade_points
        else:
            division = "Division Not Available"
            total_grade_points = "Total Grade Points Not Available"

        if position_info:
            position = position_info.position
        else:
            position = "Position Not Available"

        context = {
            'total_marks': total_marks,
            'average': average,
            'remark': remark,
            'grademetrics': grademetrics,
            'student': student,
            'results': results,
            "students": student,
            'exam_type': exam_type,
            'position': position,  # Add position to the context
            'division': division,  # Add position to the context
            'total_students': total_students,  # Add position to the context
            'total_grade_points': total_grade_points,  # Add total_grade_points to the context
        }
        html_result = render_to_string('student_template/student_result_table.html', context)
        return JsonResponse({'html_result': html_result})    


def student_home(request):
    # Get the student object using the student_id stored in the session
    student_id = request.session.get('student_id')
    if student_id:
        student_object = Students.objects.get(id=student_id)
    else:
        # Redirect to the student login page if not logged in
        return redirect('student_login')

    # Retrieve attendance data for the student
    attendance_present = AttendanceReport.objects.filter(student_id=student_object, status=True).count()
    attendance_absent = AttendanceReport.objects.filter(student_id=student_object, status=False).count()
    attendance_total = AttendanceReport.objects.filter(student_id=student_object).count()
    
    class_attendance_present = StudentClassAttendance.objects.filter(student=student_object, status=True).count()
    class_attendance_absent = StudentClassAttendance.objects.filter(student=student_object, status=False).count()
    class_attendance_total = StudentClassAttendance.objects.filter(student=student_object).count()

    # Get subject-related data
    subject_data = Subject.objects.all()
    subject_name = []
    data_present = []
    data_absent = []
    total_subjects_taken = Subject.objects.all().count()

    # Iterate over subjects to gather attendance data
    for subject in subject_data:
        attendance = Attendance.objects.filter(subject_id=subject.id)
        attendance_present_count = AttendanceReport.objects.filter(
            attendance_id__in=attendance, status=True, student_id=student_object.id
        ).count()
        attendance_absent_count = AttendanceReport.objects.filter(
            attendance_id__in=attendance, status=False, student_id=student_object.id
        ).count()
        subject_name.append(subject.subject_name)
        data_present.append(attendance_present_count)
        data_absent.append(attendance_absent_count)

    # Pass data to the template for rendering
    return render(
        request,
        "student_template/student_home.html",
        {
            "attendance_total": attendance_total,
            "attendance_present": attendance_present,
            "attendance_absent": attendance_absent,
            "class_attendance_present": class_attendance_present,
            "class_attendance_absent": class_attendance_absent,
            "class_attendance_total": class_attendance_total,
            "total_subjects_taken": total_subjects_taken,
            "subject_name": subject_name,
            "data_present": data_present,
            "data_absent": data_absent,         
            "student": student_object,  # Renamed 'students' to 'student'
        },
    )


def student_sendfeedback(request):
    # Check if the student is logged in
    student_id = request.session.get('student_id')
    if not student_id:
        # Redirect to the student login page if not logged in
        return redirect('student_login')
    # Get the student object using the student_id stored in the session
    student_obj = Students.objects.get(id=student_id)    
    # Retrieve feedback data for the student
    feedback_data = FeedBackStudent.objects.filter(student_id=student_obj)
    return render(request, "student_template/student_feedback.html", {"feedback_data": feedback_data, "student": student_obj})


def student_sendfeedback_save(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("student_sendfeedback"))    
    # Check if the student is logged in
    student_id = request.session.get('student_id')
    if not student_id:
        # Redirect to the student login page if not logged in
        return redirect('student_login')
    # Get the student object using the student_id stored in the session
    student_obj = Students.objects.get(id=student_id)    
    # Process the feedback submission
    feedback_msg = request.POST.get("feedback_msg") 
    try:           
        feedback_report = FeedBackStudent(student_id=student_obj, feedback=feedback_msg, feedback_reply="")
        feedback_report.save()
        messages.success(request, "Feedback successfully sent")
    except:
        messages.error(request, "Failed to send feedback")
    return HttpResponseRedirect(reverse("student_sendfeedback"))

def student_apply_leave(request):
    # Check if the student is logged in
    student_id = request.session.get('student_id')
    if not student_id:
        # Redirect to the student login page if not logged in
        return redirect('student_login')
    # Get the student object using the student_id stored in the session
    student_obj = Students.objects.get(id=student_id)    
    # Retrieve leave reports for the student
    student_leave_report = LeaveReportStudent.objects.filter(student_id=student_obj)    
    return render(request, "student_template/student_leave_template.html", {"student_leave_report": student_leave_report, "students": student_obj})


def student_apply_leave_save(request):
    # Check if the request method is POST
    if request.method != "POST":
        return HttpResponseRedirect(reverse("student_apply_leave"))    
    # Check if the student is logged in
    student_id = request.session.get('student_id')
    if not student_id:
        # Redirect to the student login page if not logged in
        return redirect('student_login')    
    # Get the student object using the student_id stored in the session
    student_obj = Students.objects.get(id=student_id)    
    # Retrieve form data
    leave_date = request.POST.get("leave_date")
    leave_msg = request.POST.get("leave_msg")    
    
    try:
        # Create a new leave report for the student
        leave_report = LeaveReportStudent(student_id=student_obj, leave_date=leave_date, leave_message=leave_msg, leave_status=0)
        leave_report.save()
        messages.success(request, "Leave application submitted successfully")
    except:
        messages.error(request, "Failed to submit leave application")
    
    return HttpResponseRedirect(reverse("student_apply_leave"))
        

def student_view_class_attendance(request):
    # Check if the student is logged in
    student_id = request.session.get('student_id')
    if not student_id:
        # Redirect to the student login page if not logged in
        return redirect('student_login')    
    # Get the student object using the student_id stored in the session
    student = Students.objects.get(id=student_id)    
    # Retrieve class attendance data
    attendances = ClassAttendance.objects.all()  
    
    # Assuming that the educational level is a ForeignKey in Students model
    current_class = student.current_class 
    
    return render(request, "student_template/student_view_class_attendance.html", {           
        "current_class": current_class,
        "student": student,
        "attendances": attendances,
    })
    
def student_view_subject_attendance(request):
    # Check if the student is logged in
    student_id = request.session.get('student_id')
    if not student_id:
        # Redirect to the student login page if not logged in
        return redirect('student_login')
    # Get the student object using the student_id stored in the session
    student = Students.objects.get(id=student_id)    
    # Retrieve all attendances and subjects
    attendances = Attendance.objects.all()
    subjects = Subject.objects.all()
    # Assuming that the educational level is a ForeignKey in Students model
    current_class = student.current_class 

    return render(request, "student_template/student_view_subject_attendance.html", {           
        "current_class": current_class,
        "student": student,
        "attendances": attendances,
        "subjects": subjects,
    })
    
@csrf_exempt
def student_class_attendance_data(request): 
    student_id = request.session.get('student_id') 
    date_id = request.POST.get("date")
    students = Students.objects.filter(id=student_id)   
    attendance = ClassAttendance.objects.filter(id=date_id)
    # Fetch attendance data for the given date and class
    attendance_data = StudentClassAttendance.objects.filter(
        attendance__in=attendance,
        student__in=students
    )
    
    # Serialize student data
    list_data = []
    for attendance in attendance_data:
        data_small = {"id": attendance.student.id, "name": attendance.student.full_name, "status": attendance.status}
        list_data.append(data_small)        
    # Return the serialized data as JSON response
    return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)


@csrf_exempt
def student_subject_attendance_data(request):  
    student_id = request.session.get('student_id') 
    date_id = request.POST.get("date")
    subject = request.POST.get("subject")    
    students = Students.objects.filter(id=student_id)   
    attendance = Attendance.objects.filter(id=date_id,subject_id=subject)
    # Fetch attendance data for the given date and class
    attendance_data = AttendanceReport.objects.filter(
        attendance_id__in=attendance,
        student_id__in=students
    )
    
    # Serialize student data
    list_data = []
    for attendance in attendance_data:
        data_small = {"id": attendance.student_id.id, "name": attendance.student_id.full_name, "status": attendance.status}
        list_data.append(data_small)        
    # Return the serialized data as JSON response
    return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)        