from decimal import Decimal
import json
import logging
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save,post_delete
from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.utils import timezone
from django.db.models import DecimalField
from django.db.models import Max
from django.db.models import Sum
from django.core.exceptions import ObjectDoesNotExist
# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, user_type=1, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, user_type=user_type, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 1)  # Set the default user_type for superusers
        return self.create_user(username, email, password, **extra_fields)
    
        
class CustomUser(AbstractUser):
    user_type_data = (
        (1, "AdminHOD"),
       
    )
    user_type = models.CharField(default=1, choices=user_type_data, max_length=15)
    is_active = models.BooleanField(default=False)

    # Provide unique related_name values
    groups = models.ManyToManyField(
        "auth.Group",
        verbose_name="Groups",
        blank=True,
        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
        related_name="customuser_groups",  # Add a unique related_name for groups
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        verbose_name="User permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        related_name="customuser_user_permissions",  # Add a unique related_name for user_permissions
        related_query_name="user",
    )

    objects = CustomUserManager()

    def __str__(self):
        return self.username

class AdminHOD(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='admin_hod')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

ADDRESS_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),  
    ]

CLASS_CHOICES = [
        ('Form One', 'Form One'),
        ('Form Two', 'Form Two'),
        ('Form Three', 'Form Three'),
        ('Form Four', 'Form Four'),
    ]
class Staffs(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)   
    middle_name = models.TextField(blank=True)
    address = models.TextField(blank=True)
    gender =  models.CharField(max_length=100, choices=ADDRESS_CHOICES, blank=True)   
    date_of_birth = models.DateField(blank=True, default='2000-01-01')
    date_of_employment = models.DateField(blank=True, default='2000-01-01')
    phone_number = models.CharField(max_length=20, blank=True)
    current_class = models.CharField(max_length=20, choices=CLASS_CHOICES, blank=True)
    staff_role = models.CharField(max_length=20, blank=True,default="Staff")
    profile_pic = models.FileField(upload_to='staff_profile_pic',null=True, blank=True) 
    subjects = models.ManyToManyField('Subject', related_name='staffs_subjects', blank=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    
    objects = models.Manager()
    
    def get_full_name(self):
        return f"{self.admin.first_name} {self.middle_name} {self.admin.last_name}"

class Announcement(models.Model):
    title = models.CharField(max_length=100)
    current_class = models.CharField(max_length=20, choices=CLASS_CHOICES, blank=True)
    content = models.TextField()
    announcement_file = models.FileField(upload_to='announcement',null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(AdminHOD, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = models.Manager() 
    
    def __str__(self):
        return self.title



class AnnouncementForStudents(models.Model):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE)
    student = models.ForeignKey('Students', on_delete=models.CASCADE)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()   
    class Meta:
        unique_together = ('announcement', 'student')

    def __str__(self):
        return f"{self.announcement.title} for {self.student.full_name}"

class Students(models.Model):
    id = models.AutoField(primary_key=True)
    registration_number = models.CharField(max_length=30,unique=True)   
    full_name = models.CharField(max_length=100)   
    current_class = models.CharField(max_length=20, choices=CLASS_CHOICES, blank=True)  
    date_of_birth = models.DateField(blank=True, null=True)
    gender =  models.CharField(max_length=100, choices=ADDRESS_CHOICES, blank=True)      
    phone_number = models.CharField(max_length=20)     
    address = models.CharField(max_length=200,null=True, blank=True)  
    profile_pic = models.FileField(upload_to='student_profile_pic',null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()    
    def __str__(self):
        return self.full_name
    
class ExamType(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()  # Additional field for a description of the exam type
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()  # Additional field for the creation date
    # Other fields...
    def __str__(self):
        return f"{self.name}"
    
class SujbectWiseResults(models.Model):
    student = models.ForeignKey(Students, on_delete=models.CASCADE)    
    history_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, default=0)
    english_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, default=0)
    biology_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, default=0)
    arabic_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, default=0)
    physics_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, default=0)
    mathematics_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, default=0)
    chemistry_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, default=0)
    civics_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, default=0)
    geography_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, default=0)
    kiswahili_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, default=0)
    edk_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, default=0)
    computer_application_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, default=0)
    commerce_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, default=0)
    book_keeping_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, default=0)
    date_of_exam = models.DateField(auto_now=True) 
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE)
    selected_class = models.CharField(max_length=255, null=True, blank=True)   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    
    
class Subject(models.Model):
    id = models.AutoField(primary_key=True)    
    subject_name = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    def __str__(self):
        return f"{self.subject_name}"
  
  
class Attendance(models.Model):
    id = models.AutoField(primary_key=True)  
    subject_id = models.ForeignKey(Subject,on_delete=models.DO_NOTHING)
    attendance_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)   
    updated_at = models.DateTimeField(auto_now=True)  
    objects = models.Manager()


class AttendanceReport(models.Model):
    id = models.AutoField(primary_key=True)  
    student_id = models.ForeignKey(Students,on_delete=models.DO_NOTHING)
    attendance_id = models.ForeignKey(Attendance,on_delete=models.DO_NOTHING)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  
    objects = models.Manager()  
    
class LeaveReportStudent(models.Model):
     id = models.AutoField(primary_key=True)     
     student_id = models.ForeignKey(Students,on_delete=models.DO_NOTHING)
     leave_date = models.DateTimeField(auto_now_add=True)
     leave_message = models.TextField()
     leave_status = models.IntegerField(default=0)    
     created_at = models.DateTimeField(auto_now_add=True)
     updated_at = models.DateTimeField(auto_now=True)  
     objects = models.Manager()
     
     
class ClassAttendance(models.Model):
    id = models.AutoField(primary_key=True)  
    current_class = models.CharField(max_length=15)  # Ex   
    attendance_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)   
    updated_at = models.DateTimeField(auto_now=True)  
    objects = models.Manager()
        
class StudentClassAttendance(models.Model):
    id = models.AutoField(primary_key=True)  
    attendance = models.ForeignKey(ClassAttendance, on_delete=models.CASCADE)
    student = models.ForeignKey(Students, on_delete=models.DO_NOTHING)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  
    objects = models.Manager()        
     
class LeaveReportStaffs(models.Model):
     id = models.AutoField(primary_key=True)     
     staff_id = models.ForeignKey(Staffs,on_delete=models.DO_NOTHING)
     leave_date = models.DateTimeField(auto_now_add=True)
     leave_message = models.TextField()
     leave_status = models.IntegerField(default=0)    
     created_at = models.DateTimeField(auto_now_add=True)
     updated_at = models.DateTimeField(auto_now=True)   
     objects = models.Manager()  
     

class FeedBackStudent(models.Model):
     id = models.AutoField(primary_key=True)     
     student_id = models.ForeignKey(Students,on_delete=models.DO_NOTHING)
     feedback = models.CharField(max_length=255)     
     feedback_reply = models.TextField()    
     created_at = models.DateTimeField(auto_now_add=True)
     updated_at = models.DateTimeField(auto_now=True)
     objects = models.Manager()
     
     
class FeedBackStaff(models.Model):
     id = models.AutoField(primary_key=True)     
     staff_id = models.ForeignKey(Staffs,on_delete=models.DO_NOTHING)
     feedback = models.CharField(max_length=255)     
     feedback_reply = models.TextField()    
     created_at = models.DateTimeField(auto_now_add=True)
     updated_at = models.DateTimeField(auto_now=True)   
     objects = models.Manager()        

class Result(models.Model):
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE)
    marks = models.DecimalField(max_digits=5, decimal_places=2)
    date_of_exam = models.DateField()
    selected_class = models.CharField(max_length=255, null=True, blank=True)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def calculate_performance(self):
        if self.total_marks:
            return (self.marks / self.total_marks) * 100
        else:
            return None

    def determine_grade(self):
        if self.marks >= Decimal('75.00'):
            return 'A'
        elif self.marks >= Decimal('65.00'):
            return 'B'
        elif self.marks >= Decimal('45.00'):
            return 'C'
        elif self.marks >= Decimal('30.00'):
            return 'D'
        else:
            return 'F'

    def determine_pass_fail(self):
        pass_threshold = 45  # Adjust this threshold as needed
        if self.marks >= pass_threshold:
            return 'Pass'
        else:
            return 'Fail'

    

         
class StudentExamInfo(models.Model):   # ... (other fields)
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE)
    division = models.CharField(max_length=50, null=True, blank=True)
    selected_class = models.CharField(max_length=255, null=True, blank=True) 
    total_grade_points = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0)
    best_subjects = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    
    def __str__(self):
        return f"{self.student} - {self.exam_type}"       
    

class StudentPositionInfo(models.Model):
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE)
    position = models.IntegerField(null=True, blank=True)
    current_class = models.CharField(max_length=100,default="Form I")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return f"{self.student} - {self.exam_type} - Position: {self.position}"    
   
   
# Define the signal handler
@receiver(post_save, sender=Result)
@receiver(post_delete, sender=Result)
def update_student_exam_info(sender, instance, **kwargs):
    # Define a function to calculate the grade based on the provided logic
    def calculate_grade(score):
        if score >= 75:
            return 1
        elif score >= 65:
            return 2
        elif score >= 45:
            return 3
        elif score >= 30:
            return 4
        else:
            return 5

    # Check if there are at least seven subjects with results for the student
    student = instance.student
    current_class = instance.selected_class
    exam_type = instance.exam_type

    exam_results = Result.objects.filter(
        student=student,
        exam_type=exam_type,
        selected_class=current_class
    )

    subject_count = exam_results.count()
    if subject_count >= 7:
        # Calculate the seven subjects with the highest scores
        sorted_subjects = sorted(exam_results, key=lambda x: x.marks, reverse=True)[:7]
        seven_best_subjects = [subject.subject.subject_name for subject in sorted_subjects]

        # Calculate total grade points
        total_grade_points = sum(calculate_grade(subject.marks) for subject in sorted_subjects)

        # Calculate division based on total grade points
        if 7 <= total_grade_points <= 17:
            division = "I"
        elif 18 <= total_grade_points <= 21:
            division = "II"
        elif 22 <= total_grade_points <= 24:
            division = "III"
        elif 26 <= total_grade_points <= 29:
            division = "IV"
        else:
            division = "0"
    else:
        # If less than seven subjects, mark division as incomplete
        division = -1
        total_grade_points = -1
        seven_best_subjects = []

    # Update or create StudentExamInfo instance
    student_exam_info, created = StudentExamInfo.objects.get_or_create(
        student=student,
        exam_type=exam_type,
        selected_class=current_class,
    )

    student_exam_info.division = division
    student_exam_info.total_grade_points = total_grade_points
    student_exam_info.best_subjects = seven_best_subjects
    student_exam_info.save()

        
class ExamMetrics(models.Model):
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE)
    selected_class = models.CharField(max_length=255, null=True, blank=True)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0)
    average = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0)
    grade = models.CharField(max_length=1, null=True, blank=True)
    remark = models.CharField(max_length=10, null=True, blank=True)  # Add remark field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return f"{self.student} - {self.exam_type}"         

# Signal handler to update student positions based on total marks
@receiver(post_save, sender=ExamMetrics)
@receiver(post_delete, sender=ExamMetrics)
def update_student_position(sender, instance, **kwargs):
    # Retrieve all students with the same current class and exam type
    students = ExamMetrics.objects.filter(
        selected_class=instance.selected_class,
        exam_type=instance.exam_type,
    ).order_by('-total_marks', 'created_at')  # Order by total_marks in descending order and created_at for tie-breaker

    # Update the positions based on total_marks
    prev_marks = None
    prev_position = None
    for index, student in enumerate(students, start=1):
        if student.total_marks != prev_marks:
            position = index
        else:
            position = prev_position
        student_position, created = StudentPositionInfo.objects.get_or_create(
            student=student.student,
            exam_type=student.exam_type,
            current_class=student.selected_class,
        )
        student_position.position = position
        student_position.save()
        prev_marks = student.total_marks
        prev_position = position
        
     
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 1:  # HOD
            AdminHOD.objects.create(admin=instance)            
        elif instance.user_type == 2:  # Staff
            Staffs.objects.create(admin=instance)    
       

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == 1:
        instance.admin_hod.save()
    elif instance.user_type == 2:
        instance.staffs.save()    

    
    
    
@receiver(post_save, sender=Result)
@receiver(post_delete, sender=Result)
def update_exam_metrics_on_create_or_delete(sender, instance, **kwargs):
    update_exam_metrics(instance)

@receiver(post_save, sender=Result)
def update_exam_metrics_on_update(sender, instance, **kwargs):
    if not kwargs.get('created'):
        update_exam_metrics(instance)

def update_exam_metrics(instance):
    student = instance.student
    exam_type = instance.exam_type
    selected_class = instance.selected_class

    exam_results = Result.objects.filter(
        student=student,
        exam_type=exam_type,
        selected_class=selected_class
    )

    total_marks = exam_results.aggregate(total_marks=Sum('marks'))['total_marks'] or 0

    total_subjects_count = exam_results.values('subject').distinct().count()
    average = total_marks / total_subjects_count if total_subjects_count > 0 else 0

    grade = calculate_grade(average)
    remark = calculate_remark(grade)

    exam_metrics, created = ExamMetrics.objects.get_or_create(
        student=student,
        exam_type=exam_type,
        selected_class=selected_class,
    )

    exam_metrics.total_marks = total_marks
    exam_metrics.average = average
    exam_metrics.grade = grade
    exam_metrics.remark = remark  # Assign remark
    exam_metrics.save()    
    
# Function to calculate grade based on average marks
def calculate_grade(average):
    if average >= 75:
        return 'A'
    elif average >= 65:
        return 'B'
    elif average >= 45:
        return 'C'
    elif average >= 30:
        return 'D'
    else:
        return 'F'

# Function to calculate remark based on grade
def calculate_remark(grade):
    if grade == 'F':
        return 'FAILED'
    else:
        return 'PASS'
    
   

@receiver(post_save, sender=SujbectWiseResults)
def fill_result_model(sender, instance, created, **kwargs):
    if created:
        student = instance.student
        exam_type = instance.exam_type
        selected_class = instance.selected_class
        date_of_exam = instance.date_of_exam 
        
        subject_fields = {
        'Chemistry': 'chemistry_score',
        'History': 'history_score',
        'English': 'english_score',
        'Biology': 'biology_score',
        'Arabic': 'arabic_score',
        'Physics': 'physics_score',
        'Mathematics': 'mathematics_score',
        'Geography': 'geography_score',
        'Civics': 'civics_score',
        'Kiswahili': 'kiswahili_score',
        'EDK': 'edk_score',
        'Computer Application': 'computer_application_score',
        'Commerce': 'commerce_score',
        'Book Keeping': 'book_keeping_score',
    }    
        # Iterate through the subject fields
        for field_name, subject_field in subject_fields.items():
            score = getattr(instance, subject_field)
            if score is not None:
                # Get the subject object
                try:
                    subject = Subject.objects.get(subject_name=field_name)
                except ObjectDoesNotExist:
                    # Log the error or handle it as needed
                    print(f"Subject '{field_name}' does not exist.")
                    continue
                
                # Create or update the Result object
                Result.objects.update_or_create(
                    student=student,
                    subject=subject,
                    exam_type=exam_type,
                    date_of_exam=date_of_exam,
                    selected_class=selected_class,
                    defaults={'marks': score, 'total_marks': 100}
                )
                

                