from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin

from result_module.models import Staffs

class LoginCheckMiddleWare(MiddlewareMixin):    
    def process_view(self, request, view_func, view_args, view_kwargs):
        modulename = view_func.__module__
        user = request.user
         # Allow access to login/logout pages and authentication-related views
        if (request.path == reverse("login") or
            request.path == reverse("DoLogin") or
            request.path == reverse("student_login") or
            request.path == reverse("student_dologin") or
            request.path == reverse("landing_page") or
            request.path == reverse("logout_user") or
            modulename.startswith("django.contrib.auth.views")):
            return None
        
        student_id = request.session.get('student_id')
        if student_id:
                # Redirect to student home page if session variable set
                 if modulename == "result_module.StudentView"  or modulename == "django.views.static":
                    pass              
                 else:
                    return HttpResponseRedirect(reverse("student_home"))
                   
        elif user.is_authenticated:          
            # Check for admin user
            if user.user_type == "1":
                # Allow specific views and static pages for AdminHOD
                if modulename == "result_module.HodViews" or \
                   modulename == "result_module.views" or \
                   modulename == "django.views.static" or \
                   modulename == "result_module.Delete":
                    pass              
                else:
                    return HttpResponseRedirect(reverse("admin_home"))
                
            # Check for staff user
            elif user.user_type == "2":
                staff = Staffs.objects.filter(admin=user).first()
                
                if staff:
                    if staff.staff_role == "Accountant":
                        allowed_modules = ["result_module.Financial"]
                        if modulename in allowed_modules:
                            pass
                        else:    
                            return HttpResponseRedirect(reverse("result_module:accountant_home"))
                    elif staff.staff_role == "Secretary":
                        allowed_modules = ["result_module.Secretary"]
                        if modulename in allowed_modules:
                            pass
                        else:    
                            return HttpResponseRedirect(reverse("secretary_home"))
                    else:
                        allowed_modules = [
                            "result_module.StaffImports",
                            "result_module.StaffView",
                            "result_module.views",
                            "django.views.static",
                        ]
                        if modulename in allowed_modules:
                            pass
                        else:
                            return HttpResponseRedirect(reverse("staff_home"))     
            
            # Check for student user
            
                
        else:
            # Allow specific paths during login/logout processes
            allowed_paths = [reverse("login"), reverse("DoLogin"), reverse("student_dologin"), reverse("student_login"), reverse("logout_user")]
            if request.path in allowed_paths or modulename == "django.contrib.auth.views":
                pass
            else:
                return HttpResponseRedirect(reverse("landing_page"))
            
        return HttpResponseRedirect(reverse("landing_page"))    