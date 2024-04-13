
from django.urls import  include, path
from . import views

urlpatterns = [
        path('',views.ShowLogin, name="login"),
        path('accounts/', include('django.contrib.auth.urls')), 
        path('landing_page',views.landing_page, name="landing_page"),    
        path('dologin',views.DoLogin, name="DoLogin"),    
        path('logout_user', views.logout_user, name='logout_user'), 
      
    
]