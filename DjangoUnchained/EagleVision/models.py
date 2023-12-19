from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import random
import requests
from django.conf import settings

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
    DEPARTMENT = [
        ('MCAS', 'MCAS'),
        ('CSOM', 'CSOM'),
        ('CSON', 'CSON'),
        ('LYNCH', 'LYNCH'),
        ('LAW', 'LAW'),
        ('WOODS', 'WOODS'),
        ('STM', 'STM'),
        ('SSW', 'SSW'),
    ]
    department = models.CharField(max_length=10, choices=DEPARTMENT)
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


class Admin(Person):
    pass

class SystemState(models.Model):
    state = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

class Student(Person):
    MAJORS = [
        ('', 'Select a Major'),
        ('African and African Diaspora Studies', 'African and African Diaspora Studies'),
        ('Applied Physics', 'Applied Physics'),
        ('Art History', 'Art History'),
        ('Biochemistry', 'Biochemistry'),
        ('Biology', 'Biology'),
        ('Chemistry', 'Chemistry'),
        ('Classics', 'Classics'),
        ('Communication', 'Communication'),
        ('Computer Science', 'Computer Science'),
        ('Economics', 'Economics'),
        ('English', 'English'),
        ('Environmental Geoscience', 'Environmental Geoscience'),
        ('Environmental Studies', 'Environmental Studies'),
        ('Film Studies', 'Film Studies'),
        ('French', 'French'),
        ('Geological Sciences', 'Geological Sciences'),
        ('German Studies', 'German Studies'),
        ('Hispanic Studies', 'Hispanic Studies'),
        ('History', 'History'),
        ('Human-Centered Engineering', 'Human-Centered Engineering'),
        ('Independent', 'Independent'),
        ('International Studies', 'International Studies'),
        ('Islamic Civilization and Societies', 'Islamic Civilization and Societies'),
        ('Italian', 'Italian'),
        ('Linguistics', 'Linguistics'),
        ('Mathematics', 'Mathematics'),
        ('Music', 'Music'),
        ('Neuroscience','Neuroscience'),
        ('Philosophy', 'Philosophy'),
        ('Physics', 'Physics'),
        ('Political Science', 'Political Science'),
        ('Psychology', 'Psychology'),
        ('Russian', 'Russian'),
        ('Slavic Studies', 'Slavic Studies'),
        ('Sociology', 'Sociology'),
        ('Studio Art', 'Studio Art'),
        ('Theatre','Theatre'),
        ('Theology','Theology'),
        ('American Heritage', 'American Heritage'),
        ('Applied Psychology & Human Development', 'Applied Psychology & Human Development'),
        ('Elementary Education', 'Elementary Education'),
        ('Perspectives on Spanish America','Perspectives on Spanish America'),
        ('Secondary Education', 'Secondary Education'),
        ('Transformative Educational Studies', 'Transformative Educational Studies'),
        ('Accounting', 'Accounting'),
        ('Accounting for Finance and Consulting', 'Accounting for Finance and Consulting'),
        ('Business Analytics', 'Business Analytics'),
        ('Entrepreneurship', 'Entrepreneurship'),
        ('Finance','Finance'),
        ('General Management', 'General Management'),
        ('Management and Leadership', 'Management and Leadership'),
        ('Marketing','Marketing'),
        ('Operations Management', 'Operations Management'),
        ('Global Public Health and the Common Good','Global Public Health and the Common Good'),
        ('Nursing','Nursing'),
        ('Applied Liberal Arts','Applied Liberal Arts'),
        ('Interdisciplinary Studies','Interdisciplinary Studies'),
        ('Sustainability', 'Sustainability'),
        ('Business', 'Business'),
        ('Criminal and SocialJustice', 'Criminal and Social Justice'),
        ('Cybersecurity', 'Cybersecurity'),
        ('Information Systems', 'Information Systems'),
    ]
    major_1 = models.CharField(max_length=255, choices=MAJORS, blank=True, null=True)
    major_2 = models.CharField(max_length=255, choices=MAJORS, blank=True, null=True)
    major_3 = models.CharField(max_length=255, choices=MAJORS, blank=True, null=True)
    MINORS =[
        ('', 'Select a Minor'),
        ('Accounting for CPAs', 'Accounting for CPAs'),
        ('Accounting for Finance & Consulting', 'Accounting for Finance & Consulting'),
        ('African and African Diaspora Studies', 'African and African Diaspora Studies'),
        ('American Studies', 'American Studies'),
        ('Ancient Civilization (Classics)', 'Ancient Civilization (Classics)'),
        ('Ancient Greek', 'Ancient Greek'),
        ('Applied Psychology & Human Development', 'Applied Psychology & Human Development'),
        ('Arabic Studies', 'Arabic Studies'),
        ('Art History', 'Art History'),
        ('Asian Studies', 'Asian Studies'),
        ('Biology', 'Biology'),
        ('Catholic Studies', 'Catholic Studies'),
        ('Chemistry', 'Chemistry'),
        ('Chinese', 'Chinese'),
        ('Communications', 'Communications'),
        ('Computer Science', 'Computer Science'),
        ('Cyberstrategy and Design', 'Cyberstrategy and Design'),
        ('Data Science', 'Data Science'),
        ('Design Thinking and Innovation', 'Design Thinking and Innovation'),
        ('East European Studies', 'East European Studies'),
        ('Economics', 'Economics'),
        ('Educational Theater', 'EducationalTheater'),
        ('English', 'English'),
        ('Environmental Studies', 'Environmental Studies'),
        ('Faith Peace & Justice', 'Faith Peace & Justice'),
        ('Film Studies', 'Film Studies'),
        ('Finance', 'Finance'),
        ('Foundations in Education', 'Foundations in Education'),
        ('French', 'French'),
        ('Geological Sciences', 'Geological Sciences'),
        ('German', 'German'),
        ('German Studies', 'German Studies'),
        ('Global Public Health and the Common Good', 'Global Public Health and the Common Good'),
        ('Hispanic Studies', 'Hispanic Studies'),
        ('History', 'History'),
        ('Immigration Education and Humanitarian Studies', 'Immigration, Education, and Humanitarian Studies'),
        ('Inclusive Education', 'Inclusive Education'),
        ('International Studies', 'International Studies'),
        ('Irish Studies', 'Irish Studies'),
        ('Islamic Civilization & Societies', 'Islamic Civilization & Societies'),
        ('Italian', 'Italian'),
        ('Jewish Studies', 'Jewish Studies'),
        ('Journalism', 'Journalism'),
        ('Latin', 'Latin'),
        ('Latin American Studies', 'Latin American Studies'),
        ('Leadership in Higher Education and Community Settings', 'Leadership in Higher Education and Community Settings'),
        ('Linguistics', 'Linguistics'),
        ('Management and Leadership', 'Management and Leadership'),
        ('Managing for Social Impact and Public Good', 'Managing for Social Impact and Public Good'),
        ('Marketing', 'Marketing'),
        ('Mathematics', 'Mathematics'),
        ('Medical Humanities, Health, and Culture', 'Medical Humanities, Health, and Culture'),
        ('Middle School Mathematics Teaching', 'Middle School Mathematics Teaching'),
        ('Music', 'Music'),
        ('Philosophy', 'Philosophy'),
        ('Physics', 'Physics'),
        ('Religion and Public Life', 'Religion and Public Life'),
        ('Research Evaluation and Measurement', 'Research, Evaluation, and Measurement'),
        ('Restorative and Transformational Justice', 'Restorative and Transformational Justice'),
        ('Russian', 'Russian'),
        ('Secondary Education', 'Secondary Education'),
        ('Sociology', 'Sociology'),
        ('Special Education', 'Special Education'),
        ('Studio Art', 'Studio Art'),
        ('TELL certificate', 'TELL certificate'),
        ('Theatre', 'Theatre'),
        ('Theology', 'Theology'),
        ('Womens & Gender Studies', 'Womens & Gender Studies'),
    ]
    minor_1 = models.CharField(max_length=255, choices=MINORS, blank=True, null=True)
    minor_2 = models.CharField(max_length=255, choices=MINORS, blank=True, null=True)
    eagle_id = models.CharField(max_length=50, unique=True)
    GRADUATION_SEMESTER = [
        ('Spring 2024', 'Spring 2024'),
        ('Fall 2024', 'Fall 2024'),
        ('Spring 2025', 'Spring 2025'),
        ('Fall 2025', 'Fall 2025'),
        ('Spring 2026', 'Spring 2026'),
        ('Fall 2026', 'Fall 2026'),
        ('Spring 2027', 'Spring 2027'),
        ('Fall 2027', 'Fall 2027'),    
    ]
    graduation_semester = models.CharField(max_length=11, choices=GRADUATION_SEMESTER)
   

class Course(models.Model):
    course_id = models.CharField(max_length=255,unique =True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.CharField(max_length=255, default = '01/01/2023')
    schedule = models.CharField(max_length=255, default = 'none')
    instructor = models.CharField(max_length=255, default = 'none')
    level = models.CharField(max_length=255, default = 'none')
    requisite = models.CharField(max_length=255, default = 'none')
    department = models.CharField(max_length=255, default = 'none')
    level = models.CharField(max_length=255, default = 'none')
    courseIdentifier = models.CharField(max_length=255, default="none")
    max_students_on_watch = models.IntegerField(default=0)
    min_students_on_watch = models.IntegerField(default=0)
    credits = models.CharField(max_length=10, default='3')
    time_slots = models.CharField(max_length=255, default='')
    days = models.CharField(max_length=255, default='none')

    def __str__(self):
        return self.title
    def getDepartment(self):
        return self.department
    def getSchedule(self):
        return self.schedule



class Section(models.Model):
    section_id = models.CharField(max_length=255, unique=True, default='')
    instructor = models.CharField(max_length=255, default='')
    title = models.CharField(max_length=255, default='')
    location = models.CharField(max_length=255, default='')
    currentSeats = models.DecimalField(max_digits=3, decimal_places=0, default=0)
    maxSeats = models.DecimalField(max_digits=3, decimal_places=0, default=0)
    courseid = models.CharField(max_length=255, default='')
    time = models.CharField(max_length=255, default='')


    def change_seats(self):
        response = requests.get(f'{settings.API_BASE_URL}/waitlist/waitlistregistrationgroups?courseOfferingId=' + self.courseid).json()
        for entry in response:
            for section in entry['activityOfferings']:
                if section['activityOffering']['id'] == self.section_id:
                    # self.currentSeats = section['activitySeatCount']['used']

                    # change the seats
                    self.currentSeats = random.randint(0, min(int(self.maxSeats),999))
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

class MostPopularCourse(models.Model):
    most_popular_course = models.CharField(max_length=255,default='none')
    most_popular_course_count = models.IntegerField(default=0)
    snapshot = models.ForeignKey(SystemSnapshot, on_delete=models.CASCADE)