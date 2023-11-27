from django import forms
from .models import Student, Admin

class StudentRegistrationForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)
    
    name = forms.CharField(label="Name", max_length=255)
    department = forms.CharField(label="Department", max_length=255)
    eagle_id = forms.CharField(label="Eagle ID", max_length=8, min_length=8)
    graduation_semester = forms.ChoiceField(label="Graduation Semester", choices=Student.GRADUATION_SEMESTER)
    
    major_1 = forms.CharField(label="Major 1", max_length=255)
    major_2 = forms.CharField(label="Major 2", max_length=255, required=False)
    major_3 = forms.CharField(label="Major 3", max_length=255, required=False)
    minor_1 = forms.CharField(label="Minor 1", max_length=255, required=False)
    minor_2 = forms.CharField(label="Minor 2", max_length=255, required=False)
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        email = self.cleaned_data.get('email')

        if email[-6:] != 'bc.edu':
            self.add_error('email', 'Only Boston College emails are allowed to sign up.')
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "The two password fields must match.")

        if Student.objects.filter(eagle_id=cleaned_data.get("eagle_id")).exists():
            self.add_error('eagle_id', "This Eagle ID is already registered.")
        if Student.objects.filter(email=cleaned_data.get("email")).exists():
            self.add_error('email', "This email is already registered.")
        

        return cleaned_data

class AdminRegistrationForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)
    name = forms.CharField(label="Name", max_length=255)
    department = forms.CharField(label="Department", max_length=255)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        email = cleaned_data.get('email')

        if email[-6:] != 'bc.edu':
            self.add_error('email', 'Only Boston College emails are allowed to sign up.')        

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "The two password fields must match.")

        if Admin.objects.filter(email=cleaned_data.get("email")).exists():
            self.add_error('email', "This email is already registered.")
        

        return cleaned_data

class ChangeStateForm(forms.Form):
    state = forms.CharField(label = 'open or closed?')

    def clean_state(self):
        data = self.cleaned_data['state'].lower()

        if data not in ['open', 'closed']:
            raise forms.ValidationError("Invalid state. Please enter 'open' or 'closed' (case-insensitive).")

        return data


class ExtraInfoForm_student(forms.Form):
    department = forms.CharField(label="Department", max_length=255)
    eagle_id = forms.CharField(label="Eagle ID", max_length=8, min_length=8)
    graduation_semester = forms.ChoiceField(label="Graduation Semester", choices=Student.GRADUATION_SEMESTER)
    
    major_1 = forms.CharField(label="Major 1", max_length=255)
    major_2 = forms.CharField(label="Major 2", max_length=255, required=False)
    major_3 = forms.CharField(label="Major 3", max_length=255, required=False)
    minor_1 = forms.CharField(label="Minor 1", max_length=255, required=False)
    minor_2 = forms.CharField(label="Minor 2", max_length=255, required=False)

    def clean(self):
        
        cleaned_data = super().clean()
        if Student.objects.filter(eagle_id=cleaned_data.get("eagle_id")).exists():
            self.add_error('eagle_id', "This Eagle ID is already registered.")
        if Student.objects.filter(email=cleaned_data.get("email")).exists():
            self.add_error('email', "This email is already registered.")
        
        
        return cleaned_data


class ExtraInfoForm_admin(forms.Form):
    
    department = forms.CharField(label="Department", max_length=255)

    def clean(self):
        cleaned_data = super().clean()
        if Admin.objects.filter(email=cleaned_data.get("email")).exists():
            self.add_error('email', "This email is already registered.")
        return cleaned_data
    


# class CourseFilterForm(forms.Form):
#     TIME_SLOTS = (
#         ('early_morning', 'Early Morning (00:00-09:59)'),
#         ('late_morning', 'Late Morning (10:00-11:59)'),
#         ('early_afternoon', 'Early Afternoon (12:00-15:59)'),
#         ('late_afternoon', 'Late Afternoon (16:00-17:59)'),
#         ('evening', 'Evening (18:00-23:59)'),
#     )
#     SCHOOL = (
#         ('carroll', 'Carroll School of Management'),
#         ('lynch', 'Lynch School of Education and Human Development'),
#         ('morrissey', 'Morrissey College of Arts and Sciences'),
#         ('woods', 'Woods College of Advancing Studies'),
#         ('law', 'Boston College Law School'),
#         ('nursing', 'Connell School of Nursing'),
#         ('social_work', 'School of Social Work'),
#         ('theology', 'School of Theology and Ministry'),
#         ('schiller', 'Schiller Institute for Integrated Science and Society'),

#     )
#     COURSE_LEVEL = (
#         ('undergraduate', 'Undergraduate'),
#         ('graduate', 'Graduate'),
#         ('both undergraduate and graduate', 'Both Undergraduate and Graduate'),
#     )
#     CREDITS = (
#         ('1', '1'),
#         ('2', '2'),
#         ('3', '3'),
#         ('4', '4'),
#     )
#     DELIVERY_METHOD = (
#         ('clinical', 'Clinical'),
#         ('hybrid', 'Hybrid'),
#         ('in-person', 'In-Person'),
#         ('online', 'Online'),
#         ('remote', 'Remote'),
#         ('synchronous', 'Synchronous'),
#         ('asynchronous', 'Asynchronous'),
#         ('thesis', 'Thesis'),
#     )
#     REGISTRATION_PERMISSIONS = (
#         ('none','None'),
#         ('department', 'Department'),
#         ('instructor', 'Instructor'),
#     )
        
       



    

#     time_slot = forms.ChoiceField(choices=TIME_SLOTS, required=False)
#     title = forms.CharField(max_length=255, required=False)
#     days = forms.CharField(max_length=255, required=False)
#     session = forms.CharField(max_length=255, required=False)
#     subject_area = forms.CharField(max_length=255, required=False)
#     school = forms.CharField(choices= SCHOOL,required=False)
#     credits = forms.CharField(max_length=255, required=False)
#     fulfill_requirements = forms.CharField(max_length=255, required=False)
#     instructor = forms.CharField(max_length=255, required=False)
#     delivery_method = forms.CharField(max_length=255, required=False)
#     course_level = forms.CharField(max_length=255, required=False)
#     registration_permissions = forms.CharField(max_length=255, required=False)
#     open_seats = forms.CharField(max_length=255, required=False)

#     def clean(self):
#         cleaned_data = super().clean()
#         if cleaned_data.get("time_slot") == '':
#             cleaned_data.pop("time_slot")
#         if cleaned_data.get("title") == '':
#             cleaned_data.pop("title")
#         if cleaned_data.get("days") == '':
#             cleaned_data.pop("days")
#         if cleaned_data.get("session") == '':
#             cleaned_data.pop("session")
#         if cleaned_data.get("subject_area") == '':
#             cleaned_data.pop("subject_area")
#         if cleaned_data.get("school") == '':
#             cleaned_data.pop("school")
#         if cleaned_data.get("credits") == '':
#             cleaned_data.pop("credits")
#         if cleaned_data.get("fulfill_requirements") == '':
#             cleaned_data.pop("fulfill_requirements")
#         if cleaned_data.get("instructor") == '':
#             cleaned_data.pop("instructor")
#         if cleaned_data.get("delivery_method") == '':
#             cleaned_data.pop("delivery_method")
#         if cleaned_data.get("course_level") == '':
#             cleaned_data.pop("course_level")
#         if cleaned_data.get("registration_permissions") == '':
#             cleaned_data.pop("registration_permissions")
#         if cleaned_data.get("open_seats") == '':
#             cleaned_data.pop("open_seats")
        
#         return cleaned_data





    


  