# views.py
import logging
from django.shortcuts import redirect, render
from django.contrib import messages
from django.db import IntegrityError

from result_module.models import ExamType, Students, Subject
from .resources import ExamTypeResources, StudentResources, SubjectResources
from .forms import ImportExamTypeForm, ImportStudentForm, ImportSubjectForm
from tablib import Dataset
logger = logging.getLogger(__name__)



def import_student_records(request):
    if request.method == 'POST':
        form = ImportStudentForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                resource = StudentResources()
                new_records = request.FILES['student_file']
                
                # Use tablib to load the imported data
                dataset = resource.export()
                imported_data = dataset.load(new_records.read(), format='xlsx')  # Assuming you are using xlsx, adjust accordingly

                for data in imported_data:
                     student_recode = Students(
                        registration_number=data[0],
                        full_name=data[1],                     
                        current_class=data[2], 
                        date_of_birth=data[3],                     
                        gender=data[4],                     
                        phone_number=data[5],                     
                        address=data[6],                  
                    )
                     student_recode.save()

                return redirect('manage_student') 
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')

    else:
        form = ImportStudentForm()

    return render(request, 'hod_template/import_student.html', {'form': form})

def import_subject_records(request):
    if request.method == 'POST':
        form = ImportSubjectForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                resource = SubjectResources()
                new_records = request.FILES['student_file']
                
                # Use tablib to load the imported data
                dataset = resource.export()
                imported_data = dataset.load(new_records.read(), format='xlsx')  # Assuming you are using xlsx, adjust accordingly

                for data in imported_data:
                     subject_recode = Subject(
                        subject_name=data[0],
                                      
                    )
                     subject_recode.save()

                return redirect('manage_subject') 
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')

    else:
        form = ImportSubjectForm()

    return render(request, 'hod_template/import_subject.html', {'form': form})

def import_exam_type_records(request):
    if request.method == 'POST':
        form = ImportExamTypeForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                resource = ExamTypeResources()
                new_records = request.FILES['student_file']
                
                # Use tablib to load the imported data
                dataset = resource.export()
                imported_data = dataset.load(new_records.read(), format='xlsx')  # Assuming you are using xlsx, adjust accordingly

                for data in imported_data:
                     subject_recode = ExamType(
                        name=data[0],
                        description=data[0],
                                      
                    )
                     subject_recode.save()

                return redirect('manage_exam_type') 
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')

    else:
        form = ImportExamTypeForm()

    return render(request, 'hod_template/import_exam_type.html', {'form': form})


