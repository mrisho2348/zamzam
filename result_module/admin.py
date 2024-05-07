from django.contrib import admin

from result_module.models import Announcement, AnnouncementForStudents, ExamType, Staffs, Students, Subject, SujbectWiseResults
from django.utils.html import format_html
# Register your models here.

class StaffsAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'gender', 'date_of_birth', 'date_of_employment', 'staff_role', 'phone_number','profile_pic_display')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('admin','middle_name', 'address', 'gender')
        }),
        ('Personal Info', {
            'fields': ('date_of_birth', 'date_of_employment', 'phone_number', 'profile_pic')
        }),
        ('Additional Info', {
            'fields': ('current_class', 'staff_role', 'subjects')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    def profile_pic_display(self, obj):
        if obj.profile_pic:
            return format_html('<img src="{}" style="max-width:200px; max-height:200px"/>'.format(obj.profile_pic.url))
        else:
            return '(No image)'
    profile_pic_display.allow_tags = True
    profile_pic_display.short_description = 'Profile Pic'
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'

admin.site.register(Staffs, StaffsAdmin)

class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'current_class', 'created_at', 'created_by')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('title', 'current_class', 'content', 'announcement_file')
        }),
        ('Metadata', {
            'fields': ('created_at', 'created_by', 'updated_at'),
            'classes': ('collapse',)  # Optional: hides this section by default
        }),
    )

admin.site.register(Announcement, AnnouncementAdmin)


class StudentsAdmin(admin.ModelAdmin):
    list_display = ('registration_number', 'full_name', 'current_class', 'date_of_birth', 'gender', 'phone_number', 'address','profile_pic_display', 'is_active', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('registration_number', 'full_name', 'current_class', 'date_of_birth', 'gender', 'phone_number', 'address', 'profile_pic', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    def profile_pic_display(self, obj):
        if obj.profile_pic:
            return format_html('<img src="{}" style="max-width:200px; max-height:200px"/>'.format(obj.profile_pic.url))
        else:
            return '(No image)'
    profile_pic_display.allow_tags = True
    profile_pic_display.short_description = 'Profile Pic'
admin.site.register(Students, StudentsAdmin)

class ExamTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

admin.site.register(ExamType, ExamTypeAdmin)


class SubjectWiseResultsAdmin(admin.ModelAdmin):
    list_display = (
        'student', 'exam_type', 'selected_class', 'history_score', 'english_score', 'biology_score', 
        'arabic_score', 'physics_score', 'mathematics_score', 'chemistry_score', 'civics_score', 
        'geography_score', 'kiswahili_score', 'edk_score', 'computer_application_score', 
        'commerce_score', 'date_of_exam', 'book_keeping_score', 'created_at', 'updated_at'
    )
    readonly_fields = ('created_at', 'updated_at', 'date_of_exam')

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + (
                'student', 'exam_type', 'selected_class', 
                'history_score', 'english_score', 'biology_score', 
                'arabic_score', 'physics_score', 'mathematics_score', 
                'chemistry_score', 'civics_score', 'geography_score', 
                'kiswahili_score', 'edk_score', 'computer_application_score', 
                'commerce_score', 'date_of_exam', 'book_keeping_score'
            )
        return self.readonly_fields

admin.site.register(SujbectWiseResults, SubjectWiseResultsAdmin)

class SubjectAdmin(admin.ModelAdmin):
    list_display = ('subject_name', 'is_active', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('subject_name', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

admin.site.register(Subject, SubjectAdmin)