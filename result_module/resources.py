from import_export import resources
from .models import  ExamType, Students, Subject, SujbectWiseResults

class StudentResources(resources.ModelResource):
    class Meta:
        model = Students
class ExamTypeResources(resources.ModelResource):
    class Meta:
        model = ExamType
class SubjectResources(resources.ModelResource):
    class Meta:
        model = Subject
class SujbectWiseResultsResources(resources.ModelResource):
    class Meta:
        model = SujbectWiseResults

        
