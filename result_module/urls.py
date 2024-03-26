
from django.urls import  include, path

from result_module import imports
from . import views,delete,StudentView

urlpatterns = [
        path('',views.ShowLogin, name="login"),
        path('accounts/', include('django.contrib.auth.urls')),  
        path('zamzam/dashboard',views.dashboard, name="dashboard"),
        path('dologin',views.DoLogin, name="DoLogin"),
        path('save_student/', views.save_student, name='save_student'),
        path('add_student_result/', views.add_student_result, name='add_student_result'),
        path('save_subject/', views.save_subject, name='save_subject'),
        path('save_exam_type/', views.save_exam_type, name='save_exam_type'),
        path('add_results/', views.add_results, name='add_results'),
        path('save_marks_view/', views.save_marks_view, name='save_marks_endpoint'),
        path('delete_result_endpoint/', views.delete_result_endpoint, name='delete_result_endpoint'),
        path('admin_profile/', views.admin_profile, name='admin_profile'),        
        path('add_announcement/', views.add_announcement, name='add_announcement'),
        path('delete_announcement/', views.delete_announcement, name='delete_announcement'),
        path('staff_announcements/', views.staff_announcements, name='staff_announcements'),
        path('fetch_read_count/', views.fetch_read_count, name='fetch_read_count'),
        path('edit_profile_save/', views.edit_profile_save, name='edit_profile_save'),
        path('edit_announcement/', views.edit_announcement, name='edit_announcement'),
        path('fetch_students_for_announcement/', views.fetch_students_for_announcement, name='fetch_students_for_announcement'),
        path('student-results/', views.student_results_view, name='student_results'),
        path('exam-types/', views.exam_type_list, name='exam_type_list'),
        path('exam_type_to_view_class/<int:exam_type_id>/', views.exam_type_to_view_class, name='exam_type_to_view_class'),
        path('view_student_to_add_result/<int:exam_type_id>/<str:class_name>/', views.view_student_to_add_result, name='view_student_to_add_result'),
        # manage urls 
        path('students/', views.manage_student, name='manage_student'),        
        path('manage_exam_type/', views.manage_exam_type, name='manage_exam_type'),
        path('manage_subject/', views.manage_subject, name='manage_subject'),
        path('manage_result/', views.manage_result, name='manage_result'),
        path('update_student_status/', views.update_student_status, name='update_student_status'),
        path('students_wise_result_page/', views.students_wise_result_page, name='students_wise_result_page'),
        path('student_subject_wise_result/', views.student_subject_wise_result, name='student_subject_wise_result'),
        path('student_subject_wise_result_page/<int:student_id>/', views.student_subject_wise_result_page, name='student_subject_wise_result_page'),
       
        # delete urls 
        path('delete_student/<int:student_id>/', delete.delete_student, name='delete_student'),
        path('delete_subject/<int:subject_id>/', delete.delete_subject, name='delete_subject'),
        path('delete_exam_type/<int:exam_id>/', delete.delete_exam_type, name='delete_exam_type'),
        
        # imports urls 
         path('import_student_records', imports.import_student_records, name='import_student_records'),
         path('import_subject_records', imports.import_subject_records, name='import_subject_records'),
         path('import_exam_type_records', imports.import_exam_type_records, name='import_exam_type_records'),
         
          # student url paths  
        path('student_home', StudentView.student_home, name='student_home'),      
       
        path('student_profile', StudentView.student_profile, name='student_profile'),    
        path('student_profile_save', StudentView.student_profile_save, name='student_profile_save'), 
        path('single_student_details', StudentView.single_student_details, name='single_student_details'),  
        path('student_dologin', StudentView.student_dologin, name='student_dologin'),  
        path('student_subject_wise_result_pages', StudentView.student_subject_wise_result_pages, name='student_subject_wise_result_pages'),  
        path('fetch_unread_announcement_count/', StudentView.fetch_unread_announcement_count, name='fetch_unread_announcement_count'),  
        path('student_announcements', StudentView.student_announcements, name='student_announcements'),  
        path('students_subject_wise_results', StudentView.students_subject_wise_results, name='students_subject_wise_results'),  
        path('student_login', views.student_login, name='student_login'),  
        path('logout_user', views.logout_user, name='logout_user'),  # Move this line here
    
]