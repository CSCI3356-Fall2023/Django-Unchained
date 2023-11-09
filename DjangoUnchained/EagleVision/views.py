from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .forms import StudentRegistrationForm, AdminRegistrationForm, ChangeStateForm,ExtraInfoForm_student,ExtraInfoForm_admin
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect,render
from .models import Person, Student, Admin, SystemState
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.conf import settings
from authlib.integrations.django_client import OAuth
from urllib.parse import urlencode
import json
from urllib.parse import quote_plus


oauth = OAuth()
oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)



# Create your views here.
def home_view(request):
    return redirect('login')


def login(request):
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callback"))
    )






def callback(request):
    token = oauth.auth0.authorize_access_token(request)
    userinfo = token.get('userinfo')
    email = userinfo.get("email")
    name = userinfo.get("name")

    if not email.endswith('@bc.edu'):
        messages.error(request, "Only Boston College emails are allowed to sign up.")
        return redirect('login')

    try:
        user = Person.objects.get(email=email)
        # Check if user type is set and whether additional info is required
        if user.user_type:
            if not user.is_active or not user.is_extra_info_filled_out():
                if user.user_type == 'student':
                    return redirect('student_extra_info')
                elif user.user_type == 'admin':
                    return redirect('admin_extra_info')
            else:
                auth_login(request, user)
                return redirect('profile')
        else:
         
            return redirect('role_selection')

    except Person.DoesNotExist:
        new_user = Person.objects.create_user(
            email=email,
            name=name,
            is_active=False
        )
        new_user.backend = 'django.contrib.auth.backends.ModelBackend'
        auth_login(request, new_user)
        return redirect('role_selection')

    return redirect('index')


def course_selection(request):
    return redirect('courseselect')
        

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
    try:
        state_object = SystemState.objects.get(id=1)
    except:
        state_object = SystemState()
        state_object.state = True
        state_object.save()
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





def role_selection(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        if role in ['student', 'admin']:
            request.user.user_type = role
            request.user.save() 
            if role == 'student':
                return redirect('student_extra_info')
            elif role == 'admin':
                return redirect('admin_extra_info')
    return render(request, 'identity_selection.html')



def student_extra_info(request):
    if request.method == 'POST':
        form = ExtraInfoForm_student(request.POST)
        if form.is_valid():
            request.user.student.update_extra_info(**form.cleaned_data)
            return redirect('profile')  
    else:
        form = ExtraInfoForm_student()

    return render(request, 'student_extra_info.html', {'form': form})



def admin_extra_info(request):
    if request.method == 'POST':
        form = ExtraInfoForm_admin(request.POST)
        if form.is_valid():
            request.user.admin.update_extra_info(**form.cleaned_data)
            return redirect('profile') 
    else:
        form = ExtraInfoForm_admin()

    return render(request, 'admin_extra_info.html', {'form': form})



def index(request):
    return render(
        request,
        "login.html",
        context={
            "session": request.session.get("user"),
            "pretty": json.dumps(request.session.get("user"), indent=4),
        },
    )

def logout(request):
    request.session.clear()

    return redirect(
        f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
        + urlencode(
            {
                "returnTo": request.build_absolute_uri(reverse("index")),
                "client_id": settings.AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        ),
    )