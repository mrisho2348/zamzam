
from django.urls import  include, path

from result_module import StudentView, imports


urlpatterns = [      
        path('student_subject_attendance_data', StudentView.student_subject_attendance_data, name='student_subject_attendance_data'),     
        path('student_class_attendance_data', StudentView.student_class_attendance_data, name='student_class_attendance_data'),     
        path('student_view_class_attendance', StudentView.student_view_class_attendance, name='student_view_class_attendance'),     
        path('student_view_subject_attendance', StudentView.student_view_subject_attendance, name='student_view_subject_attendance'),     
        path('student_home', StudentView.student_home, name='student_home'),    
       
        path('single_student_details', StudentView.single_student_details, name='single_student_details'), 
        path('student_dologin', StudentView.student_dologin, name='student_dologin'),  
        path('student_login', StudentView.student_login, name='student_login'),  
        path('student_subject_wise_result_pages', StudentView.student_subject_wise_result_pages, name='student_subject_wise_result_pages'),  
        path('fetch_unread_announcement_count/', StudentView.fetch_unread_announcement_count, name='fetch_unread_announcement_count'),  
        path('student_announcements', StudentView.student_announcements, name='student_announcements'),  
        path('students_subject_wise_results', StudentView.students_subject_wise_results, name='students_subject_wise_results'),  
        path('student_apply_leave', StudentView.student_apply_leave, name='student_apply_leave'),  
        path('student_apply_leave_save', StudentView.student_apply_leave_save, name='student_apply_leave_save'), 
        path('student_sendfeedback', StudentView.student_sendfeedback, name='student_sendfeedback'),  
        path('student_sendfeedback_save', StudentView.student_sendfeedback_save, name='student_sendfeedback_save'),    
        path('single_student_details', StudentView.single_student_details, name='single_student_details'),   
       
    
]