# users/urls.py
from django.urls import path
from .views import SendBypassCodeView
from .views import check_user, SignInUserView, LoginUserView, LogoutUserView

urlpatterns = [
    path('signup/', SignInUserView.as_view(), name='signup'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('logout/', LogoutUserView.as_view(), name='logout'),
    path('check_user/', check_user, name='check_user'),
    path('send-bypass-code/', SendBypassCodeView.as_view(), name='send-bypass-code'),
]
