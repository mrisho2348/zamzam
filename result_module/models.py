from decimal import Decimal
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save,post_delete
from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.utils import timezone
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
    is_active = models.BooleanField(default=True)

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

class Announcement(models.Model):
    title = models.CharField(max_length=100)
    current_class = models.CharField(max_length=100) 
    content = models.TextField()
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
    current_class = models.CharField(max_length=100)   
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10)    
    phone_number = models.CharField(max_length=20)     
    address = models.CharField(max_length=200,null=True, blank=True)  
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

class Subject(models.Model):
    id = models.AutoField(primary_key=True)    
    subject_name = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    def __str__(self):
        return f"{self.subject_name}"
    

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

    if exam_results.count() >= 7:
        # Calculate the seven subjects with the highest scores
        sorted_subjects = sorted(exam_results, key=lambda x: x.marks, reverse=True)[:7]
        seven_best_subjects = [subject.subject.subject_name for subject in sorted_subjects]

        # Calculate total grade points
        total_grade_points = sum(calculate_grade(subject.marks) for subject in sorted_subjects)

        # Calculate division based on total grade points
        if 7 <= total_grade_points <= 17:
            division = "Division 1"
        elif 18 <= total_grade_points <= 21:
            division = "Division 2"
        elif 22 <= total_grade_points <= 24:
            division = "Division 3"
        elif 26 <= total_grade_points <= 29:
            division = "Division 4"
        else:
            division = "Division 0"

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
        
        

@receiver(post_save, sender=StudentExamInfo)
@receiver(post_delete, sender=StudentExamInfo)
def update_student_position(sender, instance, **kwargs):
    # Retrieve all students with the same current class and exam type
    students = StudentExamInfo.objects.filter(
        selected_class=instance.selected_class,
        exam_type=instance.exam_type,
    ).order_by('total_grade_points')  # Order by total_grade_points in ascending order

    # Update the positions based on total_grade_points
    for index, student in enumerate(students, start=1):
        student_position, created = StudentPositionInfo.objects.get_or_create(
            student=student.student,
            exam_type=student.exam_type,
            current_class=student.selected_class,
        )
        student_position.position = index
        student_position.save() 
        
     
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 1:  # HOD
            AdminHOD.objects.create(admin=instance)
       

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == 1:
        instance.admin_hod.save()
        