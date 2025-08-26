from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UsersManager(BaseUserManager):

    def create_user(self, first_name, last_name, email, phone_number, password=None):
        """
        Creates and saves a regular User with the given details.
        """
        if not first_name:
            raise ValueError("First name must be included")
        if not last_name:
            raise ValueError("Last name must be included")
        if not email:
            raise ValueError("Please add email address")
        if not phone_number:
            raise ValueError("Please add a phone number")

        email = self.normalize_email(email)
        user = self.model(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
        )
        if password:
            user.set_password(password)
        else:
            raise ValueError("User must have a password")
        
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, email, phone_number, password):
        """
        Creates and saves a superuser with the given details.
        """
        user = self.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            password=password
        )
        user.is_admin = True
        user.is_staff = True      # Must be True for admin login
        user.is_superuser = True  # Must be True for admin login
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=50, null=False)
    last_name = models.CharField(max_length=50, null=False)
    email = models.EmailField(verbose_name="email", max_length=100, unique=True)
    phone_number = models.BigIntegerField(unique=True, null=False)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_landlord = models.BooleanField(default=False)
    is_tenant = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['phone_number', 'first_name', 'last_name']

    objects = UsersManager()

    def __str__(self):
        return self.email

    # These two methods are required for admin access
    def has_perm(self, perm, obj=None):
        return self.is_admin  # Only admin users have permissions
    
    def has_module_perms(self, app_label):
        return self.is_admin
