from collections import defaultdict
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import RequestContext
from django.urls import reverse
from django.views.decorators.http import require_POST
from result_module.models import CustomUser, ExamType, Result, StudentExamInfo, StudentPositionInfo, Students, Subject
from django.contrib import messages
from django.contrib.auth import logout,login
from result_module.emailBackEnd import EmailBackend
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
# Create your views here.

def dashboard(request):
    return render(request,"hod_template/home_content.html")

def ShowLogin(request):  
  return render(request,'login.html')

def  admin_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    return render(request,"hod_template/admin_profile.html",{"user":user})  

def edit_profile_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("admin_profile"))
    
    else:
       first_name = request.POST.get("first_name")
       last_name = request.POST.get("last_name")
       password = request.POST.get("password")
       try:           
          customuser = CustomUser.objects.get(id=request.user.id)
          customuser.first_name = first_name
          customuser.last_name = last_name
          if password!= "" and password!=None:
              customuser.set_password(password)     
                         
          customuser.save()
          messages.success(request,"profile is successfully edited")
          return HttpResponseRedirect(reverse("admin_profile"))
      
       except:
            messages.error(request,"editing  of profile  failed")
            return HttpResponseRedirect(reverse("admin_profile"))

def DoLogin(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not allowed</h2>")
    else:
        user = EmailBackend.authenticate(request, request.POST.get("email"), request.POST.get("password"))
        if user is not None:
            if not user.is_active:
                messages.error(request, "Your account is not active. Please contact the administrator for support.")
                return HttpResponseRedirect(reverse("login"))

            login(request, user)
            if user.user_type == "1":
                return HttpResponseRedirect(reverse("dashboard"))
            elif user.user_type == "2":
                return HttpResponseRedirect(reverse("dashboard"))             
            else:
                return HttpResponseRedirect(reverse("login"))
        else:
            messages.error(request, "Invalid Login Details")
            return HttpResponseRedirect(reverse("login"))
    

def manage_student(request):
    students = Students.objects.all()
    return render(request, 'hod_template/manage_student.html', {'students': students})

def student_subject_wise_result_page(request,student_id): 
    student = Students.objects.get(id=student_id)
    exam_types = ExamType.objects.all()
    distinct_dates= Result.objects.order_by('date_of_exam').values_list('date_of_exam', flat=True).distinct()
    return render(request, 'hod_template/subject_wise_results.html',
                  {
                      'student': student,
                      'exam_types': exam_types,
                      'distinct_dates': distinct_dates,
                   })

def manage_exam_type(request):
    exam_types = ExamType.objects.all()
    return render(request, 'hod_template/manage_exam_types.html', {'exam_types': exam_types})

def manage_subject(request):
    subjects = Subject.objects.all()
    return render(request, 'hod_template/manage_subject.html', {'subjects': subjects})

def manage_result(request):
    # Get all students, results, and subjects
    students = Students.objects.all()
    subjects = Subject.objects.all()

    # Initialize a dictionary to store results for each student
    student_results = defaultdict(dict)

    # Retrieve results for each student and subject
    for student in students:
        # Filter results for the current student
        student_results_queryset = Result.objects.filter(student=student)
        # Group results by subject
        for subject in subjects:
            # Get results for the current subject and student
            subject_results = student_results_queryset.filter(subject=subject)
            # Store the marks for the subject
            student_results[student][subject.subject_name] = [result.marks for result in subject_results]
    print(student_results)
    context = {
        'student_results': student_results,
    }
    return render(request, 'hod_template/manage_results.html', context)

@csrf_exempt
@require_POST
def save_student(request):
    try:
        student_id = request.POST.get('student_id')
        registration_number = request.POST.get('registration_number')
        full_name = request.POST.get('full_name')
        current_class = request.POST.get('current_class')
        date_of_birth = request.POST.get('date_of_birth')
        gender = request.POST.get('gender')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        # Add more fields as needed

        if student_id:
            # Editing existing inventory item
            student = Students.objects.get(pk=student_id)
            student.registration_number = registration_number
            student.full_name = full_name
            student.current_class = current_class
            student.date_of_birth =  date_of_birth
            student.gender = gender
            student.phone_number = phone_number
            student.address = address           
            student.save()
        else:
            # Adding new inventory item
            student = Students(
            registration_number=registration_number,
            full_name=full_name,
            current_class=current_class,
            date_of_birth=date_of_birth,
            gender=gender,
            phone_number=phone_number,
            address=address               
            )
            student.save()

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})  

@csrf_exempt       
@require_POST
def add_results(request):
    try:
        exam_id = request.POST.get('exam_id')
        student = request.POST.get('student')
        subject = request.POST.get('subject')
        exam_type = request.POST.get('exam_type')        
        marks = request.POST.get('marks')
        date_of_exam = request.POST.get('date_of_exam')
        selected_class = request.POST.get('selected_class')
        total_marks = request.POST.get('total_marks')
        
        # Add more fields as needed
        student=Students.objects.get(pk=student)
        subject= Subject.objects.get(pk=subject)
        exam_type= ExamType.objects.get(pk=exam_type)
        
        if exam_id:
            # Editing existing inventory item
            result = Result.objects.get(pk=exam_id)
            result.student = student
            result.subject = subject
            result.exam_type = exam_type
            result.selected_class = selected_class
            result.marks =  marks
            result.date_of_exam = date_of_exam          
            result.total_marks = total_marks           
            result.save()
        else:
            # Adding new inventory item
            result = Result(
            student=student,
            subject=subject,           
            exam_type=exam_type,
            marks=marks,
            date_of_exam=date_of_exam,
            selected_class=selected_class,              
            total_marks=total_marks,               
            )
            result.save()

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})     
    

@csrf_exempt    
@require_POST
def save_subject(request):
    try:
        subject_id = request.POST.get('subject_id')
        subject_name = request.POST.get('subject_name')
        if subject_id:
            # Editing existing inventory item
            subject = Subject.objects.get(pk=subject_id)
            subject.subject_name = subject_name
                   
            subject.save()
        else:
            # Adding new inventory item
            subject = Subject(
            subject_name=subject_name,
              
            )
            subject.save()

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}) 

@csrf_exempt        
@require_POST
def save_exam_type(request):
    try:
        exam_type_id = request.POST.get('exam_type_id')
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if exam_type_id:
            # Editing existing inventory item
            exam_type = ExamType.objects.get(pk=exam_type_id)
            exam_type.name = name
            exam_type.description = description
                   
            exam_type.save()
        else:
            # Adding new inventory item
            exam_type = ExamType(
            name=name,
            description=description,
              
            )
            exam_type.save()

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})     
    

def update_student_status(request):
    try:
        if request.method == 'POST':
            # Get the user_id and is_active values from POST data
            user_id = request.POST.get('user_id')
            is_active = request.POST.get('is_active')

            # Retrieve the staff object or return a 404 response if not found
            student = get_object_or_404(Students, id=user_id)

            # Toggle the is_active status based on the received value
            if is_active == '1':
                student.is_active = False
            elif is_active == '0':
                student.is_active = True
            else:
                messages.error(request, 'Invalid request')
                return JsonResponse("Invalid request") # Make sure 'manage_staffs' is the name of your staff list URL

            student.save()
            messages.success(request, 'Status updated successfully')
        else:
            messages.error(request, 'Invalid request method')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')

    # Redirect back to the staff list page
    return redirect('manage_student')  # Make sure 'manage_staffs' is the name of your staff list URL


# def student_subject_wise_result(request):
#     # Get the student based on the provided student_id
#     student_id = request.POST.get('student_id')
#     exam_type_id = request.POST.get('exam_type_id')
#     year = request.POST.get('year')

#     student = Students.objects.get(id=student_id)
#     # Replace 'Students' with your actual student mode
    
  
#     form_i_students = Students.objects.filter(current_class=student.current_class)
#     total_students = form_i_students.count()
#     # Query the results for the specific student
#     exam_type = get_object_or_404(ExamType, id=exam_type_id)

#     results = Result.objects.filter(student=student, exam_type_id=exam_type)
#     exam_info = StudentExamInfo.objects.filter(
#         student=student,
#         exam_type=exam_type,
#         selected_class=student.current_class
#     ).first()

#     # Retrieve the StudentPositionInfo for the specified student, exam type, and current class
#     position_info = StudentPositionInfo.objects.filter(
#         student=student,
#         exam_type=exam_type,
#         current_class=student.current_class
#     ).first()

#     if exam_info:
#         division = exam_info.division
#         total_grade_points = exam_info.total_grade_points
#     else:
#         division = "Division Not Available"
#         total_grade_points = "Total Grade Points Not Available"

#     if position_info:
#         position = position_info.position
#     else:
#         position = "Position Not Available"

#     context = {
#         'student': student,
#         'results': results,
#         "students": student,
#         'exam_type': exam_type,
#         'position': position,  # Add position to the context
#         'division': division,  # Add position to the context
#         'total_students': total_students,  # Add position to the context
#         'total_grade_points': total_grade_points,  # Add total_grade_points to the context
#     }
#     html_result = render_to_string('hod_template/subject_wise_results.html', context)

#     return JsonResponse({'html_result': html_result})
#     # return render(request, 'hod_template/subject_wise_results.html', context)

def student_subject_wise_result(request):
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
        html_result = render_to_string('hod_template/result_table.html', context)
        return JsonResponse({'html_result': html_result})
 