# views.py
from decimal import Decimal, InvalidOperation
import logging
from django.shortcuts import redirect, render
from django.contrib import messages
from django.urls import reverse
from result_module.models import ExamType, Students,SujbectWiseResults
from .resources import  SujbectWiseResultsResources
from .forms import ImportSujbectWiseResultsForm

def import_subject_wise_result(request, exam_type_id):
    if request.method == 'POST':
        form = ImportSujbectWiseResultsForm(request.POST, request.FILES)
        exam_type = ExamType.objects.get(pk=exam_type_id)  # Get the exam type
                
        if form.is_valid():
            try:
                resource = SujbectWiseResultsResources()
                new_records = request.FILES['new_record']
                
                # Load the imported data using tablib
                dataset = resource.export()
                imported_data = dataset.load(new_records.read(), format='xlsx')  # Adjust format accordingly

                for data in imported_data:
                    # Check if the row has the expected number of elements
                    if len(data) != 16:  # Assuming there are 16 columns of data in each row
                        # Log the error and skip this row
                        messages.error(request, f'Invalid data format in row: {data}')
                        continue

                    registration_number = data[0]  # Assuming student registration number is in the first column
                    try:
                        # Get the student object using the provided registration number
                        student = Students.objects.get(registration_number=registration_number)
                    except Students.DoesNotExist:
                        # If the student does not exist, log the error and continue to the next record
                        messages.error(request, f'Student "{registration_number}" does not exist.')
                        continue

                    # Validate and convert score values to decimal numbers
                    scores = data[2:]
                    converted_scores = []
                    for i, score in enumerate(scores):
                        try:
                            converted_score = Decimal(score)
                            converted_scores.append(converted_score)
                        except InvalidOperation:
                            # Log the error and skip this row
                            messages.error(request, f'Invalid score format for student "{student.full_name}" at index {i+1}')
                            break  # Skip the entire row if any score value is invalid

                    else:
                        # Check if a record already exists for this student, exam type, and class
                        existing_record = SujbectWiseResults.objects.filter(student=student, exam_type=exam_type, selected_class=student.current_class).exists()
                        if existing_record:
                            # Skip this record if a record already exists for this student, exam type, and class
                            continue

                        # Create a new SujbectWiseResults record
                        new_record = SujbectWiseResults(                       
                            student_id=student.id,
                            physics_score=converted_scores[0],
                            chemistry_score=converted_scores[1],
                            biology_score=converted_scores[2],
                            mathematics_score=converted_scores[3],
                            geography_score=converted_scores[4],
                            kiswahili_score=converted_scores[5],
                            history_score=converted_scores[6],
                            english_score=converted_scores[7],
                            civics_score=converted_scores[8],
                            arabic_score=converted_scores[9],
                            edk_score=converted_scores[10],
                            computer_application_score=converted_scores[11],
                            commerce_score=converted_scores[12],
                            book_keeping_score=converted_scores[13],
                            selected_class=student.current_class,
                            exam_type=exam_type,
                        )
                        new_record.save()
                
                # Redirect to the manage_sujbectWiseResults page after successful import
                return redirect(reverse('staff_view_student_to_add_result', args=[exam_type_id, student.current_class]))
            except Exception as e:
                # Handle any exceptions and display an error message
                messages.error(request, f'An error occurred: {e}')
    else:
        # If the request method is not POST, render the import form
        form = ImportSujbectWiseResultsForm()

    return render(request, 'staff_template/import_subject_wise_result.html', {
        'form': form,
        'exam_type_id': exam_type_id,  
    })
    
