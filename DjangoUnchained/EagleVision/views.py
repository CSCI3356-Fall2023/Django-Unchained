from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .forms import StudentRegistrationForm, AdminRegistrationForm, ChangeStateForm
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect,render
from .models import UserProfile, Student, Admin, SystemState
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.urls import reverse

# Create your views here.

def login(request):
    template = loader.get_template('login.html')
    context = {
        'Title': 'Sign into your Account', 
        'FieldOne': 'Email',
        'FieldTwo': 'Password',
        'Button': 'Login'
    }
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, email=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile')
        else:
            messages.error(request, ("There was an error when logging in. Plase try again..."))
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

            user_profile = UserProfile(user=user, user_type='student',name=form.cleaned_data['name'])
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
            return redirect('logout')
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

            user_profile = UserProfile(user=user, user_type='admin',name=form.cleaned_data['name'])
            user_profile.name = form.cleaned_data['name']
            user_profile.save()

            admin_instance = Admin(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                department=form.cleaned_data['department'],
            )
            admin_instance.save()
            
            return redirect('logout')
    else:
        form = AdminRegistrationForm()

    return render(request, 'admin_register.html', {'form': form})

def logout(request):
    template = loader.get_template('login.html')
    context = {
        'Title': 'Sign into your Account', 
        'FieldOne': 'Email',
        'FieldTwo': 'Password',
        'Button': 'Login'
    }
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, email=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile')
        else:
            messages.error(request, ("There was an error when logging in. Plase try again..."))
    ## correct_login(request)
    return HttpResponse(template.render(context, request))

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
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        user_profile = None
    try:
        system_state = SystemState.objects.latest('updated_at')
    except SystemState.DoesNotExist:
        system_state = None
    context = {
        'name': user_profile.name,
        'user': user,
        'user_profile': user_profile,
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
                return redirect('profile')
    return render(request, 'change_state.html', {'form' : form, 'state': state})