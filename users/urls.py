from django.urls import path
from  . import views

urlpatterns = [
    path('signup/', views.SignInUserView.as_view(), name='signup'), 
    path('login/', views.LoginUserView.as_view(), name='user_login'),
    path('logout/', views.LogoutUserView.as_view(), name='user_logout'),
]