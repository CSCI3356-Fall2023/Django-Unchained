from django import forms
from .models import Student, Admin, Person

class StudentRegistrationForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)
    
    name = forms.CharField(label="Name", max_length=255)
    department = forms.ChoiceField(label="Department", choices=Person.DEPARTMENT)
    eagle_id = forms.CharField(label="Eagle ID", max_length=8, min_length=8)
    graduation_semester = forms.ChoiceField(label="Graduation Semester", choices=Student.GRADUATION_SEMESTER)
    
    major_1 = forms.ChoiceField(label="Major 1", choices=Student.MAJORS)
    major_2 = forms.ChoiceField(label="Major 2", required=False, choices=Student.MAJORS)
    major_3 = forms.ChoiceField(label="Major 3", required=False, choices=Student.MAJORS)
    minor_1 = forms.ChoiceField(label="Minor 1", required=False, choices=Student.MINORS)
    minor_2 = forms.ChoiceField(label="Minor 2", required=False, choices=Student.MINORS)
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
    department = forms.ChoiceField(label="Department", choices=Person.DEPARTMENT)

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
    department = forms.ChoiceField(label="Department", choices=Person.DEPARTMENT)
    eagle_id = forms.CharField(label="Eagle ID", max_length=8, min_length=8)
    graduation_semester = forms.ChoiceField(label="Graduation Semester", choices=Student.GRADUATION_SEMESTER)
    
    major_1 = forms.ChoiceField(label="Major 1", choices=Student.MAJORS)
    major_2 = forms.ChoiceField(label="Major 2", choices=Student.MAJORS, required=False)
    major_3 = forms.ChoiceField(label="Major 3", choices=Student.MAJORS, required=False)
    minor_1 = forms.ChoiceField(label="Minor 1", choices=Student.MINORS, required=False)
    minor_2 = forms.ChoiceField(label="Minor 2", choices=Student.MINORS, required=False)

    def check_for_duplicates(self, cleaned_data):
        field_names = ['major_1', 'major_2', 'major_3', 'minor_1', 'minor_2']
        field_values = [cleaned_data.get(field) for field in field_names]

        # Check for duplicates between majors and minors
        for i, majorminor1 in enumerate(field_names):
            for majorminor2 in field_names[i + 1:]:
                majorminor1 = cleaned_data.get(majorminor1)
                majorminor2 = cleaned_data.get(majorminor2)

                if majorminor1 and majorminor2 and majorminor1 == majorminor2:
                    raise forms.ValidationError(f"{majorminor1.capitalize()} should be different from {majorminor2.capitalize()}.")

    def __init__(self, *args, **kwargs):
        self.student_instance = kwargs.pop('student_instance', None)
        super(ExtraInfoForm_student, self).__init__(*args, **kwargs)


    def clean(self):
        cleaned_data = super().clean()
        self.check_for_duplicates(cleaned_data)
        return cleaned_data

class ExtraInfoForm_admin(forms.Form):
    
    department = forms.ChoiceField(label="Department", choices=Person.DEPARTMENT)

    def clean(self):
        cleaned_data = super().clean()
        if Admin.objects.filter(email=cleaned_data.get("email")).exists():
            self.add_error('email', "This email is already registered.")
        return cleaned_data

class CourseFilterForm(forms.Form):
    TIME_SLOTS = (
        ('early_morning', 'Early Morning (00:00-09:59)'),
        ('late_morning', 'Late Morning (10:00-11:59)'),
        ('early_afternoon', 'Early Afternoon (12:00-15:59)'),
        ('late_afternoon', 'Late Afternoon (16:00-17:59)'),
        ('evening', 'Evening (18:00-23:59)'),
    )
  
   
    DAYS = (
        ('M', 'Monday'), 
        ('T', 'Tuesday'), 
        ('W', 'Wednesday'), 
        ('TH', 'Thursday'), 
        ('F', 'Friday'), 
        ('MW', 'Monday and Wednesday'), 
        ('MWF', 'Monday, Wednesday, and Friday'), 
        ('TUTH', 'Tuesday and Thursday')
    )   
    MAJORS = ( 
        ("AADS", "AADS"),
        ("ACCT", "ACCT"),
        ("ADAC", "ADAC"),
        ("ADAN", "ADAN"),
        ("ADBI", "ADBI"),
        ("ADBM", "ADBM"),
        ("ADCJ", "ADCJ"),
        ("ADCO", "ADCO"),
        ("ADCY", "ADCY"),
        ("ADEC", "ADEC"),
        ("ADEN", "ADEN"),
        ("ADET", "ADET"),
        ("ADEX", "ADEX"),
        ("ADFA", "ADFA"),
        ("ADGR", "ADGR"),
        ("ADHS", "ADHS"),
        ("ADIT", "ADIT"),
        ("ADMK", "ADMK"),
        ("ADMT", "ADMT"),
        ("ADPL", "ADPL"),
        ("ADPO", "ADPO"),
        ("ADPS", "ADPS"),
        ("ADSA", "ADSA"),
        ("ADSB", "ADSB"),
        ("ADSO", "ADSO"),
        ("ADTH", "ADTH"),
        ("APSY", "APSY"),
        ("ARTH", "ARTH"),
        ("ARTS", "ARTS"),
        ("BCOM", "BCOM"),
        ("BIOL", "BIOL"),
        ("BSLW", "BSLW"),
        ("BZAN", "BZAN"),
        ("CHEM", "CHEM"),
        ("CLAS", "CLAS"),
        ("COMM", "COMM"),
        ("CSCI", "CSCI"),
        ("EALC", "EALC"),
        ("ECON", "ECON"),
        ("EDUC", "EDUC"),
        ("EESC", "EESC"),
        ("ELHE", "ELHE"),
        ("ENGL", "ENGL"),
        ("ENGR", "ENGR"),
        ("ENVS", "ENVS"),
        ("ERAL", "ERAL"),
        ("FILM", "FILM"),
        ("FORM", "FORM"),
        ("FORS", "FORS"),
        ("FREN", "FREN"),
        ("GERM", "GERM"),
        ("GSOM", "GSOM"),
        ("HIST", "HIST"),
        ("HLTH", "HLTH"),
        ("ICSP", "ICSP"),
        ("INTL", "INTL"),
        ("ISYS", "ISYS"),
        ("ITAL", "ITAL"),
        ("JESU", "JESU"),
        ("JOUR", "JOUR"),
        ("LAWS", "LAWS"),
        ("LING", "LING"),
        ("LREN", "LREN"),
        ("MATH", "MATH"),
        ("MESA", "MESA"),
        ("MFIN", "MFIN"),
        ("MGMT", "MGMT"),
        ("MKTG", "MKTG"),
        ("MUSA", "MUSA"),
        ("MUSP", "MUSP"),
        ("NELC", "NELC"),
        ("NURS", "NURS"),
        ("PHCG", "PHCG"),
        ("PHIL", "PHIL"),
        ("PHYS", "PHYS"),
        ("POLI", "POLI"),
        ("PRTO", "PRTO"),
        ("PSYC", "PSYC"),
        ("RLRL", "RLRL"),
        ("ROTC", "ROTC"),
        ("SCHI", "SCHI"),
        ("SCWK", "SCWK"),
        ("SLAV", "SLAV"),
        ("SOCY", "SOCY"),
        ("SPAN", "SPAN"),
        ("THEO", "THEO"),
        ("THTR", "THTR"),
        ("TMCE", "TMCE"),
        ("TMHC", "TMHC"),
        ("TMNT", "TMNT"),
        ("TMOT", "TMOT"),
        ("TMPS", "TMPS"),
        ("TMRE", "TMRE"),
        ("TMST", "TMST"),
        ("TMTM", "TMTM"),
        ("UGMG", "UGMG"),
        ("UNAS", "UNAS"),
        ("UNCP", "UNCP"),
        ("UNCS", "UNCS"),
        ("XRBC", "XRBC"))



    

    time_slot = forms.ChoiceField(choices=TIME_SLOTS, required=False,
                                    widget=forms.widgets.RadioSelect, label="Time")
   
    days = forms.MultipleChoiceField(choices=DAYS, required=False, label="Days")
    
    subject_area = forms.ChoiceField(choices=MAJORS, required=False, label="Major")
   
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

        
    



    


  