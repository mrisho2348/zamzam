
from django.urls import  include, path

from result_module import imports
from . import views,delete

urlpatterns = [
        path('',views.ShowLogin, name="login"),
        path('accounts/', include('django.contrib.auth.urls')),  
        path('zamzam/dashboard',views.dashboard, name="dashboard"),
        path('dologin',views.DoLogin, name="DoLogin"),
        path('save_student/', views.save_student, name='save_student'),
        path('save_subject/', views.save_subject, name='save_subject'),
        path('save_exam_type/', views.save_exam_type, name='save_exam_type'),
        path('add_results/', views.add_results, name='add_results'),
        path('admin_profile/', views.admin_profile, name='admin_profile'),
        path('edit_profile_save/', views.edit_profile_save, name='edit_profile_save'),
        
        # manage urls 
        path('students/', views.manage_student, name='manage_student'),        
        path('manage_exam_type/', views.manage_exam_type, name='manage_exam_type'),
        path('manage_subject/', views.manage_subject, name='manage_subject'),
        path('manage_result/', views.manage_result, name='manage_result'),
        path('update_student_status/', views.update_student_status, name='update_student_status'),
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
]