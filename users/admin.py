from django.contrib.auth.models import Group
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import User

# Register your models here.
class UserView(UserAdmin):
    list_filter = ('email',)
    list_display = ('first_name', 'last_name',
            'email','is_landlord','is_tenant')
    fieldsets = (
        (None, {'fields': ('first_name', 'last_name',
            'email', 'phone_number','password')}),
                )
    add_fieldsets = (
        (None, {'fields': ('first_name','last_name','email','password')}),
    )

    ordering = ('email',)
    filter_horizontal = ()        


admin.site.register(User, UserView)