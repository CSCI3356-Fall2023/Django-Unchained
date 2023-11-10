from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from .forms import StudentRegistrationForm, AdminRegistrationForm, ChangeStateForm,ExtraInfoForm_student,ExtraInfoForm_admin
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect,render
from .models import Person, Student, Admin, SystemState, Course
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth import login as auth_login
from django.views.decorators.http import require_http_methods
import requests
from django.conf import settings
from authlib.integrations.django_client import OAuth
from urllib.parse import urlencode
import json
from urllib.parse import quote_plus
from .models import Person, SystemState
from django.shortcuts import get_object_or_404

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
        
        if user.user_type:
            if not user.is_active or not user.is_extra_info_filled_out():
                if user.user_type == 'student':
                    request.session["email"] = email
                    return redirect('student_extra_info')
                elif user.user_type == 'admin':
                    request.session["email"] = email
                    return redirect('admin_extra_info')
            else:
                auth_login(request, user)
                request.session["email"] = email
                return redirect('profile')
        else:
            request.session["email"] = email
            return redirect('role_selection')

    except Person.DoesNotExist:
        new_user = Person.objects.create_user(
            email=email,
            name=name,
            is_active=False
        )
        auth_login(request, new_user)
        request.session["email"] = email
        return redirect('role_selection')

    return redirect('index')


def course_selection(request):
    return redirect('course_selection')
        
    
# def login_view(request):
#     if request.method == "POST":
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         user = authenticate(email=email, password=password)  

#         if user is not None:
#             if user.is_active:
#                 auth_login(request, user)
#                 user.authenticate()
#                 return redirect('profile')
#             else:
#                 messages.error(request, "Your account is inactive.")
#         else:
#             messages.error(request, "Invalid credentials.")

   
#     return render(request, 'login.html', {})

# def forgot(request):
#     template = loader.get_template('login.html')
#     context = {
#         'Title': 'Reset Password', 
#         'FieldOne': 'Email',
#         'FieldTwo': 'New Password',
#         'Button': 'Confirm'
#     }
#     return HttpResponse(template.render(context, request))

# def register(request):
#     return render(request, 'identity_selection.html')

# def student_register(request):
    # if request.method == 'POST':
    #     form = StudentRegistrationForm(request.POST)
    #     if form.is_valid():
    #             student = Student.objects.create_user(
    #             email=form.cleaned_data['email'],
    #             password=form.cleaned_data['password'],
    #             name=form.cleaned_data['name'],
    #             department=form.cleaned_data['department'],
    #             eagle_id=form.cleaned_data['eagle_id'],
    #             major_1=form.cleaned_data['major_1'],
    #             major_2=form.cleaned_data['major_2'],
    #             major_3=form.cleaned_data['major_3'],
    #             minor_1=form.cleaned_data['minor_1'],
    #             minor_2=form.cleaned_data['minor_2'],
    #             graduation_semester=form.cleaned_data['graduation_semester']
    #         )

    #             return redirect('login')  
    # else:
    #     form = StudentRegistrationForm()

    # return render(request, 'student_register.html', {'form': form})

# def admin_register(request):
    # if request.method == 'POST':
    #     form = AdminRegistrationForm(request.POST)
    #     if form.is_valid():
    #         admin_instance = Admin.objects.create_superuser( 
    #             email=form.cleaned_data['email'],
    #             password=form.cleaned_data['password'],
    #             department=form.cleaned_data['department'],
    #             name = form.cleaned_data['name'],
    #             is_staff=True,
    #         )
    #         return redirect('login')  
    # else:
    #     form = AdminRegistrationForm()

    # return render(request, 'admin_register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')



@login_required
def user_profile(request):
    user = request.user
    system_state = get_object_or_404(SystemState, pk=1)

    state = 'Open' if system_state.state else 'Closed'

    context = {
        'user': user,
        'system_state': system_state,
        'state': state,
    }
    return render(request, 'profiles/profile.html', context)

@login_required
def change_state(request):
    try:
        current_state = SystemState.objects.latest('updated_at')
    except SystemState.DoesNotExist:
        current_state = None

    if request.method == 'POST':
        form = ChangeStateForm(request.POST)

        if form.is_valid():
            new_state_str = form.cleaned_data['state']
            new_state = True if new_state_str == 'Open' else False

            if current_state:
                current_state.state = new_state
                current_state.save()
            else:
                SystemState.objects.create(state=new_state)

            return redirect('profile')
    else:
        initial_state = current_state.state if current_state else ''
        form = ChangeStateForm(initial={'state': initial_state})

    context = {'form': form, 'state': current_state.state if current_state else ''}
    print("Current State:", current_state)
    return render(request, 'change_state.html', context)

def role_selection(request):
    email = request.session.get('email')
    user = Person.objects.get(email=email)
    if request.method == 'POST':
        role = request.POST.get('role')
        if role in ['student', 'admin']:
            user.user_type = role
            user.save() 
            if role == 'student':
                request.session["email"] = email
                return redirect('student_extra_info')
            elif role == 'admin':
                request.session["email"] = email
                return redirect('admin_extra_info')
    return render(request, 'identity_selection.html')



def student_extra_info(request):
    email = request.session.get('email')
    user = Person.objects.get(email=email)
    if request.method == 'POST':
        form = ExtraInfoForm_student(request.POST)
        if form.is_valid():
            user.department = form.cleaned_data.get('department')
            user.major_1 = form.cleaned_data.get('major_1')
            user.major_2 = form.cleaned_data.get('major_2')
            user.major_3 = form.cleaned_data.get('major_3')
            user.minor_1 = form.cleaned_data.get('minor_1')
            user.minor_2 = form.cleaned_data.get('minor_2')
            user.eagle_id = form.cleaned_data.get('eagle_id')
            user.graduation_semester = form.cleaned_data.get('graduation_semester')
            user.extra_info_filled_out = True
            user.is_active = True
            user.save()
            return redirect('profile')  
             
    else:
        form = ExtraInfoForm_student()

    return render(request, 'student_extra_info.html', {'form': form})

def admin_extra_info(request):
    email = request.session.get('email')
    user = Person.objects.get(email=email)
    if request.method == 'POST':
        form = ExtraInfoForm_admin(request.POST)
        if form.is_valid():
            user.department = form.cleaned_data.get('department')
            user.extra_info_filled_out = True
            user.is_staff = True
            user.is_active = True
            user.save()
            return redirect('profile') 
    else:
        form = ExtraInfoForm_admin()

    return render(request, 'admin_extra_info.html', {'form': form})

def index(request):
    return render(
        request,
        "registration/login.html",
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

def api_endpoint(request):
    response = requests.get('http://localhost:8080/waitlist/waitlistactivityofferings?personId=90000001&termId=kuali.atp.FA2023-2024')
    data_list = []
    for entry in response.json():
        offering = entry['activityOffering']
        new_course = Course(course_id=offering['id'], title=offering['name'], description=offering['descr']['plain'])
        new_course.save()
        data_list.append(new_course)
    return render(request, 'course_selection.html', {'courses': data_list})
