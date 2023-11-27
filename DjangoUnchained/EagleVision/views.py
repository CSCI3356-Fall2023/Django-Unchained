from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from .forms import StudentRegistrationForm, AdminRegistrationForm, ChangeStateForm,ExtraInfoForm_student,ExtraInfoForm_admin
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect,render
from .models import Person, Student, Admin, SystemState, Course, Watchlist, Section
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
from .models import Person, SystemState, Course
from django.shortcuts import get_object_or_404
from django.utils.html import escape
from bs4 import BeautifulSoup
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt
from .constants import TIME_SLOTS
from .forms import CourseFilterForm
from django.core.paginator import Paginator

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

# @login_required
# def course_selection(request):
#     user_watchlist_course_ids = Watchlist.objects.filter(user=request.user).values_list('course_id', flat=True)
#     all_courses = Course.objects.all()
#     print("User's Watchlist Course IDs:", user_watchlist_course_ids)
#     context = {
#         'courses': all_courses,
#         'user_watchlist_ids': user_watchlist_course_ids,
#     }
#     return render(request, 'course_selection.html', context)


@login_required
def course_selection(request):
    
    user_watchlist_course_ids = Watchlist.objects.filter(user=request.user).values_list('course_id', flat=True)

    
    response = requests.get('http://localhost:8080/waitlist/waitlistcourseofferings?termId=kuali.atp.FA2023-2024&code=CSCI')
    data_list = []
    if response.status_code == 200:
        for entry in response.json():
            offering = entry['courseOffering']
            term = entry['term']
            description_html = offering['descr']['plain']
            date_text = term['descr']['plain']
            soup = BeautifulSoup(description_html, 'html.parser')
            description_text = soup.get_text(separator=' ')

            
            new_response = requests.get('http://localhost:8080/waitlist/waitlistactivityofferings?courseOfferingId=' + offering['id'])
            course_info = {}

            for new_entry in new_response.json():
                if isinstance(new_entry, str):
                    continue

                activity = new_entry.get('activityOffering')
                if activity:
                    course_id = offering['id']
                    instructors = activity.get('instructors', [])
                    schedule_names = new_entry.get('scheduleNames', [])
                    if course_id in course_info:
                        course_info[course_id]['schedules'].extend(schedule_names)
                        course_info[course_id]['instructors'].extend([instructor.get('personName', '') for instructor in instructors])
                    else:
                        course_info[course_id] = {
                            'schedules': schedule_names,
                            'instructors': [instructor.get('personName', '') for instructor in instructors]
                        }

           
            for course_id, info in course_info.items():
                upper_sche = [sche.upper() for sche in sorted(info['schedules'])]
                upper_instr = [instr.upper() for instr in sorted(info['instructors'])]
                unique_sche = list(set(upper_sche))
                unique_instr = list(set(upper_instr))

                schedules_str = ', '.join(sorted(unique_sche))
                instructors_str = ', '.join(sorted(unique_instr))
                
               
                new_course = Course(
                    course_id=course_id,
                    title=offering['name'],
                    description=description_text,
                    date=date_text,
                    schedule=schedules_str,
                    instructor=instructors_str
                )
                new_course.save()
                data_list.append(new_course)
    for block in Course.objects.all():
        if Course.objects.filter(course_id=block.course_id).count() > 1:
            block.delete()

    all_courses = Course.objects.all()
    context = {
        'courses': all_courses,
        'user_watchlist_ids': user_watchlist_course_ids,
    }

    return render(request, 'course_selection.html', context)



def logout_view(request):
    logout(request)
    return redirect('login')



@login_required
def user_profile(request):
    user = request.user
    try:
        system_state = SystemState.objects.get(id=1)  
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
        current_state = SystemState.objects.latest('updated_at')
    except SystemState.DoesNotExist:
        current_state = None

    if request.method == 'POST':
        form = ChangeStateForm(request.POST)

        if form.is_valid():
            new_state_str = form.cleaned_data['state']
            new_state = True if new_state_str.lower() == 'open' else False


            if current_state:
                current_state.state = new_state
                current_state.save()
            else:
                SystemState.objects.create(state=new_state)

            return redirect('profile')
    else:
        initial_state = current_state.state if current_state else ''
        form = ChangeStateForm(initial={'state': initial_state})

    context = {'form': form, 'current_state': current_state.state if current_state else ''}
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
    response = requests.get('http://localhost:8080/waitlist/waitlistcourseofferings?termId=kuali.atp.FA2023-2024&code=CSCI')
    data_list = []
    if response.status_code == 200:
        for entry in response.json():
            offering = entry['courseOffering']
            term = entry['term']
            requisite_ids = entry.get('courseOffering', {}).get('requisiteIds', [])
            req = []
            for id in requisite_ids:
                if id == offering['id']:
                    req.append(offering['name'])
            #'requisiteIds' is not the same as 'id' of requisites. Still exploring...#
            description_html = offering['descr']['plain']
            date_text = term['descr']['plain']
            soup = BeautifulSoup(description_html, 'html.parser')
            description_text = soup.get_text(separator=' ')
            new_response = requests.get('http://localhost:8080/waitlist/waitlistactivityofferings?courseOfferingId=' + offering['id'])
            course_info = {}

            for new_entry in new_response.json():
                if isinstance(new_entry, str):
                    continue

                activity = new_entry.get('activityOffering')

                if activity:
                    course_id = offering['id']
                    instructors = activity.get('instructors', [])
                    schedule_names = new_entry.get('scheduleNames', [])
                    if course_id in course_info:
                        course_info[course_id]['schedules'].extend(schedule_names)
                        course_info[course_id]['instructors'].extend([instructor.get('personName', '') for instructor in instructors])
                    else:
                        course_info[course_id] = {
                            'schedules': schedule_names,
                            'instructors': [instructor.get('personName', '') for instructor in instructors]
                        }


            for course_id, info in course_info.items():
                upper_sche = [sche.upper() for sche in sorted(info['schedules'])]
                upper_instr = [instr.upper() for instr in sorted(info['instructors'])]
                unique_sche = list(set(upper_sche))
                unique_instr = list(set(upper_instr))

                schedules_str = ', '.join(sorted(unique_sche))
                instructors_str = ', '.join(sorted(unique_instr))
                
                new_course = Course(
                    course_id=course_id,
                    title=offering['name'],
                    description=description_text,
                    date=date_text,
                    schedule=schedules_str,
                    instructor=instructors_str
                )
                new_course.save()
                data_list.append(new_course)
    for block in Course.objects.all():
        if Course.objects.filter(course_id=block.course_id).count() > 1:
            block.delete()
    return render(request, 'course_selection.html', {'courses': data_list})


def search_results(request):
    if request.method == 'GET':
        search_query = request.GET.get('search_query', '')
        term = request.GET.get('term', '')
        major = request.GET.get('major', '')
        days = request.GET.getlist('date')  
        time_slots = request.GET.getlist('time_slot')

        courses = Course.objects.filter(title__icontains=search_query)
        if term:
            courses = courses.filter(term__icontains=term)
        if major:
            courses = courses.filter(major__icontains=major)
        if days:
            courses = courses.filter(days__in=days)  
        if time_slots:
            courses = courses.filter(time_slot__in=time_slots)  
        distinct_courses = {}
        for course in courses:
            distinct_courses[course.title] = course
        filtered_courses = list(distinct_courses.values())

        return render(request, 'search_results.html', {'filtered_courses': filtered_courses})

    return HttpResponseRedirect(reverse('course_selection'))

def filter(request):
    context = {}
    context['form'] = CourseFilterForm()
    return render(request, "filters.html", context)
    # return render(request, "filters.html", {'TIME_SLOTS': TIME_SLOTS})


## we need to delete this later
def filterRequest(request):
    return 0;

@login_required
def watchlist(request):
    user_watchlist_courses = Course.objects.filter(watchlist__user=request.user)

    context = {
        'user': request.user,
        'watchlist_courses': user_watchlist_courses,
    }
    return render(request, "watchlist.html", context)


@login_required
@require_http_methods(["POST"])
def add_to_watchlist(request):
    course_id = request.POST.get('course_id')
    course = get_object_or_404(Course, pk=course_id)

   
    watchlist_entry, created = Watchlist.objects.get_or_create(user=request.user, course=course)

    if created:
        messages.success(request, "Course added to watchlist successfully.")
    else:
        messages.info(request, "This course is already in your watchlist.")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
@require_http_methods(["POST"])
def remove_from_watchlist(request):
    course_id = request.POST.get('course_id')
    course = get_object_or_404(Course, pk=course_id)
    Watchlist.objects.filter(user=request.user, course=course).delete()
    
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def section_api_endpoint(request, title):
    getID = requests.get("http://localhost:8080/waitlist/waitlistcourseofferings?termId=kuali.atp.FA2023-2024&code=" + title[0:9]).json()
    courseID = getID[0]['courseOffering']['id']
    print(courseID)
    registrationGroupResponse = requests.get("http://localhost:8080/waitlist/waitlistregistrationgroups?courseOfferingId=" + courseID).json()
    for entry in registrationGroupResponse:
        for section in entry['activityOfferings']:
            instructors = []
            for instructor in section['activityOffering']['instructors']:
                instructors.append(instructor['personName'])
            print(instructors)
            current = section['activitySeatCount']['used']
            print(current)
            max = section['activitySeatCount']['total']
            name = section['activityOffering']['formatOfferingName']
            locale = section['scheduleNames'][0]
            course = Section(instructor=';'.join(sorted(instructors)),
                                title=name, 
                                currentSeats=current, 
                                maxSeats=max, 
                                location=locale, 
                                courseid=courseID)
            for courses in Section.objects.all():
                if courses.location == course.location and courses.courseid == course.courseid:
                    courses.delete()
            course.save()
    
    # Deletes the duplicate objects after they're added
    
    queryset = Section.objects.filter(courseid=courseID)
    context = {'data': queryset}
    return render(request, 'section_selection.html', context)