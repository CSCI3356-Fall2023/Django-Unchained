from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .forms import StudentRegistrationForm, AdminRegistrationForm, ChangeStateForm
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect,render
from .models import UserProfile, Student, Admin, SystemState
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import login as auth_login

# Create your views here.

def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(email=email, password=password)  

        if user is not None:
            if user.is_active:
                auth_login(request, user)  
                return redirect('profile')
            else:
                messages.error(request, "Your account is inactive.")
        else:
            messages.error(request, "Invalid credentials.")

   
    return render(request, 'login.html', {})

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
                student = Student.objects.create_user(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                name=form.cleaned_data['name'],
                department=form.cleaned_data['department'],
                eagle_id=form.cleaned_data['eagle_id'],
                major_1=form.cleaned_data['major_1'],
                major_2=form.cleaned_data['major_2'],
                major_3=form.cleaned_data['major_3'],
                minor_1=form.cleaned_data['minor_1'],
                minor_2=form.cleaned_data['minor_2'],
                graduation_semester=form.cleaned_data['graduation_semester']
            )

                return redirect('login')  


           
    else:
        form = StudentRegistrationForm()

    return render(request, 'student_register.html', {'form': form})

def admin_register(request):
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            admin_instance = Admin.objects.create_superuser( 
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                department=form.cleaned_data['department'],
                name = form.cleaned_data['name'],
                is_staff=True,
            )
            return redirect('login')  
    else:
        form = AdminRegistrationForm()

    return render(request, 'admin_register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

##when do I call this
def correct_login(request):
    if request.user.is_authenticated:
        redir_url = reverse('profile')
    else:
        redir_url = reverse('login')
    return HttpResponseRedirect(redir_url)


@login_required
def user_profile(request):
    user = request.user
    try:
        system_state = SystemState.objects.latest('updated_at')
    except SystemState.DoesNotExist:
        system_state = None

    context = {
        'user': user,
        'system_state': system_state,
    }
    return render(request, 'profiles/profile.html', context)


@login_required
def change_state(request):
    try:
        Admin.objects.get(email=request.user)
    except:
        return redirect('profile')
    state_dict = {'OPEN': True, 'CLOSED': False}
    form = ChangeStateForm()
    user = request.user
    state_object = SystemState.objects.get(id=1)
    state = 'CLOSED'
    if state_object.state:
        state = 'OPEN'
    if request.method == 'POST':
        form = ChangeStateForm(request.POST)
        if form.is_valid():
            new_state = form.cleaned_data['state'].upper()
            if new_state in state_dict.keys():
                state_object.state = state_dict[new_state]
                state_object.save()
                return redirect('change_state')
    return render(request, 'change_state.html', {'form' : form, 'state': state})