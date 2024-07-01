from django.contrib.auth.models import Group
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from users.models import User

class UserAdmin(BaseUserAdmin):
    list_filter = ('email',)
    list_display = ('first_name', 'last_name', 'email', 'is_landlord', 'is_tenant')
    fieldsets = (
        (None, {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'is_active', 'is_admin')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'email', 'password1', 'password2', 'is_staff', 'is_superuser', 'is_active', 'is_admin'),
        }),
    )
    ordering = ('email',)
    filter_horizontal = ()        

admin.site.register(User, UserAdmin)
admin.site.unregister(Group)  # Optional: Unregister Group if not needed
