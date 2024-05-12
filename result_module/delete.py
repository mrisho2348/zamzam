from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from result_module.models import ExamType, Students, Subject
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


@csrf_exempt
@require_POST
def delete_student(request):
    try:
        student_id = request.POST.get('studentId')  # Get studentId from post data
        if student_id:
            student = get_object_or_404(Students, pk=student_id)
            student.delete()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Student ID is missing'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}) 
   
    
@csrf_exempt      
@require_POST
def delete_exam_type(request, exam_id):
    try:
        exam = get_object_or_404(ExamType, pk=exam_id)
        exam.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}) 

    
@csrf_exempt      
@require_POST
def delete_subject(request, subject_id):
    try:
        subject = get_object_or_404(Subject, pk=subject_id)
        subject.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}) 