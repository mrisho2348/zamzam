
from django.urls import   path
from result_module import HodViews, Delete, imports

urlpatterns = [       
        path('admin_get_class_student_attendance_data/',HodViews.admin_get_class_student_attendance_data, name="admin_get_class_student_attendance_data"),
        path('admin_get_subject_student_attendance_data/',HodViews.admin_get_subject_student_attendance_data, name="admin_get_subject_student_attendance_data"),
        path('admin_view_class_attendance/',HodViews.admin_view_class_attendance, name="admin_view_class_attendance"),
        path('admin_view_subject_attendance/',HodViews.admin_view_subject_attendance, name="admin_view_subject_attendance"),
        path('admin_home/',HodViews.admin_home, name="admin_home"),
        path('display_results/',HodViews.display_results, name="display_results"),
        path('save_student_result/',HodViews.save_student_result, name="save_student_result"),
        path('add_staff_record/',HodViews.add_staff_record, name="add_staff_record"),
        path('update_staff_status/',HodViews.update_staff_status, name="update_staff_status"),
        path('manage_staff/',HodViews.manage_staff, name="manage_staff"),
        path('check_email_exist', HodViews.check_email_exist, name='check_email_exist'),
        path('check_username_exist', HodViews.check_username_exist, name='check_username_exist'),
        path('student_feedback_message', HodViews.student_feedback_message, name='student_feedback_message'),
        path('student_feedback_message_replied', HodViews.student_feedback_message_replied, name='student_feedback_message_replied'),        
        path('staff_feedback_message_replied', HodViews.staff_feedback_message_replied, name='staff_feedback_message_replied'),
        path('staff_feedback_message', HodViews.staff_feedback_message, name='staff_feedback_message'),
        path('student_leave_view', HodViews.student_leave_view, name='student_leave_view'),
        path('staff_leave_view', HodViews.staff_leave_view, name='staff_leave_view'), 
        path('download-template/<str:class_name>/', HodViews.download_excel_template, name='download_excel_template'),
        path('student_approve_leave/<str:leave_id>', HodViews.student_approve_leave, name='student_approve_leave'),  
        path('student_disapprove_leave/<str:leave_id>', HodViews.student_disapprove_leave, name='student_disapprove_leave'), 
        path('staff_approve_leave/<str:leave_id>', HodViews.staff_approve_leave, name='staff_approve_leave'), 
        path('staff_disapprove_leave/<str:leave_id>', HodViews.staff_disapprove_leave, name='staff_disapprove_leave'), 
        path('admin_view_attendance', HodViews.admin_view_attendance, name='admin_view_attendance'), 
        path('admin_get_student_attendance', HodViews.admin_get_student_attendance, name='admin_get_student_attendance'), 
        path('admin_get_attendance_date', HodViews.admin_get_attendance_date, name='admin_get_attendance_date'), 
        path('admin_save_updateattendance', HodViews.admin_save_updateattendance, name='admin_save_updateattendance'),
        path('delete-staff/<int:staff_id>/', HodViews.delete_staff, name='delete_staff'),
        path('save_student/', HodViews.save_student, name='save_student'),
        path('add_student_result/', HodViews.add_student_result, name='add_student_result'),
        path('save_subject/', HodViews.save_subject, name='save_subject'),
        path('save_exam_type/', HodViews.save_exam_type, name='save_exam_type'),
        path('add_results/', HodViews.add_results, name='add_results'),
        path('save_marks_view/', HodViews.save_marks_view, name='save_marks_endpoint'),
        path('delete_result_endpoint/', HodViews.delete_result_endpoint, name='delete_result_endpoint'),              
        path('add_announcement/', HodViews.add_announcement, name='add_announcement'),
        path('delete_announcement/', HodViews.delete_announcement, name='delete_announcement'),
        path('staff_announcements/', HodViews.staff_announcements, name='staff_announcements'),
        path('fetch_read_count/', HodViews.fetch_read_count, name='fetch_read_count'),       
        path('edit_announcement/', HodViews.edit_announcement, name='edit_announcement'),
        path('fetch_students_for_announcement/', HodViews.fetch_students_for_announcement, name='fetch_students_for_announcement'),
        path('student-results/', HodViews.student_results_view, name='student_results'),
        path('exam-types/', HodViews.exam_type_list, name='exam_type_list'),
        path('exam_type_to_view_class/<int:exam_type_id>/', HodViews.exam_type_to_view_class, name='exam_type_to_view_class'),
        path('view_student_to_add_result/<int:exam_type_id>/<str:class_name>/', HodViews.view_student_to_add_result, name='view_student_to_add_result'),
        
        path('students/', HodViews.manage_student, name='manage_student'),        
        path('manage_exam_type/', HodViews.manage_exam_type, name='manage_exam_type'),
        path('manage_subject/', HodViews.manage_subject, name='manage_subject'),
        path('manage_result/', HodViews.manage_result, name='manage_result'),
        path('update_student_status/', HodViews.update_student_status, name='update_student_status'),
        path('students_wise_result_page/', HodViews.students_wise_result_page, name='students_wise_result_page'),
        path('student_subject_wise_result/', HodViews.student_subject_wise_result, name='student_subject_wise_result'),
        path('student_subject_wise_result_page/<int:student_id>/', HodViews.student_subject_wise_result_page, name='student_subject_wise_result_page'),
       
        # delete urls 
        path('delete_student/', Delete.delete_student, name='delete_student'),
        path('delete_subject/<int:subject_id>/', Delete.delete_subject, name='delete_subject'),
        path('delete_exam_type/<int:exam_id>/', Delete.delete_exam_type, name='delete_exam_type'),
        
        
        # imports urls 
         path('import_student_records', imports.import_student_records, name='import_student_records'),
         path('import_subject_records', imports.import_subject_records, name='import_subject_records'),
         path('import_exam_type_records', imports.import_exam_type_records, name='import_exam_type_records'),
         path('import_subject_wise_result/<int:exam_type_id>/', imports.import_subject_wise_result, name='import_subject_wise_result'),
       
    
]