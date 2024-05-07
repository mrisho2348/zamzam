from collections import defaultdict
from decimal import Decimal
import json
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import RequestContext
from django.urls import reverse
from django.views.decorators.http import require_POST
from result_module.models import AdminHOD, Announcement, AnnouncementForStudents, Attendance, AttendanceReport, ClassAttendance, CustomUser, ExamMetrics, ExamType, FeedBackStaff, FeedBackStudent, LeaveReportStaffs, LeaveReportStudent, Result, Staffs, StudentClassAttendance, StudentExamInfo, StudentPositionInfo, Students, Subject, SujbectWiseResults
from django.contrib import messages
from django.contrib.auth import logout,login
from result_module.emailBackEnd import EmailBackend
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from openpyxl import Workbook
# Create your views here.

@login_required
def admin_home(request):
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

def download_excel_template(request, class_name):
    # Get students for the given class
    students = Students.objects.filter(current_class=class_name)

    # Create a new workbook
    wb = Workbook()
    ws = wb.active

    # Add headers for the Excel sheet
    headers = ['Student']
    subject_scores = SujbectWiseResults._meta.get_fields()[2:-5]  # Exclude student and timestamp fields
    for field in subject_scores:
        headers.append(field.name.replace('_score', '').capitalize())  # Get subject name from field name
    ws.append(headers)

    # Add student names and zero scores for each subject
    for student in students:
        row_data = [student.full_name]
        for _ in subject_scores:
            row_data.append(0)  # Populate each subject column with zero value
        ws.append(row_data)

    # Save the workbook in memory
    from io import BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    # Set response headers for Excel file download
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={class_name}_template.xlsx'
    
    # Write workbook data to response
    response.write(output.getvalue())

    return response

@login_required
def manage_student(request):
    students = Students.objects.all()
    exam_types = ExamType.objects.all()
    return render(request, 'hod_template/manage_student.html', {
        'students': students,
        'exam_types': exam_types,
        })

@login_required
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

@login_required    
def students_wise_result_page(request):
    exam_types = ExamType.objects.all()
    distinct_dates= Result.objects.order_by('date_of_exam').values_list('date_of_exam', flat=True).distinct()   
    return render(request, 'hod_template/student_results.html',
                  {                   
                      'exam_types': exam_types,
                      'distinct_dates': distinct_dates,
                   })
    
    
@login_required
def manage_exam_type(request):
    exam_types = ExamType.objects.all()
    return render(request, 'hod_template/manage_exam_types.html', {'exam_types': exam_types})

@login_required
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
        announcement_file_url = None
        accepted_image_formats ='application/pdf'
        max_file_size = 5 * 1024 * 1024
        announcement_file = request.FILES.get('announcement_file')
        if announcement_file:
            if announcement_file.content_type not in accepted_image_formats or announcement_file.size > max_file_size:
                return JsonResponse({'status': False, 'message': 'File must be PDF and should not exceed 5MB.'})
            fs = FileSystemStorage()
            announcement_file_name = fs.save('announcement/' + announcement_file.name, announcement_file)
            announcement_file_url = fs.url(announcement_file_name)
            print(announcement_file_url)
        # Retrieve the announcement object
        announcement = Announcement.objects.get(pk=announcement_id)
        # Update the announcement fields
        announcement.title = title
        announcement.content = content
        announcement.current_class = current_class
        announcement.announcement_file = announcement_file_url
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

@login_required
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
            announcement_file_url = None
            accepted_image_formats = 'application/pdf'
            max_file_size = 5 * 1024 * 1024
            announcement_file = request.FILES.get('announcement_file')
            if announcement_file:
                if announcement_file.content_type not in accepted_image_formats or announcement_file.size > max_file_size:
                    return JsonResponse({'status': False, 'message': 'File must be PDF and should not exceed 5MB.'})
                fs = FileSystemStorage()
                announcement_file_name = fs.save('announcement/' + announcement_file.name, announcement_file)
                announcement_file_url = fs.url(announcement_file_name)
                print(announcement_file_url)
            Announcement.objects.create(
                title=title,
                current_class=current_class,
                content=content, 
                created_by=created_by,
                announcement_file=announcement_file_url,
                )
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
        
        student_photo = request.FILES.get('student_photo')
        accepted_image_formats = ['image/jpeg', 'image/jpg', 'image/png']
        max_file_size = 5 * 1024 * 1024
        student_photo_url = None
        if student_photo:
            if student_photo.content_type not in accepted_image_formats or student_photo.size > max_file_size:
                return JsonResponse({'status': False, 'message': 'File must be PNG, JPEG, or JPG and should not exceed 5MB.'})
            fs = FileSystemStorage()
            student_photo_name = fs.save('student_profile_pic/' + student_photo.name, student_photo)
            student_photo_url = fs.url(student_photo_name)
            print(student_photo_url)
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
            student.profile_pic = student_photo_url           
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
            address=address,               
            profile_pic=student_photo_url,               
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


@login_required
def exam_type_list(request):
    exam_types = ExamType.objects.all()
    return render(request, 'hod_template/exam_type_list.html', {'exam_types': exam_types})

@login_required
def exam_type_to_view_class(request, exam_type_id):
    try:
        # Retrieve the exam type object
        exam_type = ExamType.objects.get(pk=exam_type_id)
        
        # Pass the exam type object to the template
        return render(request, 'hod_template/class_wise_results.html', {'exam_type': exam_type})
    except ExamType.DoesNotExist:
        # Handle the case where the exam type does not exist
        return redirect('exam_type_list') 

@login_required
def view_student_to_add_result(request, exam_type_id, class_name):
    # Retrieve all students for the specified class
    students = Students.objects.filter(current_class=class_name, is_active=True)  
    exam_type = ExamType.objects.get(pk=exam_type_id)  
    # Pass the list of students to the template
    return render(request, 'hod_template/class_wise_students_list.html', {'students': students, 'exam_type': exam_type,'class_name':class_name})

@login_required
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
  
@csrf_exempt   
def save_student_result(request):
    if request.method == 'POST':
        try:
            # Parse form data
            student_id = request.POST.get('student_id')
            exam_type_id = request.POST.get('exam_type_id')
            date_of_exam = request.POST.get('date_of_exam')
            student = Students.objects.get(id=student_id)
            selected_class = student.current_class

            # Check if required fields are missing
            if not all([student_id, exam_type_id, date_of_exam]):
                return JsonResponse({'success': False, 'message': 'Required field(s) missing'})

            # Assign default values if fields are empty or null
            history_score = request.POST.get('history_score', 0)
            english_score = request.POST.get('english_score', 0)
            biology_score = request.POST.get('biology_score', 0)
            arabic_score = request.POST.get('arabic_score', 0)
            physics_score = request.POST.get('physics_score', 0)
            mathematics_score = request.POST.get('mathematics_score', 0)
            chemistry_score = request.POST.get('chemistry_score', 0)
            civics_score = request.POST.get('civics_score', 0)
            geography_score = request.POST.get('geography_score', 0)
            kiswahili_score = request.POST.get('kiswahili_score', 0)
            edk_score = request.POST.get('edk_score', 0)
            computer_application_score = request.POST.get('computer_application_score', 0)
            commerce_score = request.POST.get('commerce_score', 0)
            book_keeping_score = request.POST.get('book_keeping_score', 0)

            # Create Results instance
            result = SujbectWiseResults(
                student_id=student_id,
                exam_type_id=exam_type_id,
                selected_class=selected_class,
                history_score=history_score,
                english_score=english_score,
                biology_score=biology_score,
                arabic_score=arabic_score,
                physics_score=physics_score,
                mathematics_score=mathematics_score,
                chemistry_score=chemistry_score,
                civics_score=civics_score,
                geography_score=geography_score,
                kiswahili_score=kiswahili_score,
                edk_score=edk_score,
                computer_application_score=computer_application_score,
                commerce_score=commerce_score,
                book_keeping_score=book_keeping_score,
                date_of_exam=date_of_exam
            )

            # Save the result
            result.save()

            # Return success response
            return JsonResponse({'success': True, 'message': 'Student result added successfully'})

        except Students.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Student does not exist'})

        except Exception as e:
            # Return failure response with error message
            return JsonResponse({'success': False, 'message': str(e)})

    # If request method is not POST, return failure response
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@login_required
def display_results(request):
    results = SujbectWiseResults.objects.all()
    students = Students.objects.all()
    exam_types = ExamType.objects.all()
    return render(request, 'hod_template/exam_results.html', {
        'results': results,
        'students': students,
        'exam_types': exam_types,
        })


@login_required
def manage_staff(request):     
    staffs=Staffs.objects.all()  
    subjects=Subject.objects.all()  
    return render(request,"hod_template/manage_staff.html",{
        "staffs":staffs,
        "subjects":subjects,
        })      

def add_staff_record(request):
    if request.method == 'POST':
        # Extract form data from the request
        first_name = request.POST.get('first_name')
        middle_name = request.POST.get('middle_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        current_class = request.POST.get('current_class')
        subjects = request.POST.getlist('subject')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        dob = request.POST.get('dob')
        doe = request.POST.get('doe')
        phone = request.POST.get('phone')
        staff_id = request.POST.get('staff_id')
        
        # Handling staff photo upload
        staff_photo_url = None
        accepted_image_formats = ['image/jpeg', 'image/jpg', 'image/png']
        max_file_size = 5 * 1024 * 1024
        staff_photo = request.FILES.get('staff_photo')
        if staff_photo:
            if staff_photo.content_type not in accepted_image_formats or staff_photo.size > max_file_size:
                return JsonResponse({'status': False, 'message': 'File must be PNG, JPEG, or JPG and should not exceed 5MB.'})
            fs = FileSystemStorage()
            staff_photo_name = fs.save('staff_profile_pic/' + staff_photo.name, staff_photo)
            staff_photo_url = fs.url(staff_photo_name)
            print(staff_photo_url)
        
        try:
            if staff_id:
                # Editing an existing staff record
                staff = Staffs.objects.get(pk=staff_id)
                user = staff.admin
                # Update user data
                user.first_name = first_name
                user.last_name = last_name                         
                user.save()
                # Update staff data
                staff.middle_name = middle_name
                staff.profile_pic = staff_photo_url
                staff.address = address
                staff.current_class = current_class
                staff.gender = gender
                staff.date_of_birth = dob
                staff.date_of_employment = doe
                staff.phone_number = phone
                staff.save()
                # Update subjects
                staff.subjects.set(subjects)
                return JsonResponse({'status': True, 'message': 'Staff record updated successfully.'})
            else:
                if CustomUser.objects.filter(username=username).exists():
                    return JsonResponse({'status': False, 'message': 'Username already exists.'})
            
                if CustomUser.objects.filter(email=email).exists():
                    return JsonResponse({'status': False, 'message': 'Email already exists.'})
            
                # Adding a new staff record
                user = CustomUser.objects.create_user(
                    last_name=last_name,
                    first_name=first_name,
                    username=username,
                    email=email,
                    password=password,
                    user_type=2
                )
                staff = user.staffs              
                staff.date_of_birth = dob
                staff.date_of_employment = doe
                staff.gender = gender
                staff.middle_name = middle_name
                staff.current_class = current_class
                staff.address = address
                staff.phone_number = phone             
                staff.profile_pic = staff_photo_url      
                # Save the staff record
                staff.save()
                staff.subjects.set(subjects)
                return JsonResponse({'status': True, 'message': 'Staff record added successfully.'})
        except Exception as e:
            return JsonResponse({'status': False, 'message': str(e)}, status=400)
    return JsonResponse({'status': False, 'message': 'Invalid request method.'}, status=400)


@csrf_exempt
def delete_staff(request, staff_id):
    if request.method == 'POST':
        try:
            staff = get_object_or_404(Staffs, id=staff_id)
            staff.delete()
            return JsonResponse({'status': 'success', 'message': 'Staff record deleted successfully.'})
        except IntegrityError as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'An error occurred while deleting the staff record.'}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)


def update_staff_status(request):
    try:
        if request.method == 'POST':
            # Get the user_id and is_active values from POST data
            user_id = request.POST.get('user_id')
            is_active = request.POST.get('is_active')

            # Retrieve the staff object or return a 404 response if not found
            staff = get_object_or_404(CustomUser, id=user_id)

            # Toggle the is_active status based on the received value
            if is_active == '1':
                staff.is_active = False
            elif is_active == '0':
                staff.is_active = True
            else:
                messages.error(request, 'Invalid request')
                return redirect('manage_staff')  # Make sure 'manage_staffs' is the name of your staff list URL

            staff.save()
            messages.success(request, 'Status updated successfully')
        else:
            messages.error(request, 'Invalid request method')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')

    # Redirect back to the staff list page
    return redirect('manage_staff')  # Make sure 'manage_staffs' is the name of your staff list URL


@csrf_exempt
def staff_feedback_message_replied(request):
    feedback_id = request.POST.get("id")
    feedback_message = request.POST.get("message")
    try:    
      feedback = FeedBackStaff.objects.get(id=feedback_id)
      feedback.feedback_reply = feedback_message
      feedback.save() 
      return HttpResponse(True)
    except:
       return HttpResponse(False)           
 
@login_required   
def student_leave_view(request):
    leaves = LeaveReportStudent.objects.all()
    return render(request,"hod_template/student_leave_view.html",{"leaves":leaves})

def student_approve_leave(request,leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return HttpResponseRedirect(reverse("student_leave_view"))

def student_disapprove_leave(request,leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return HttpResponseRedirect(reverse("student_leave_view"))

@login_required
def staff_leave_view(request):
    leaves = LeaveReportStaffs.objects.all()
    return render(request,"hod_template/staff_leave_view.html",{"leaves":leaves})

def staff_approve_leave(request,leave_id):
    leave = LeaveReportStaffs.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return HttpResponseRedirect(reverse("staff_leave_view"))


def staff_disapprove_leave(request,leave_id):
    leave = LeaveReportStaffs.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return HttpResponseRedirect(reverse("staff_leave_view"))

@login_required
def admin_view_attendance(request):     
     return render(request,"hod_template/admin_view_attendance.html",{})

@csrf_exempt
def admin_get_student_attendance(request):
    try:
        attendance_date = request.POST.get("attendance_date_id")
        current_class = request.POST.get("current_class")     
        students = Students.objects.filter(selected_class=current_class)      
        # Fetch attendance records for the selected date and students
        attendance_data = AttendanceReport.objects.filter(
            attendance_id=attendance_date,
            student_id__in=students
        )
        
        
        list_data = []

        for student in attendance_data:
            data_small = {"id": student.student_id.admin.id, "name": student.student_id.admin.first_name + " " + student.student_id.admin.last_name, "status": student.status}
            list_data.append(data_small)

        return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)
    except Exception as e:
          # Fix the print statement here
        return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
def admin_get_attendance_date(request):
     subject = request.POST.get("subject_id")
     session_year_id = request.POST.get("session_year_id") 
     subject_obj = Subject.objects.get(id=subject)
     attendance = Attendance.objects.filter(subject_id=subject_obj)
     attendance_obj = []
     
     for attendance_single in attendance:
         data = {
             "id":attendance_single.id,
             "attendance_date":str(attendance_single.attendance_date),
             "session_year_id":attendance_single.session_id.id
             }
         attendance_obj.append(data)
         
     return JsonResponse(json.dumps(attendance_obj),content_type="application/json",safe=False) 
 
 
def admin_save_updateattendance(request):
    student_ids=request.POST.get("student_ids")
    attendance_date=request.POST.get("attendance_date")     
    attendance=Attendance.objects.get(id=attendance_date)     
    json_sstudent=json.loads(student_ids)
    try:
        for stud in json_sstudent:
             student=Students.objects.get(admin_id=stud['id'])
             attendance_report=AttendanceReport.objects.get(student_id=student,attendance_id=attendance)
             attendance_report.status =stud["status"]
             attendance_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("ERR")

@csrf_exempt
def student_feedback_message_replied(request):
    feedback_id = request.POST.get("id")
    feedback_message = request.POST.get("message")
    try:    
      feedback = FeedBackStudent.objects.get(id=feedback_id)
      feedback.feedback_reply = feedback_message
      feedback.save() 
      return HttpResponse(True)
    except:
       return HttpResponse(False)  

@login_required 
def staff_feedback_message(request):
    feedbacks = FeedBackStaff.objects.all()
    return render(request,"hod_template/staff_feedback_message.html",{"feedbacks":feedbacks})

@login_required
def  student_feedback_message(request):
    feedbacks = FeedBackStudent.objects.all()
    return render(request,"hod_template/student_feedback_message.html",{"feedbacks":feedbacks})

@csrf_exempt
def check_email_exist(request):
    email = request.POST.get("email")
    user_object = CustomUser.objects.filter(email=email).exists()
    if user_object:
        return HttpResponse(True)
    
    else:
        return HttpResponse(False)
    
    
@csrf_exempt
def check_username_exist(request):
    username = request.POST.get("username")
    user_object = CustomUser.objects.filter(username=username).exists()
    if user_object:
        return HttpResponse(True)
    
    else:
        return HttpResponse(False) 
   
@login_required   
def admin_view_class_attendance(request):
    admin = request.user
    attendances=ClassAttendance.objects.all()  
    return render(request, "hod_template/admin_view_class_attendance.html", {          
         "admin": admin,
        "attendances": attendances,
    })

@login_required    
def admin_view_subject_attendance(request):
    admin = request.user
    attendances=Attendance.objects.all()  
    subjects=Subject.objects.all() 
    return render(request, "hod_template/admin_view_subject_attendance.html", {          
        "admin": admin,
        "attendances": attendances,
        "subjects": subjects,
    })   
    
@csrf_exempt
def admin_get_class_student_attendance_data(request):  
    date_id = request.POST.get("date") 
    current_class = request.POST.get("current_class")    
    students = Students.objects.filter(current_class=current_class)   
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
def admin_get_subject_student_attendance_data(request):  
    date_id = request.POST.get("date") 
    current_class = request.POST.get("current_class")    
    subject = request.POST.get("subject")    
    students = Students.objects.filter(current_class=current_class)   
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