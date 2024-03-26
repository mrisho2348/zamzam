from collections import defaultdict
from decimal import Decimal
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import RequestContext
from django.urls import reverse
from django.views.decorators.http import require_POST
from result_module.models import AdminHOD, Announcement, AnnouncementForStudents, CustomUser, ExamMetrics, ExamType, Result, StudentExamInfo, StudentPositionInfo, Students, Subject
from django.contrib import messages
from django.contrib.auth import logout,login
from result_module.emailBackEnd import EmailBackend
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
# Create your views here.

def dashboard(request):
    # Fetch total number of students
    total_students = Students.objects.count()

    # Fetch total number of subjects
    total_subjects = Subject.objects.count()

    # Fetch total number of female students
    total_female_students = Students.objects.filter(gender='Female').count()

    # Fetch total number of male students
    total_male_students = Students.objects.filter(gender='Male').count()

    return render(request, "hod_template/home_content.html", {
        'total_students': total_students,
        'total_subjects': total_subjects,
        'total_female_students': total_female_students,
        'total_male_students': total_male_students,
    })

def logout_user(request):
  logout(request)
  return HttpResponseRedirect(reverse("login"))

def ShowLogin(request):  
  return render(request,'login.html')

def student_login(request):  
  return render(request,'student_template/student_login.html')

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
          customuser = CustomUser.objects.get(admin=request.user.id)
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
    exam_types = ExamType.objects.all()
    return render(request, 'hod_template/manage_student.html', {
        'students': students,
        'exam_types': exam_types,
        })

def student_subject_wise_result_page(request,student_id): 
    student = Students.objects.get(id=student_id)
    exam_types = ExamType.objects.all()
    distinct_dates= Result.objects.order_by('date_of_exam').values_list('date_of_exam', flat=True).distinct()
    print(distinct_dates)
    return render(request, 'hod_template/subject_wise_results.html',
                  {
                      'student': student,
                      'exam_types': exam_types,
                      'distinct_dates': distinct_dates,
                   })
    
def students_wise_result_page(request):
    exam_types = ExamType.objects.all()
    distinct_dates= Result.objects.order_by('date_of_exam').values_list('date_of_exam', flat=True).distinct()   
    return render(request, 'hod_template/student_results.html',
                  {                   
                      'exam_types': exam_types,
                      'distinct_dates': distinct_dates,
                   })
    
    

def manage_exam_type(request):
    exam_types = ExamType.objects.all()
    return render(request, 'hod_template/manage_exam_types.html', {'exam_types': exam_types})

def manage_subject(request):
    subjects = Subject.objects.all()
    return render(request, 'hod_template/manage_subject.html', {'subjects': subjects})

@login_required
def staff_announcements(request):
    try:
        admin_hod = request.user.admin_hod  # Access the AdminHOD instance associated with the logged-in user
        staff_announcements = Announcement.objects.filter(created_by=admin_hod)
        return render(request, 'hod_template/staff_announcements.html', {'announcements': staff_announcements})
    except AdminHOD.DoesNotExist:
        return render(request, 'hod_template/staff_announcements.html', {'announcements': []})
  
@csrf_exempt    
def fetch_read_count(request):
    if request.method == 'GET' and 'announcement_id' in request.GET:
        announcement_id = request.GET.get('announcement_id')
        read_count = AnnouncementForStudents.objects.filter(announcement_id=announcement_id, read=True).count()
        return JsonResponse({'read_count': read_count})
    else:
        return JsonResponse({'error': 'Invalid request'})   


@require_POST
def edit_announcement(request):
    try:
        announcement_id = request.POST.get('announcement_id')
        title = request.POST.get('title')
        content = request.POST.get('content')
        current_class = request.POST.get('current_class')

        # Retrieve the announcement object
        announcement = Announcement.objects.get(pk=announcement_id)

        # Update the announcement fields
        announcement.title = title
        announcement.content = content
        announcement.current_class = current_class
        announcement.save()

        return JsonResponse({'status': 'success', 'message': 'Announcement updated successfully'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'Error occurred while updating announcement' + str(e)})
    
@csrf_exempt     
def fetch_students_for_announcement(request):
    if request.method == 'GET' and 'announcement_id' in request.GET:
        announcement_id = request.GET['announcement_id']
        try:
            announcement_students = AnnouncementForStudents.objects.filter(announcement_id=announcement_id, read=True)
            students_data = [{'registration_number': student.student.registration_number, 'full_name': student.student.full_name} for student in announcement_students]
            return JsonResponse({'students': students_data})
        except AnnouncementForStudents.DoesNotExist:
            return JsonResponse({'error': 'No students found for this announcement'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)     

def delete_announcement(request):
    if request.method == 'POST':
        try:
            announcement_id = request.POST.get('announcement_id')
            announcement = Announcement.objects.get(id=announcement_id)
            announcement.delete()
            return JsonResponse({'status': 'success', 'message': 'Announcement deleted successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Error deleting announcement', 'details': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def manage_result(request):
    # Fetch all students
    students = Students.objects.all()

    # Fetch all subjects
    subjects = Subject.objects.all()
    exam_types = ExamType.objects.all()
    # Create a dictionary to store each student's results
    student_results = {}

    # Iterate over each student
    for student in students:
        # Fetch results for the current student
        results = Result.objects.filter(student=student)

        # Create a dictionary to store subject-wise results for the current student
        student_subject_results = {}

        # Iterate over each subject
        for subject in subjects:
            # Check if there is a result for the current subject and student
            result = results.filter(subject=subject).first()
            if result:
                # If result exists, store the grade
                grade = result.determine_grade()
            else:
                # If result does not exist, mark as 'Not Assigned'
                grade = ''

            # Store subject-wise grades in the dictionary
            student_subject_results[subject.subject_name] = grade

        # Add the dictionary of subject-wise grades to the main dictionary
        student_results[student] = student_subject_results

    return render(request, 'hod_template/manage_results.html', {'student_results': student_results,'students':students,'subjects':subjects,'exam_types':exam_types})



def add_announcement(request):
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            current_class = request.POST.get('current_class')
            content = request.POST.get('content')
            created_by = request.user.admin_hod  # Assuming the currently logged-in user is an AdminHOD

            Announcement.objects.create(title=title, current_class=current_class, content=content, created_by=created_by)
            return JsonResponse({'status':'success','message': 'Announcement added successfully'})
        except Exception as e:
            return JsonResponse({'status':'error', 'message': 'Error occurred while adding announcement' + str(e)})
    else:
        return JsonResponse({'status':'error', 'message':  'Invalid request method'})

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
        student_id = request.POST.get('student')
        subject_id = request.POST.get('subject')
        exam_type_id = request.POST.get('exam_type')        
        marks = request.POST.get('marks')
        date_of_exam = request.POST.get('date_of_exam')
        selected_class = request.POST.get('selected_class')
        total_marks = request.POST.get('total_marks')
        exam_id = request.POST.get('exam_id')  # For editing existing result
        
        # Retrieve the student, subject, and exam type objects
        student = Students.objects.get(pk=student_id)
        subject = Subject.objects.get(pk=subject_id)
        exam_type = ExamType.objects.get(pk=exam_type_id)
        
        # Check if the result already exists
        result_exists = Result.objects.filter(
            student_id=student_id,
            subject_id=subject_id,
            exam_type_id=exam_type_id,
            selected_class=selected_class
        ).exists()
        
        if result_exists:
            return JsonResponse({'status': 'error', 'message': f'The result for {subject} in {exam_type} for {student} already exists'})
        
        # If not, proceed with adding or editing the result
        if exam_id:
            # Editing existing result
            result = Result.objects.get(pk=exam_id)
            result.student = student
            result.subject = subject
            result.exam_type = exam_type
            result.marks = marks
            result.date_of_exam = date_of_exam          
            result.selected_class = selected_class
            result.total_marks = total_marks
            result.save()
        else:
            # Adding new result
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

        return JsonResponse({'status': 'success','message':'student result successfully added '})
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
            'remark': remark,
            'grademetrics': grademetrics,
            'average': average,
            'total_marks': total_marks,
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

@csrf_exempt 
def save_marks_view(request):
    if request.method == 'POST':
        try:
            # Retrieve data from the POST request
            result_id = request.POST.get('resultId')
            marks = request.POST.get('marks')

            # Update the marks for the corresponding result
            result = Result.objects.get(id=result_id)
            result.marks = marks
            result.save()

            # Return success response
            return JsonResponse({'success': True, 'message': 'Marks updated successfully.'})

        except Exception as e:
            # Return error response
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        # Return error response for unsupported request method
        return JsonResponse({'success': False, 'message': 'Only POST requests are allowed for this endpoint.'})
    
    
@csrf_exempt  # Use this decorator if CSRF protection is not needed
def delete_result_endpoint(request):
    if request.method == 'POST':
        try:
            # Extract the result ID from the request
            result_id = request.POST.get('resultId')

            # Perform the deletion operation, assuming Result is the model name
            result = Result.objects.get(id=result_id)
            result.delete()

            # Return success response
            return JsonResponse({'success': True, 'message': 'Result deleted successfully.'})

        except Exception as e:
            # Return error response
            return JsonResponse({'success': False, 'message': str(e)})

    else:
        # Return error response for non-POST requests
        return JsonResponse({'success': False, 'message': 'Only POST requests are allowed for this endpoint.'})
        

def student_results_view(request):
    if request.method == 'POST' and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        # Extract form data
        selected_class = request.POST.get('selected_class')
        exam_type_id = request.POST.get('exam_type_id')
        date_of_exam = request.POST.get('date_of_exam')
        
        # Fetch all students
        students = Students.objects.filter(current_class=selected_class)
        
        # Fetch all subjects
        subjects = Subject.objects.all()
        
        # Create a list to store each student's results and metrics
        student_results = []
        
        # Iterate over each student
        for student in students:
            # Fetch results for the current student filtered by exam type and date
            results = Result.objects.filter(
                student=student,
                exam_type_id=exam_type_id,
                date_of_exam=date_of_exam,
                selected_class=selected_class,
            )
            
            # Initialize variables for position, division, total grade points, total marks, average, grade, and remark
            position = None
            division = None
            total_grade_points = None
            total_marks = None
            average = None
            grademetrics = None
            remark = None
            
            # Iterate over each result for the current student
            for result in results:
                # Fetch or calculate position
                position_info, created = StudentPositionInfo.objects.get_or_create(
                    student=student,
                    exam_type=result.exam_type,
                    current_class=result.selected_class,
                )
                position = position_info.position
                
                # Fetch or calculate division
                student_exam_info, created = StudentExamInfo.objects.get_or_create(
                    student=student,
                    exam_type=result.exam_type,
                    selected_class=result.selected_class,
                )
                division = student_exam_info.division
                total_grade_points = student_exam_info.total_grade_points
                
                # Fetch or calculate ExamMetrics
                exam_metrics, created = ExamMetrics.objects.get_or_create(
                    student=student,
                    exam_type=result.exam_type,
                    selected_class=result.selected_class,
                )
                total_marks = exam_metrics.total_marks
                average = exam_metrics.average
                grademetrics = exam_metrics.grade
                remark = exam_metrics.remark
                exam_type = result.exam_type
            
            # Create a dictionary to store subject-wise results for the current student
            student_subject_results = {}
            
            # Iterate over each subject
            for subject in subjects:
                # Check if there is a result for the current subject and student
                result = results.filter(subject=subject).first()
                if result:
                    # If result exists, store the grade
                    grade = result.determine_grade()
                else:
                    # If result does not exist, mark as 'Not Assigned'
                    grade = ''
                
                # Store subject-wise grades in the dictionary
                student_subject_results[subject.subject_name] = grade
            
            # Append student results and metrics to the list
            student_results.append({
                'student': student,
                'total_marks': total_marks,
                'average': average,
                'grademetrics': grademetrics,
                'position': position,
                'division': division,
                'total_grade_points': total_grade_points,
                'remark': remark,
                'student_subject_results': student_subject_results,
            })
        
        # Render the HTML template with the fetched data
        html_result = render_to_string('hod_template/student_results_table.html', {'student_results': student_results})
        
        # Return the HTML result as JSON response
        return JsonResponse({'html_result': html_result})


def exam_type_list(request):
    exam_types = ExamType.objects.all()
    return render(request, 'hod_template/exam_type_list.html', {'exam_types': exam_types})

def exam_type_to_view_class(request, exam_type_id):
    try:
        # Retrieve the exam type object
        exam_type = ExamType.objects.get(pk=exam_type_id)
        
        # Pass the exam type object to the template
        return render(request, 'hod_template/class_wise_results.html', {'exam_type': exam_type})
    except ExamType.DoesNotExist:
        # Handle the case where the exam type does not exist
        return redirect('exam_type_list') 

def view_student_to_add_result(request, exam_type_id, class_name):
    # Retrieve all students for the specified class
    students = Students.objects.filter(current_class=class_name, is_active=True)  
    exam_type = ExamType.objects.get(pk=exam_type_id)  
    # Pass the list of students to the template
    return render(request, 'hod_template/class_wise_students_list.html', {'students': students, 'exam_type': exam_type,'class_name':class_name})


def view_student_to_add_result(request, exam_type_id, class_name): 
        
    # Fetch all students for the specified class
    students = Students.objects.filter(current_class=class_name)
    exam_type = ExamType.objects.get(pk=exam_type_id)  
    # Fetch all subjects
    subjects = Subject.objects.all()
    
    # Create a list to store each student's results and metrics
    student_results = []
    
    # Iterate over each student
    for student in students:
        # Fetch results for the current student filtered by exam type and class
        results = Result.objects.filter(
            student=student,
            exam_type_id=exam_type_id,               
            selected_class=class_name,
        )
        
        # Initialize variables for position, division, total grade points, total marks, average, grade, and remark
        position = None
        division = None
        total_grade_points = None
        total_marks = None
        average = None
        grademetrics = None
        remark = None
        
        # Iterate over each result for the current student
        for result in results:
            # Fetch or calculate position
            position_info, created = StudentPositionInfo.objects.get_or_create(
                student=student,
                exam_type=result.exam_type,
                current_class=result.selected_class,
            )
            position = position_info.position
            
            # Fetch or calculate division
            student_exam_info, created = StudentExamInfo.objects.get_or_create(
                student=student,
                exam_type=result.exam_type,
                selected_class=result.selected_class,
            )
            division = student_exam_info.division
            total_grade_points = student_exam_info.total_grade_points
            
            # Fetch or calculate ExamMetrics
            exam_metrics, created = ExamMetrics.objects.get_or_create(
                student=student,
                exam_type=result.exam_type,
                selected_class=result.selected_class,
            )
            total_marks = exam_metrics.total_marks
            average = exam_metrics.average
            grademetrics = exam_metrics.grade
            remark = exam_metrics.remark
            exam_type = result.exam_type
        
        # Create a dictionary to store subject-wise results for the current student
        student_subject_results = {}
        
        # Iterate over each subject
        for subject in subjects:
            # Check if there is a result for the current subject and student
            result = results.filter(subject=subject).first()
            if result:
                # If result exists, store the grade
                grade = result.determine_grade()
            else:
                # If result does not exist, mark as 'Not Assigned'
                grade = ''
            
            # Store subject-wise grades in the dictionary
            student_subject_results[subject.subject_name] = grade
        
        # Append student results and metrics to the list
        student_results.append({
            'student': student,
            'total_marks': total_marks,
            'average': average,
            'grademetrics': grademetrics,
            'position': position,
            'division': division,
            'total_grade_points': total_grade_points,
            'remark': remark,
            'student_subject_results': student_subject_results,
        })
    
    # Render the HTML template with the fetched data
    return render(request, 'hod_template/class_wise_students_list.html', {
        'student_results': student_results, 
        'class_name': class_name,
        'subjects':subjects,
        'exam_type':exam_type,
        })


@csrf_exempt
def add_student_result(request):
    if request.method == 'POST':
        try:
            # Extract data from the request
            data = request.POST

            # List to store subject IDs for checking uniqueness
            subject_ids = []

            # Iterate over the data to process each row of results
            for i in range(len(data.getlist('subjects[]'))):
                subject_id = int(data.getlist('subjects[]')[i])
                marks = float(data.getlist('marks[]')[i])

                # Validate marks range
                if marks < 0 or marks > 100:
                    return JsonResponse({'success': False, 'message': 'Marks should be between 0 and 100.'})

                # Validate subject uniqueness
                if subject_id in subject_ids:
                    return JsonResponse({'success': False, 'message': 'Each subject should be selected only once for each row.'})
                subject_ids.append(subject_id)

                # Check if a result already exists for the student, exam type, class, and subject
                existing_result = Result.objects.filter(
                    student_id=data.get('student_id'),
                    subject_id=subject_id,
                    exam_type_id=data.get('exam_type'),
                    selected_class=data.get('class_name')
                ).first()
                student = Students.objects.get(id=data.get('student_id'))
                if existing_result:
                    return JsonResponse({'success': False, 'message': f'Result already exists for {student} in {existing_result.subject} for this exam type and class.'})

                # Create a Result object and save it to the database
                Result.objects.create(
                    student_id=data.get('student_id'),
                    subject_id=subject_id,
                    exam_type_id=data.get('exam_type'),
                    marks=marks,
                    date_of_exam=data.get('date_of_exam'),
                    selected_class=data.get('class_name'),
                    total_marks=100
                )

            return JsonResponse({'success': True, 'message': 'Results added successfully.'})

        except Exception as e:
            # Return error response
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        return JsonResponse({'success': False, 'message': 'Only POST requests are allowed for this endpoint.'})