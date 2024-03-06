
from datetime import datetime
from time import strptime
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from result_module.models import (

    CustomUser,
   
    Students, 
    Subject,
    ExamType,
    Result,
    StudentExamInfo,
    StudentPositionInfo,

)
from result_module.templatetags.custom_filters import strftime


def student_home(request):
    # Retrieve logged-in student's ID from session variable
    student_id = request.session.get('student_id')

    if student_id:
        try:
            # Fetch the logged-in student's information
            student = Students.objects.get(id=student_id)
            
            # You can add additional logic here if needed
            
            return render(request, "student_template/student_home.html", {'student': student})
        except Students.DoesNotExist:
            messages.error(request, 'Student not found.')
    else:
        messages.error(request, 'Please log in to view student home.')

    # Redirect to login page if not logged in or if student not found
    return redirect('student_login')


def student_view_attendance(request):
    student = Students.objects.get(admin=request.user.id)
    subjects = student.subjects.all()  # Assuming subjects is the related_name of the ManyToManyField
    return render(request, "student_template/student_view_attendance.html", {"subjects": subjects,"students":student})





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

def  student_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    students = Students.objects.get(admin=user)
    return render(request,"student_template/student_profile.html",{"user":user,"students":students})  

@login_required
def student_profile_save(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        password = request.POST.get("password")
        address = request.POST.get("address")

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != "" and password is not None:
                customuser.set_password(password)
            customuser.save()

            students = Students.objects.get(admin=customuser.id)
            students.address = address
            students.save()

            messages.success(request, "Profile has been successfully edited")
        except:
            messages.error(request, "Editing of profile failed")

    return HttpResponseRedirect(reverse("student_profile"))





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
    
def student_subject_wise_results(request):
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

        results = Result.objects.filter(student=student, exam_type_id=exam_type)
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
            'student': student,
            'results': results,
            "students": student,
            'exam_type': exam_type,
            'position': position,  # Add position to the context
            'division': division,  # Add position to the context
            'total_students': total_students,  # Add position to the context
            'total_grade_points': total_grade_points,  # Add total_grade_points to the context
        }
        html_result = render_to_string('student_template/result_table.html', context)
        return JsonResponse({'html_result': html_result})    

 

