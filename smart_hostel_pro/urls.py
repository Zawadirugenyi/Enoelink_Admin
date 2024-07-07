from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('users/', include('users.urls')),
    path('api/', include('hostel.urls')), 
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Include admin URLs within the i18n_patterns
if 'django.middleware.locale.LocaleMiddleware' in settings.MIDDLEWARE:
    urlpatterns += i18n_patterns(
        path('admin/', admin.site.urls),
        # other paths if needed
    )
else:
    urlpatterns += [
        path('admin/', admin.site.urls),
    ]

urlpatterns += [
    path('set_language/', include('django.conf.urls.i18n')),
]


