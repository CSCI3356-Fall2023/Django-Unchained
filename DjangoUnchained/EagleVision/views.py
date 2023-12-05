from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from .forms import StudentRegistrationForm, AdminRegistrationForm, ChangeStateForm,ExtraInfoForm_student,ExtraInfoForm_admin, CourseFilterForm
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect, render, get_object_or_404, get_object_or_404
from .models import Person, Student, Admin, SystemState, Course, Watchlist, Section
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.views.decorators.http import require_http_methods
import requests
from django.conf import settings
from authlib.integrations.django_client import OAuth
from urllib.parse import urlencode
import json
from .models import SystemSnapshot
from urllib.parse import quote_plus
from django.utils.html import escape
from bs4 import BeautifulSoup
from django.db.models import Count, Max, Min
from django.views.decorators.csrf import csrf_exempt
from .constants import TIME_SLOTS
from django.core.paginator import Paginator
from django.contrib.auth.decorators import user_passes_test
from django.core.mail import send_mail
from django.template.loader import render_to_string
import uuid
from django.utils.timezone import now
from pprint import pprint

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




@login_required
def course_selection(request):
    user_watchlist_course_ids = Watchlist.objects.filter(user=request.user).values_list('course_id', flat=True)    
    response = requests.get('http://localhost:8080/waitlist/waitlistcourseofferings?termId=kuali.atp.FA2023-2024&code=CSCI')
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

                
                Course.objects.get_or_create(
                    course_id=course_id,
                    defaults={
                        'title': offering['name'],
                        'description': description_text,
                        'date': date_text,
                        'schedule': schedules_str,
                        'instructor': instructors_str
                    }
                )

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
    if request.method == 'GET':
        form = CourseFilterForm(request.GET)
        if form.is_valid():
            time = form.cleaned_data['time_slot']
            days = form.cleaned_data['days']
            major = form.cleaned_data['subject_area']
            response = requests.get('http://localhost:8080/waitlist/waitlistcourseofferings?termId=kuali.atp.FA2023-2024&code=' + major)
            data_list = []
            if response.status_code == 200:
                for course in response.json():
                    offering = course['courseOffering']
                    term = course['term']
                    requisite_ids = course.get('courseOffering', {}).get('requisiteIds', [])
                    req = []
                    for id in requisite_ids:
                        if id == offering['id']:
                            req.append(offering['name'])
                    desc = offering['descr']['plain']
                    date = term['descr']['plain']
                    soup = BeautifulSoup(desc, 'html.parser')
                    desc_text = soup.get_text(separator=' ')
                    sections = requests.get('http://localhost:8080/waitlist/waitlistactivityofferings?courseOfferingId=' + offering['id'])
                    course_info = {}

                    for act in sections.json():
                        if isinstance(act, str):
                            continue
                        activity = act['activityOffering']
                        if activity:
                            course_id = offering['id']
                            instructors = activity.get('instructors', [])
                            schedule = act.get('scheduleNames', [])
                            if course_id in course_info:
                                course_info[course_id]['schedules'].extend(schedule)
                                course_info[course_id]['instructors'].extend([instructor.get('personName', '') for instructor in instructors])
                            else:
                                course_info[course_id] = {
                                    'schedules': schedule, 
                                    'instructors': [instructor.get('person', '') for instructor in instructors]
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
                            description=desc_text, 
                            date=date, 
                            schedule=schedules_str, 
                            instructor=instructors_str)
                        new_course.save()
                        data_list.append(new_course)
            for block in Course.objects.all():
                if Course.objects.filter(course_id=block.course_id).count() > 1:
                    block.delete()

            courses = Course.objects.all()

            if major:
                courses = courses.filter(title__icontains=major)
            if days:
                for day in days:
                    courses = courses.filter(schedule__icontains=day)
            if time:
                courses = courses.filter(schedule__in=time)
            distinct = {}
            for c in courses:
                distinct[c.title] = c
            print(distinct)
            filteredCourses = list(distinct.values())
            return render(request, "search_results.html", {'filtered_courses': filteredCourses})
    else:
        context = {}
        context['form'] = CourseFilterForm(initial={'time_slot': 'Early Morning (00:00-09:59)', 
                                            'days': 'Monday', 
                                            'subject_area': 'CSCI'})
        return render(request, "filters.html", context)


@login_required
def watchlist(request):
    user_watchlist_courses = Watchlist.objects.filter(user=request.user).select_related('section')
    sections = [entry.section for entry in user_watchlist_courses]
    seats_info = [{'course_title': section.title, 'current_seats': section.currentSeats, 'max_seats': section.maxSeats} for section in sections]
    
    context = {
        'user': request.user,
        'watchlist_courses': sections,
        'seats_info': seats_info
    }
    return render(request, "watchlist.html", context)


@login_required
@require_http_methods(["POST"])
def add_to_watchlist(request):
    try:
        current_state = SystemState.objects.latest('updated_at')
        if not current_state.state:  
            messages.error(request, "The system is currently closed. You cannot add courses to your watchlist.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    except SystemState.DoesNotExist:
        messages.error(request, "System state is not set. Please contact the administrator.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    section_id = request.POST.get('section_id')
    section = Section.objects.get(section_id=section_id)
    course = Course.objects.get(course_id=section.courseid)
    watchlist_entry, created = Watchlist.objects.get_or_create(user=request.user, section=section, course=course)
    if created:
        messages.success(request, "Course added to watchlist successfully.")
    else:
        messages.info(request, "This course is already in your watchlist.")


    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
@require_http_methods(["POST"])
def remove_from_watchlist(request):
    section_id = request.POST.get('section_id')
    section = get_object_or_404(Section, pk=section_id)    
    Watchlist.objects.filter(user=request.user, section=section).delete()
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def section_api_endpoint(request, id):
    recipient_email = request.session.get('email', 'recipient@example.com')
    user_watchlist_section_ids = Watchlist.objects.filter(user=request.user).values_list('section_id', flat=True)    
    registrationGroupResponse = requests.get("http://localhost:8080/waitlist/waitlistregistrationgroups?courseOfferingId=" + id).json()
    for entry in registrationGroupResponse:
        for section in entry['activityOfferings']:
            instructors = []
            for instructor in section['activityOffering']['instructors']:
                instructors.append(instructor['personName'])
            identity = section['activityOffering']['id']
            current = section['activitySeatCount']['used']
            max = section['activitySeatCount']['total']
            name = section['activityOffering']['formatOfferingName']
            locale = section['scheduleNames'][0]

            '''
            if current < max and Watchlist.objects.filter(user=request.user, course__course_id=courseID).exists():
                # Send email notification
                subject = f'Seats Available for {title}'
                message = f'There are {max - current} available seats for {title}.'
                ##html_message = render_to_string('email_notification_template.html', {'message': message})
                send_email(recipient_email, subject, message)
            '''

            course = Section.objects.get_or_create(section_id=identity,
                                instructor=';'.join(sorted(instructors)),
                                title=name, 
                                currentSeats=current, 
                                maxSeats=max, 
                                location=locale, 
                                courseid=id)


    
    # Deletes the duplicate objects after they're added
    
    queryset = Section.objects.filter(courseid=id)
    context = {
            'data': queryset,
            'user_watchlist_section_ids': user_watchlist_section_ids,
        }
    return render(request, 'section_selection.html', context)
def is_admin(user):
    return user.is_authenticated and user.is_staff
@login_required
@user_passes_test(is_admin)
def admin_report(request):
    snapshots = SystemSnapshot.objects.all().order_by('-created_at')
    selected_snapshot_id = None
    courses_data = []
    departments = Course.objects.values_list('department', flat=True).distinct()
    courses = Course.objects.values_list('title', flat=True).distinct()
    professors = Course.objects.values_list('instructor', flat=True).distinct()

    # Handling POST 
    if request.method == 'POST':
        selected_snapshot_id = request.POST.get('snapshot')
        if selected_snapshot_id:
            return apply_snapshot(request, selected_snapshot_id)

    # Handling GET 
    elif request.method == 'GET':
        selected_snapshot_id = request.GET.get('snapshot', None)
        if selected_snapshot_id:
            selected_snapshot = get_object_or_404(SystemSnapshot, id=selected_snapshot_id)
            courses_data = selected_snapshot.data['courses']
        else:
            courses_data = Course.objects.all().annotate(
                num_students_on_watch=Count('watchlist')
            ).annotate(
                max_students_watch=Max('watchlist__user_id'),
                min_students_watch=Min('watchlist__user_id'),
            )

    context = {
        'snapshots': snapshots,
        'selected_snapshot_id': selected_snapshot_id,
        'courses_data': courses_data,
        'departments': departments,
        'courses': courses,
        'professors': professors,
    }
    return render(request, 'admin_report.html', context)


def send_email(recipient, subject, message):
    send_mail(
        subject,
        message,
        'stoeva@bc.edu',  
        [recipient],
        fail_silently=False,
    )
@login_required
@user_passes_test(is_admin)
def detailed_report(request, course_id, snapshot_id):

    if not course_id or not snapshot_id:
        return redirect('admin_report')

    snapshot = get_object_or_404(SystemSnapshot, id=snapshot_id)
    snapshot_data = snapshot.data

    course_info = next((course for course in snapshot_data.get('courses', []) if course['course_id'] == course_id), None)
    if not course_info:
        return redirect('admin_report')

    sections_data = course_info.get('sections', [])

    context = {
        'course': course_info,
        'sections_data': sections_data,
    }
    return render(request, 'detailed_report.html', context)


@login_required
@user_passes_test(is_admin)
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

            if new_state_str.lower() == 'closed':
                capture_system_snapshot()

            return redirect('profile')
    else:
        initial_state = current_state.state if current_state else ''
        form = ChangeStateForm(initial={'state': initial_state})

    context = {'form': form, 'current_state': current_state.state if current_state else ''}
    return render(request, 'change_state.html', context)


    
from django.utils.timezone import now

def capture_system_snapshot():
    snapshot_name = f"End of Add/Drop {now().year}"

    courses_data = []
    for course in Course.objects.all():
        # Filter sections directly based on the course
        sections = Section.objects.filter(courseid=course.course_id)

        sections_data = []
        for section in sections:
            # Use select_related to optimize database queries
            watchers = Watchlist.objects.filter(section=section).select_related('user')
            watchers_data = [{
                'name': watcher.user.name,
                'email': watcher.user.email,
                'department': watcher.user.department,
            } for watcher in watchers]

            section_data = {
                'section_title': section.title,
                'section_id': section.section_id,
                'watchers': watchers_data,
            }
            sections_data.append(section_data)

        course_data = {
            'course_id': course.course_id,
            'title': course.title,
            'sections': sections_data,
        }
        courses_data.append(course_data)

    snapshot_data = {'courses': courses_data}
    SystemSnapshot.objects.create(name=snapshot_name, data=snapshot_data)


    

@login_required
@user_passes_test(is_admin)
def list_system_snapshots(request):
    snapshots = SystemSnapshot.objects.all().order_by('-created_at')  
    return render(request, 'list_system_snapshots.html', {'snapshots': snapshots})



def view_snapshot_report(request, snapshot_id):
    snapshot = get_object_or_404(SystemSnapshot, id=snapshot_id)
    
    context = {
        'snapshot': snapshot,
        'courses': snapshot.data.get('courses', []),
    }
    return render(request, 'snapshot_report.html', context)


@login_required
@user_passes_test(is_admin)
def apply_snapshot(request, snapshot_id):
    snapshot = get_object_or_404(SystemSnapshot, id=snapshot_id)
    snapshot_data = snapshot.data

    courses_data = []
    for course_info in snapshot_data.get('courses', []):
        total_watchers = 0
        for section_info in course_info.get('sections', []):
            total_watchers += len(section_info.get('watchers', []))  

        course_data = {
            'course_id': course_info.get('course_id'),
            'title': course_info.get('title'),
            'num_students_on_watch': total_watchers,  
        }
        courses_data.append(course_data)

    context = {
        'snapshots': SystemSnapshot.objects.all().order_by('-created_at'),
        'selected_snapshot_id': snapshot_id,
        'courses_data': courses_data,
    }

    return render(request, 'admin_report.html', context)
def change_seats(request, section_id):
    section = get_object_or_404(Section, section_id=section_id)

    if request.method == 'POST':
        section.change_seats()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def set_email(current, max, title, section_id, request):
    recipient_email = request.session.get('email', 'recipient@example.com')
    if current < max and Watchlist.objects.filter(user=request.user, section_id=section_id).exists():
            # Send email notification
            subject = f'Seats Available for {title}'
            message = f'There are {max - current} available seats for {title}.'
            ##html_message = render_to_string('email_notification_template.html', {'message': message})
            send_email(recipient_email, subject, message)