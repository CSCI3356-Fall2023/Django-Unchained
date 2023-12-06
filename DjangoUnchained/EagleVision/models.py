from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import random
import logging
import requests

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
   
class Admin(Person):
    pass

class Course(models.Model):
    course_id = models.CharField(max_length=255,unique =True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.CharField(max_length=255, default = '01/01/2023')
    schedule = models.CharField(max_length=255, default = 'none')
    instructor = models.CharField(max_length=255, default = 'none')
    requisite = models.CharField(max_length=255, default = 'none')
    department = models.CharField(max_length=255, default = 'none')
    courseIdentifier = models.CharField(max_length=255, default="none")
    max_students_on_watch = models.IntegerField(default=0)
    min_students_on_watch = models.IntegerField(default=0)
    
    def __str__(self):
        return self.title
    def getDepartment(self):
        return self.department
    def getSchedule(self):
        return self.schedule
    def getTimeSlot(self):
        return self.time_slot

class Section(models.Model):
    section_id = models.CharField(max_length=255, unique=True, default='')
    instructor = models.CharField(max_length=255, default='')
    title = models.CharField(max_length=255, default='')
    location = models.CharField(max_length=255, default='')
    currentSeats = models.DecimalField(max_digits=3, decimal_places=0, default=0)
    maxSeats = models.DecimalField(max_digits=3, decimal_places=0, default=0)
    courseid = models.CharField(max_length=255, default='')

    def change_seats(self):
        response = requests.get("http://localhost:8080/waitlist/waitlistregistrationgroups?courseOfferingId=" + self.courseid).json()
        for entry in response:
            for section in entry['activityOfferings']:
                if section['activityOffering']['id'] == self.section_id:
                    self.currentSeats = section['activitySeatCount']['used']
                    self.save()

class Watchlist(models.Model):
    user = models.ForeignKey(Person, on_delete=models.CASCADE)
    section= models.ForeignKey(Section, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)


class SystemSnapshot(models.Model):
    name = models.CharField(max_length=255)
    data = models.JSONField() 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name