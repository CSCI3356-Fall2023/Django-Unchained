
from django.conf import settings
from django.core.mail import send_mail
from EagleVision.models import Section, Watchlist
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from .models import Course
from django.conf import settings


ALLOWED_DAYS = {'M', 'T', 'W', 'TH', 'F', 'Tu', 'TuTh', 'MWF'}

def change_seats_job():
    sections = Section.objects.all()
    for section in sections:
        section.change_seats()

def check_and_notify():
    watchlist_entries = Watchlist.objects.all()
    course_available=[]

    for watchlist_entry in watchlist_entries:
        user = watchlist_entry.user
        section = watchlist_entry.section

        # Send priority email less than five seats
        if section.maxSeats - section.currentSeats < 6:
            subject = f'Only {section.maxSeats - section.currentSeats} seats available for {section.title}'
            message = f'There are {section.maxSeats - section.currentSeats} available seats for {section.title}. Register soon since seats may fill up quickly.'
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
        course_available.append({'title': section.title, 'available_seats': section.maxSeats - section.currentSeats})

    if course_available:
        # Send a single email if there are more than five seats available
        subject = 'Courses with Available Seats in Watchlist'
        message = '\n'.join([
            f'{course["title"]}: {course["available_seats"]} available seats'
            for course in course_available
        ])
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
    
def load_courses():
    response = requests.get(f'{settings.API_BASE_URL}/waitlist/waitlistcourseofferings?termId=kuali.atp.FA2023-2024&code=')
    if response.status_code == 200:
        for entry in response.json():
            offering = entry['courseOffering']
            term = entry['term']
            description_html = offering['descr']['plain']
            date_text = term['descr']['plain']
            soup = BeautifulSoup(description_html, 'html.parser')
            description_text = soup.get_text(separator=' ')

            new_response = requests.get(f'http://localhost:8080/waitlist/waitlistactivityofferings?courseOfferingId={offering["id"]}')
            
            course_info = {}

            for new_entry in new_response.json():
                if isinstance(new_entry, str):
                    continue

                activity = new_entry.get('activityOffering')
                if activity:
                    course_id = offering['id']
                    instructors = activity.get('instructors', [])
                    schedule_names = new_entry.get('scheduleNames', [])
                    cleaned_schedule = clean_schedule_string(''.join(schedule_names))
                    time_slots = []
                    for schedule in cleaned_schedule:
                        if len(schedule) == 3:
                            location, day, time = schedule

                            time_slot = get_time_slot(time)
                            time_slots.append(time_slot)
                        else:
        
                            time_slots.append('Unknown')

                    days = []
                    for schedule in cleaned_schedule:
                        if len(schedule) >= 2:
                            _, day, *_ = schedule
                            if day in ALLOWED_DAYS:
                                days.append(day)


                    if course_id in course_info:
                        course_info[course_id]['time_slots'].extend(time_slots)
                        course_info[course_id]['days'].extend(days)
                        course_info[course_id]['instructors'].extend([instructor.get('personName', '') for instructor in instructors])
                    else:
                        course_info[course_id] = {
                            'time_slots': time_slots,
                            'days': days,
                            'instructors': [instructor.get('personName', '') for instructor in instructors],
                        }

            for course_id, info in course_info.items():
                unique_instr = list(set(info['instructors']))
                instructors_str = ', '.join(sorted(unique_instr))
                unique_days = list(set(info['days']))  
                days_str = ', '.join(sorted(unique_days))
                department = offering['name'][:4]
                
                Course.objects.get_or_create(
                    course_id=course_id,
                    defaults={
                        'title': offering['name'],
                        'description': description_text,
                        'date': date_text,
                        'schedule': ', '.join(schedule_names),
                        'instructor': instructors_str,
                        'time_slots': time_slots, 
                        'days': days_str,
                        'department': department
                    }
                )
                
def standardize_time_format(time_str):
    if time_str == 'ARRANGEMENT' or time_str == 'Arrangement' or time_str == 'Asynchronous'or time_str == 'TBA':
        return 'BY ARRANGEMENT'
    time_str = time_str.replace('NOON', '12:00 PM').replace('Noon', '12:00 PM')
    time_str = re.sub(r"(AM|PM)", r" \1", time_str, flags=re.IGNORECASE)
    return time_str


def clean_schedule_string(schedule_str):
    sessions = schedule_str.split(', ')
    cleaned_sessions = []

    for session in sessions:
        if "Asynchronous" in session or "Arrangement" in session:
            cleaned_sessions.append(('Online', 'BY ARRANGEMENT'))
            continue

        parts = session.split(' ')
        if len(parts) >= 2:
            day, time = parts[-2], parts[-1]
            if day.lower() == 'by':
                time = 'BY ARRANGEMENT'
            else:
                time = standardize_time_format(time)
            cleaned_sessions.append((session.replace(day, '').replace(time, '').strip(), day, time))
        else:
            cleaned_sessions.append(('Unknown', 'Unknown'))

    return cleaned_sessions




def get_time_slot(start_time_str):
    standardized_time = standardize_time_format(start_time_str.split('-')[0].strip())

    if standardized_time == 'BY ARRANGEMENT' or not is_valid_time(standardized_time):
        return 'BY ARRANGEMENT'

    start_time = datetime.strptime(standardized_time, '%I:%M %p')

    if start_time.hour < 10:
        return 'early_morning'
    elif 10 <= start_time.hour < 12:
        return 'late_morning'
    elif 12 <= start_time.hour < 16:
        return 'early_afternoon'
    elif 16 <= start_time.hour < 18:
        return 'late_afternoon'
    else:
        return 'evening'

def is_valid_time(time_str):
    try:
        datetime.strptime(time_str, '%I:%M %p')
        return True
    except ValueError:
        return False
