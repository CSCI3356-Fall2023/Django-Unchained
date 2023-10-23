from django.db import models
from django.contrib.auth.models import User

# abstract class

# user profile model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    USER_TYPE_CHOICES = [
        ('student', 'Student'),
        ('admin', 'Admin'),
    ]
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    
    def get_full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

# system state model
class SystemState(models.Model):
     state = models.BooleanField()
     updated_at = models.DateTimeField(auto_now=True)

# common abstract class
class Person(models.Model):
    # common fields for students and admin
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=255)

    class Meta:
        abstract = True  

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
    
# admin class which inherits from person
class Admin(Person):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=255)

