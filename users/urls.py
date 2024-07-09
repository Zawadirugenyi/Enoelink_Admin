from django.urls import path
from .views import SignInUserView, LoginUserView, LogoutUserView

urlpatterns = [
    path('signup/', SignInUserView.as_view(), name='signup'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('logout/', LogoutUserView.as_view(), name='logout'),
]
