from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from django.conf import settings

class CustomUserManager(BaseUserManager):
    def create_user(self, email,name,password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name,**extra_fields)
        user.save(using=self._db)
        return user
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class Person(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = [
        ('student', 'Student'),
        ('admin', 'Admin'),
    ]
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, default=email)
    name = models.CharField(max_length=255, blank=True)
    department = models.CharField(max_length=255, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_extra_info_filled_out = models.BooleanField(default=False)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, blank=True)

    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    def is_extra_info_filled_out(self):
        return bool(self.is_active)



class SystemState(models.Model):
    state = models.BooleanField()
    updated_at = models.DateTimeField(auto_now=True)

class Student(Person):
    major_1 = models.CharField(max_length=255, blank=True, null=True)
    major_2 = models.CharField(max_length=255, blank=True, null=True)
    major_3 = models.CharField(max_length=255, blank=True, null=True)
    minor_1 = models.CharField(max_length=255, blank=True, null=True)
    minor_2 = models.CharField(max_length=255, blank=True, null=True)
    eagle_id = models.CharField(max_length=50, unique=True)
    GRADUATION_SEMESTER = [
        ('Spring2024', 'Spring 2024'),
        ('Fall2024', 'Fall 2024'),
        ('Spring2025', 'Spring 2025'),
        ('Fall2025', 'Fall 2025'),
        ('Spring2026', 'Spring 2026'),
        ('Fall2026', 'Fall 2026'),
        ('Spring2027', 'Spring 2027'),
        ('Fall2027', 'Fall 2027'),    
    ]
    graduation_semester = models.CharField(max_length=10, choices=GRADUATION_SEMESTER)
    def update_extra_info(self, **kwargs):
        for field, value in kwargs.items():
            setattr(self, field, value)
        self.extra_info_filled_out = True  
        self.is_active = True
        self.save()

class Admin(Person):
    def update_extra_info(self, **kwargs):
        for field, value in kwargs.items():
            setattr(self, field, value)
        self.extra_info_filled_out = True 
        self.is_staff = True 
        self.is_active = True
        self.is_superuser = True
        self.save()

class Course(models.Model):
    course_id = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.title