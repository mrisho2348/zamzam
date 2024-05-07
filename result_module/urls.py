
from django.urls import  include, path
from . import views

urlpatterns = [
        path('login',views.ShowLogin, name="login"),
        path('accounts/', include('django.contrib.auth.urls')), 
        path('',views.landing_page, name="landing_page"),    
        path('add_staff',views.add_staff, name="add_staff"),    
        path('add_staff_save',views.add_staff_save, name="add_staff_save"),    
        path('activate/<str:user_id>/<str:activation_key>/', views.activate_account, name='activate_account'),  
        path('dologin',views.DoLogin, name="DoLogin"),    
        path('logout_user', views.logout_user, name='logout_user'), 

]