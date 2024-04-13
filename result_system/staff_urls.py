
from django.urls import include, path

from result_module import StaffImports, StaffView

urlpatterns = [
 # staff url paths  
    path('get_subject_student_attendance_data', StaffView.get_subject_student_attendance_data, name='get_subject_student_attendance_data'),  
    path('staff_view_subject_attendance', StaffView.staff_view_subject_attendance, name='staff_view_subject_attendance'),  
    path('get_class_student_attendance_data', StaffView.get_class_student_attendance_data, name='get_class_student_attendance_data'),  
    path('staff_view_class_attendance', StaffView.staff_view_class_attendance, name='staff_view_class_attendance'),  
    path('staff_home', StaffView.staff_home, name='staff_home'),  
    path('staff_take_class_attendance', StaffView.staff_take_class_attendance, name='staff_take_class_attendance'),  
    path('staff_take_attendance', StaffView.staff_take_attendance, name='staff_take_attendance'),  
    path('staff_fetch_students', StaffView.staff_fetch_students, name='staff_fetch_students'),  
    path('get_students', StaffView.get_students, name='staff_get_students'),  
    path('staff_update_class_attendance', StaffView.staff_update_class_attendance, name='staff_update_class_attendance'),  
    path('staff_save_class_attendance_data', StaffView.staff_save_class_attendance_data, name='staff_save_class_attendance_data'),  
    path('save_attendance_data', StaffView.save_attendance_data, name='staff_save_attendance_data'),  
    path('staff_get_class_attendance_date', StaffView.staff_get_class_attendance_date, name='staff_get_class_attendance_date'),  
    path('get_attendance_date', StaffView.get_attendance_date, name='staff_get_attendance_date'),  
    path('get_class_student_attendance', StaffView.get_class_student_attendance, name='get_class_student_attendance'),  
    path('get_student_attendance', StaffView.get_student_attendance, name='get_student_attendance'),  
    path('staff_update_attendance', StaffView.staff_update_attendance, name='staff_update_attendance'),  
    path('save_class_updateattendance', StaffView.save_class_updateattendance, name='save_class_updateattendance'),  
    path('save_updateattendance', StaffView.save_updateattendance, name='save_updateattendance'),  
    path('staff_apply_leave', StaffView.staff_apply_leave, name='staff_apply_leave'),  
    path('staff_apply_leave_save', StaffView.staff_apply_leave_save, name='staff_apply_leave_save'),  
    path('staff_sendfeedback', StaffView.staff_sendfeedback, name='staff_sendfeedback'),  
    path('staff_sendfeedback_save', StaffView.staff_sendfeedback_save, name='staff_sendfeedback_save'),  
    path('staff_detail', StaffView.staff_detail, name='staff_detail'),  
   
  
    
    path('import_subject_wise_result/<int:exam_type_id>/', StaffImports.import_subject_wise_result, name='staff_import_subject_wise_result'),
    
    path('add_results/', StaffView.add_results, name='staff_add_results'),
    path('add_student_result/', StaffView.add_student_result, name='staff_add_student_result'),
    path('save_marks_view/', StaffView.save_marks_view, name='staff_save_marks_endpoint'),
    path('delete_result_endpoint/', StaffView.delete_result_endpoint, name='staff_delete_result_endpoint'),
    path('student-results/', StaffView.student_results_view, name='staff_student_results'),
    path('exam-types/', StaffView.exam_type_list, name='staff_exam_type_list'),
    path('exam_type_to_view_class/<int:exam_type_id>/', StaffView.exam_type_to_view_class, name='staff_exam_type_to_view_class'),
    path('view_student_to_add_result/<int:exam_type_id>/<str:class_name>/', StaffView.view_student_to_add_result, name='staff_view_student_to_add_result'),
    path('manage_result/', StaffView.manage_result, name='staff_manage_result'),    
    path('students_wise_result_page/', StaffView.students_wise_result_page, name='staff_students_wise_result_page'),
    path('student_subject_wise_result/', StaffView.student_subject_wise_result, name='staff_student_subject_wise_result'),
    path('student_subject_wise_result_page/<int:student_id>/', StaffView.student_subject_wise_result_page, name='staff_student_subject_wise_result_page'),

 
]