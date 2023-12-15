from django.http import HttpResponseRedirect
from .forms import ChangeStateForm,ExtraInfoForm_student,ExtraInfoForm_admin, CourseFilterForm

from django.shortcuts import redirect, render, get_object_or_404, get_object_or_404
from .models import Person, Student, SystemState, Course, Watchlist, Section, SystemSnapshot, MostPopularCourse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import login as auth_login, logout
from django.views.decorators.http import require_http_methods
import requests
from django.conf import settings
from authlib.integrations.django_client import OAuth
from urllib.parse import urlencode
import json
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from .constants import TIME_SLOTS
from django.core.paginator import Paginator
from django.contrib.auth.decorators import user_passes_test
from django.utils.timezone import now
from django.core.paginator import Paginator

ALLOWED_DAYS = {'M', 'T', 'W', 'TH', 'F', 'Tu', 'TuTh', 'MWF'}

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
                return redirect('courseselect')
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
                request.session["user_id"] = user.id  
                return redirect('student_extra_info')
            elif role == 'admin':
                request.session["email"] = email
                return redirect('admin_extra_info')
    return render(request, 'identity_selection.html')


def student_extra_info(request):
    user = Person.objects.get(id = request.session.get('user_id'))

    if request.method == 'POST':
        form = ExtraInfoForm_student(request.POST)
        if form.is_valid():
            student, student_created = Student.objects.update_or_create(
                person_ptr_id=user.id,
                defaults={
                    'name': user.name,
                    'department': form.cleaned_data.get('department'),
                    'eagle_id': form.cleaned_data.get('eagle_id'),
                    'graduation_semester': form.cleaned_data.get('graduation_semester'),
                    'major_1': form.cleaned_data.get('major_1'),
                    'major_2': form.cleaned_data.get('major_2'),
                    'major_3': form.cleaned_data.get('major_3'),
                    'minor_1': form.cleaned_data.get('minor_1'),
                    'minor_2': form.cleaned_data.get('minor_2'),
                }
            )

            user.is_active = True
            user.is_staff = False
            user.is_extra_info_filled_out = True
            user.save()

            auth_login(request, user)
            return redirect('courseselect')

    else:
        form = ExtraInfoForm_student()

    return render(request, 'student_extra_info.html', {'form': form})


@login_required
def course_selection(request):
    user_watchlist_course_ids = Watchlist.objects.filter(user=request.user).values_list('course_id', flat=True)
    all_courses = Course.objects.all()
    paginator = Paginator(all_courses, 10)
    page_number = request.GET.get('page', 1)
    request.session['last_course_page'] = page_number 
    page_obj = paginator.get_page(page_number)


    context = {
        'page_obj': page_obj,
        'courses': all_courses,
        'user_watchlist_ids': user_watchlist_course_ids,
        'form': CourseFilterForm()
    }
    return render(request, 'course_selection.html', context)


def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def user_profile(request):
    user = request.user
    if user.user_type == 'student':
        user_info = Student.objects.get(email=user.email)
    else:
        user_info = user


    system_state = SystemState.objects.get_or_create()[0].state
    try:
        system_state = SystemState.objects.get(id=1)
    except SystemState.DoesNotExist:
        system_state = None

    context = {
        'user': user_info,
        'system_state': system_state,
    }
    return render(request, 'profiles/profile.html', context)



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
            return redirect('courseselect') 
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
    subject_areas = [
    'AADS', 'ARTS', 'BIOL', 'CHEM', 'CSCI',
    'INTL','JOUR', 'LAWS', 'MATH', 'XRBC'
    ]
    for area in subject_areas:
        response = requests.get('http://localhost:8080/waitlist/waitlistcourseofferings?termId=kuali.atp.FA2023-2024&code='+area)
        data_list = []
        if response.status_code == 200:
            for entry in response.json():
                offering = entry['courseOffering']
                term = entry['term']
                description_html = offering['descr']['plain']
                date_text = term['descr']['plain']
                soup = BeautifulSoup(description_html, 'html.parser')
                description_text = soup.get_text(separator=' ')
                    
                new_course = Course(
                    title=offering['name'],
                    description=description_text,
                    date=date_text,
                )
                new_course.save()
                data_list.append(new_course)
    for block in Course.objects.all():
        if Course.objects.filter(course_id=block.course_id).count() > 1:
            block.delete()
    return render(request, 'course_selection.html', {'courses': data_list})

def search_results(request):
    if request.method == 'GET':
        search_query = request.GET.get('search_query', '').strip()
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

        paginator = Paginator(filtered_courses, 10)  
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        query_params = request.GET.copy()
        if 'page' in query_params:
            del query_params['page']
        current_query = query_params.urlencode()

        context = {
            'page_obj': page_obj,
            'courses': filtered_courses,
            'form': CourseFilterForm(),
            'current_query': current_query  
        }
        return render(request, 'search_results.html', context)

    

def filter(request):
    context = {}
    context['form'] = CourseFilterForm()
    return render(request, "filters.html", context)


def filterRequest(request):
    if request.method == 'GET':
        form = CourseFilterForm(request.GET)
        if form.is_valid():
            time_slot = form.cleaned_data.get('time_slot', [])
            days = form.cleaned_data.get('days', [])
            major = form.cleaned_data.get('subject_area', 'CSCI')

            courses = Course.objects.all()

            if major:
                courses = courses.filter(department__contains=major)
            if days:    
                first_day = days[0]
                courses = courses.filter(days__contains=first_day)
            if time_slot:
                courses = courses.filter(time_slots__contains=time_slot)

            filtered_courses = list(courses)

            paginator = Paginator(filtered_courses, 10)
            page_number = request.GET.get('page', 1)
            page_obj = paginator.get_page(page_number)
            query_params = request.GET.copy()
            if 'page' in query_params:
                del query_params['page']
            current_query = query_params.urlencode()

            context = {
                'page_obj': page_obj,
                'courses': filtered_courses,
                'form': CourseFilterForm(),
                'current_query': current_query  
            }


            return render(request, 'filters.html', context)


@login_required
def watchlist(request):
    user_watchlist_courses = Watchlist.objects.filter(user=request.user).select_related('section')
    sections = [entry.section for entry in user_watchlist_courses]


    if request.method == 'POST':
        sections = sort_sections(request, sections)

    combined_course_info = [(section, section.title.split()[1]) for section in sections]
    paginator = Paginator(combined_course_info, 10)
    page_number = request.GET.get('page', 1)
    request.session['last_course_page'] = page_number
    page_obj = paginator.get_page(page_number)

    context = {
        'user': request.user,
        'page_obj': page_obj,
    }
    return render(request, "watchlist.html", context)



@login_required
@require_http_methods(["POST"])
def add_to_watchlist(request):
    try:
        current_state = SystemState.objects.latest('updated_at')
        if not current_state.state:   
            messages.error(request, 'Sorry System is closed right now please contact Admin.')
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
            name = section['activityOffering']['name']
            locale = section['scheduleNames'][0]
            time = section['scheduleNames'][0].replace('Noon', 'PM')[-16:].strip()

            Section.objects.get_or_create(
                section_id=identity,
                defaults={
                    'instructor': ', '.join(instructors),
                    'title': name,
                    'location': locale,
                    'currentSeats': current,
                    'maxSeats': max,
                    'courseid': id,
                    'time': time
                }
            )
    queryset = Section.objects.filter(courseid=id)
    if request.method == 'POST':
        queryset = sort_sections(request, queryset)
    context = {
            'course_id' : id,
            'data': queryset,
            'user_watchlist_section_ids': user_watchlist_section_ids,
            'last_course_id': request.session.get('last_course_id')
        }
    return render(request, 'section_selection.html', context)

def is_admin(user):
    return user.is_authenticated and user.is_staff


def process_snapshot_data(snapshot_data):
    courses_data = []

    for course_info in snapshot_data.get('courses', []):

        course_data = {
            'course_id': course_info.get('course_id'),
            'title': course_info.get('title'),
            'num_students_on_watch': course_info.get('num_students_on_watch', 0),
            'max_students_on_watch': course_info.get('max_students_on_watch', 0),
            'min_students_on_watch': course_info.get('min_students_on_watch', 0),
        }
        courses_data.append(course_data)

    return courses_data

@login_required
@user_passes_test(is_admin)
def admin_report(request):
    snapshots = SystemSnapshot.objects.all().order_by('-created_at')
    courses = Course.objects.values_list('title', flat=True).distinct()
    page_number = request.GET.get('page', 1)
    request.session['last_course_page'] = page_number
    most_popular_course_instance = MostPopularCourse.objects.all().first()

    if most_popular_course_instance:
        most_popular_course = most_popular_course_instance.most_popular_course
        most_popular_course_count = most_popular_course_instance.most_popular_course_count
    else:
        most_popular_course = "Not Available"
        most_popular_course_count = 0

    selected_snapshot_id = None
    snapshot_data = request.session.get('snapshot_data')

    if request.method == 'POST':
        snapshot_id = request.POST.get('snapshot')
        if snapshot_id:
            return apply_snapshot(request, snapshot_id)
            

    if snapshot_data:
        selected_snapshot_id = request.session.get('selected_snapshot_id')
        most_popular_course_instance = MostPopularCourse.objects.filter(snapshot_id=selected_snapshot_id).first()
        if most_popular_course_instance:
            most_popular_course = most_popular_course_instance.most_popular_course
            most_popular_course_count = most_popular_course_instance.most_popular_course_count
        courses_data = process_snapshot_data(snapshot_data)
        paginator = Paginator(courses_data, 9)
        paginated_courses_data = paginator.get_page(page_number)
        selected_course = request.GET.get('course', '')

        courses_query = Course.objects.all()

        if selected_course:
            courses_query = courses_query.filter(title__icontains=selected_course)

        context = {
            'snapshots': snapshots,
            'selected_snapshot_id': selected_snapshot_id,
            'courses_data': paginated_courses_data,
            'courses': courses,
            'filtered_courses': courses_query,
            'MostPopularCourse': most_popular_course,
            'MostPopularCourseCount': most_popular_course_count,
        }

    else:
        selected_snapshot_id = request.GET.get('snapshot', None)
        selected_course = request.GET.get('course', '')

        if selected_snapshot_id:
            selected_snapshot = get_object_or_404(SystemSnapshot, id=selected_snapshot_id)
            request.session['snapshot_data'] = selected_snapshot.data
            request.session['selected_snapshot_id'] = selected_snapshot_id
            return redirect('admin_report')

        courses_query = Course.objects.all()

        if selected_course:
            courses_query = courses_query.filter(title__icontains=selected_course)
        

        paginator = Paginator(courses_query, 9)
        paginated_courses_data = paginator.get_page(page_number)

    context = {
        'snapshots': snapshots,
        'selected_snapshot_id': selected_snapshot_id,
        'courses_data': paginated_courses_data,
        'courses': courses,
        'filtered_courses': courses_query,
        'MostPopularCourse': most_popular_course,
        'MostPopularCourseCount': most_popular_course_count,
    }

    return render(request, 'admin_report.html', context)


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
    most_popular_courses_count = 0
    most_popular_courses_title = '' 
    
    for course in Course.objects.all():
        sections = Section.objects.filter(courseid=course.course_id)
        sections_data = []
        course_watcher = 0
        for section in sections:
            watchers = Watchlist.objects.filter(section=section)
            section_watcher_count = len(watchers)
            course_watcher += section_watcher_count
            watchers_data = [{
                'name': watcher.user.name,
                'email': watcher.user.email,
                'department': watcher.user.department,
            } for watcher in watchers]

            section_data = {
                'section_title': section.title,
                'section_id': section.section_id,
                'watchers': watchers_data,
                'section_watcher_count': section_watcher_count,
            
            }

            sections_data.append(section_data)
        course.max_students_on_watch = max(course_watcher, course.max_students_on_watch)
        
        if course_watcher > most_popular_courses_count:
            most_popular_courses_count = course_watcher
            most_popular_courses_title = course.title
       

        most_popular_courses_count = max(most_popular_courses_count, course_watcher)
        
        course_data = {
            'course_id': course.course_id,
            'title': course.title,
            'sections': sections_data,
            'num_students_on_watch': course_watcher,
            'max_students_on_watch': course.max_students_on_watch,
            
        }      
        courses_data.append(course_data)
    
    snapshot_data = {'courses': courses_data}
    SystemSnapshot.objects.create(
        name=snapshot_name, 
        data=snapshot_data,
    )

    MostPopularCourse.objects.update_or_create(
        snapshot_id=SystemSnapshot.objects.latest('created_at').id,
        defaults={
            'most_popular_course': most_popular_courses_title,
            'most_popular_course_count': most_popular_courses_count,
        }
    )
    
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
    request.session['snapshot_data'] = snapshot.data  
    request.session['selected_snapshot_id'] = snapshot_id  

    return redirect('admin_report')  



@require_http_methods(['POST'])
def sort_sections(request, queryset):
    queryset = list(queryset)
    try:
        parameter = request.POST['sort']
    except:
        parameter='default'
    
    sort_functions = {
                    'default': lambda section: section.title,
                    'teacher_ascending' : lambda section : section.instructor,
                    'teacher_descending' : lambda section: section.instructor,
                    'max_seats_ascending': lambda section: section.maxSeats,
                    'max_seats_descending' : lambda section: section.maxSeats,
                    'open_seats_ascending' : lambda section: section.maxSeats - section.currentSeats,
                    'open_seats_descending' : lambda section: section.maxSeats - section.currentSeats,
                    'time_ascending': lambda section: section.time,
                    'time_descending': lambda section: section.time
    }

    reversed_queries = {'teacher_descending', 'max_seats_descending', 'open_seats_descending', 'time_descending'}
    queryset.sort(key=sort_functions[parameter], reverse=parameter in reversed_queries)
    if parameter == 'time_ascending' or parameter == 'time_descending':
        morning = [section for section in queryset if 'AM' in section.time[:7]]
        night = [section for section in queryset if 'PM' in section.time[:7]]
        if parameter in reversed_queries:
            queryset = night + morning
        else:
            queryset = morning + night
    return queryset

@require_http_methods(['POST'])
def filter_sections(request, queryset):
    queryset = list(queryset)
    time_functions = {
                        'morning': lambda time: int(time[:2]) < 12 and time[5] == 'A',
                        'afternoon': lambda time: (int(time[:2]) == 12 or int(time[:2]) <= 5) and (time[6] == 'P' or time[5] == 'P'),
                        'evening': lambda time: int(time[:2]) > 5 and time[5] == 'P' 
    }
    filter_functions = {
                        'department': lambda section, option: section.title[:4] in request.POST.getlist('department'),
                        'open_seats': lambda section, option: section.maxSeats - section.currentSeats > 0,
                        'time': lambda section, option: time_functions[option](section.time)
    }

    filter_options = ['department', 'time', 'open_seats']
    new_queryset = []

    for option in filter_options:
        if option in request.POST:
            for selection in request.POST.getlist(option):
                new_queryset += [section for section in queryset if filter_functions[option](section, selection)]
    return list(set(new_queryset))

def course_report_filter(request):
    selected_course = request.GET.get('course')
    all_courses = Course.objects.all()

    if selected_course:
        filtered_courses = Course.objects.filter(title__icontains=selected_course)
    else:
        filtered_courses = all_courses

    context = {
        'courses_data': filtered_courses,
        'all_courses': all_courses
    }
    return render(request, 'admin_report.html', context)