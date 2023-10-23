from django import forms
from .models import Student, Admin, UserProfile

class StudentRegistrationForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)
    
    name = forms.CharField(label="Name", max_length=255)
    department = forms.CharField(label="Department", max_length=255)
    eagle_id = forms.CharField(label="Eagle ID", max_length=8, min_length=8)
    major_1 = forms.CharField(label="Major 1", max_length=255)
    graduation_semester = forms.ChoiceField(label="Graduation Semester", choices=Student.GRADUATION_SEMESTER)
    
    major_2 = forms.CharField(label="Major 2", max_length=255, required=False)
    major_3 = forms.CharField(label="Major 3", max_length=255, required=False)
    minor_1 = forms.CharField(label="Minor 1", max_length=255, required=False)
    minor_2 = forms.CharField(label="Minor 2", max_length=255, required=False)
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

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

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "The two password fields must match.")

        if Admin.objects.filter(email=cleaned_data.get("email")).exists():
            self.add_error('email', "This email is already registered.")
        

        return cleaned_data
    

  