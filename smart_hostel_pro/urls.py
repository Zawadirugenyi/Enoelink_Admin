from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('users/', include('users.urls')),
    path('api/', include('hostel.urls')),

    # Root URL points to your hostel app (adjust if needed)
    path('', include('hostel.urls')),  
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Admin URLs with optional language prefix
if 'django.middleware.locale.LocaleMiddleware' in settings.MIDDLEWARE:
    urlpatterns += i18n_patterns(
        path('admin/', admin.site.urls),
    )
else:
    urlpatterns += [
        path('admin/', admin.site.urls),
    ]

# Language switching endpoint
urlpatterns += [
    path('set_language/', include('django.conf.urls.i18n')),
]
