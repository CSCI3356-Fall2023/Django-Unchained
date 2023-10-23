from django.http import HttpResponse
from django.template import loader
from .forms import StudentRegistrationForm, AdminRegistrationForm
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect,render
from .models import UserProfile, Student, Admin, SystemState
from django.contrib.auth.decorators import login_required

# Create your views here.

def login(request):
    template = loader.get_template('login.html')
    context = {
        'Title': 'Sign into your Account', 
        'FieldOne': 'Email',
        'FieldTwo': 'Password',
        'Button': 'Login'
    }
    return HttpResponse(template.render(context, request))

def forgot(request):
    template = loader.get_template('login.html')
    context = {
        'Title': 'Reset Password', 
        'FieldOne': 'Email',
        'FieldTwo': 'New Password',
        'Button': 'Confirm'
    }
    return HttpResponse(template.render(context, request))

def register(request):
    return render(request, 'identity_selection.html')

def student_register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = User(
                username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                password=make_password(form.cleaned_data['password'])
            )

            user.save()

            user_profile = UserProfile(user=user, user_type='student')
            user_profile.save()

            student = Student(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                department=form.cleaned_data['department'],
                eagle_id=form.cleaned_data['eagle_id'],
                major_1=form.cleaned_data['major_1'],
                major_2=form.cleaned_data['major_2'],
                major_3=form.cleaned_data['major_3'],
                minor_1=form.cleaned_data['minor_1'],
                minor_2=form.cleaned_data['minor_2'],
                graduation_semester=form.cleaned_data['graduation_semester']
                
            )
            student.save()
            return redirect('login')  
    else:
        form = StudentRegistrationForm()

    return render(request, 'student_register.html', {'form': form})

def admin_register(request):
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            user = User(
                username=form.cleaned_data['email'], 
                email=form.cleaned_data['email'],
                password=make_password(form.cleaned_data['password'])
            )
            user.save()

            user_profile = UserProfile(user=user, user_type='admin')
            user_profile.save()

            admin_instance = Admin(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                department=form.cleaned_data['department'],
            )
            admin_instance.save()
            return redirect('login')  
    else:
        form = AdminRegistrationForm()

    return render(request, 'admin_register.html', {'form': form})

@login_required
def user_profile(request):
    user = request.user
    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        user_profile = None
    try:
        system_state = SystemState.objects.latest('updated_at')
    except SystemState.DoesNotExist:
        system_state = None
    context = {
        'user': user,
        'user_profile': user_profile,
        'system_state': system_state,
    }
    return render(request, 'profiles/profile.html', context)