
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import  redirect, render
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import logout,login
from result_module.emailBackEnd import EmailBackend
from result_module.models import CustomUser, Students, Subject
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode

def logout_user(request):
  logout(request)
  return HttpResponseRedirect(reverse("landing_page"))

def ShowLogin(request):  
  return render(request,'login.html')

def landing_page(request):  
  return render(request,'index.html')

def add_staff(request):  
    subjects = Subject.objects.all()
    return render(request,"add_staff.html",{"subjects":subjects})





def add_staff_save(request):
    if request.method == "POST":
        try:
            # Extract form data
            first_name = request.POST.get('first_name')
            middle_name = request.POST.get('middle_name')
            last_name = request.POST.get('last_name')
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            current_class = request.POST.get('current_class')
            subjects = request.POST.getlist('subject')
            address = request.POST.get('address')
            gender = request.POST.get('gender')
            dob = request.POST.get('dob')
            doe = request.POST.get('doe')
            phone = request.POST.get('phone')
            
            # Define accepted file formats
            accepted_image_formats = ['image/jpeg', 'image/jpg', 'image/png']         

            # Define maximum file size in bytes (5MB)
            max_file_size = 5 * 1024 * 1024
            try:
                # Save the staff's profile picture
                staff_photo_url = None
                staff_photo = request.FILES.get('staff_photo')
                if staff_photo and (staff_photo.content_type not in accepted_image_formats or staff_photo.size > max_file_size):
                    messages.error(request, 'File must be PNG, JPEG, or JPG and should not exceed 5MB.')
                    return redirect("add_staff")               

                fs = FileSystemStorage()
                # Save the staff's profile picture using FileSystemStorage
                if staff_photo:
                    staff_photo_name = fs.save('staff_profile_pic/' + staff_photo.name, staff_photo)
                    staff_photo_url = fs.url(staff_photo_name)  
                                
                if CustomUser.objects.filter(username=username).exists():
                    messages.error(request, 'Username already taken try another.')
                    return redirect("add_staff")
            
                if CustomUser.objects.filter(email=email).exists():
                    messages.error(request, 'Email already taken try another email.')
                    return redirect("add_staff")
                
                user = CustomUser.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name, user_type=2)
              
                staff = user.staffs         
                staff.middle_name = middle_name
                staff.profile_pic = staff_photo_url
                staff.address = address
                staff.current_class = current_class
                staff.gender = gender
                staff.date_of_birth = dob
                staff.date_of_employment = doe
                staff.phone_number = phone      
                # Save the staff record
                staff.save()
                # Assign subjects to the staff
                staff.subjects.set(subjects)
                
                # Send verification email
                current_site = get_current_site(request)
                mail_subject = 'Activate your Zam Zam Islamic School account.'
                message = render_to_string('verification_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })
                to_email = email
                send_mail(mail_subject, message, 'mrishohamisi2348@gmail.com', [to_email])
                
                # Redirect to the verification page
                return render(request, 'verify_email.html', {'email': email})
                
            except Exception as e:
                messages.error(request, f"Error saving staff record: {str(e)}")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

    return redirect("add_staff")


def activate_account(request, uidb64, token):
    try:
        # Decode the user ID from base64 and get the user
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    # Check if the user exists and the token is valid
    if user is not None and default_token_generator.check_token(user, token):
        # Update the user's account status to indicate verification
        user.is_active = True
        user.save()
        # Redirect the user to the login page
        return redirect('login')
    else:
        # Handle invalid activation link
        return HttpResponse('Activation link is invalid or expired.')
    

def DoLogin(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not allowed</h2>")
    else:
        user = EmailBackend.authenticate(request, request.POST.get("email"), request.POST.get("password"))
        if user is not None:
            if not user.is_active:
                messages.error(request, "Your account is not active. Please contact the administrator for support.")
                return HttpResponseRedirect(reverse("login"))

            login(request, user)
            if user.user_type == "1":
                return HttpResponseRedirect(reverse("admin_home"))
            elif user.user_type == "2":
                return HttpResponseRedirect(reverse("staff_home"))             
            else:
                return HttpResponseRedirect(reverse("login"))
        else:
            messages.error(request, "Invalid Login Details")
            return HttpResponseRedirect(reverse("login"))
    


