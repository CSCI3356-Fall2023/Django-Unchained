
from django.conf import settings
from django.core.mail import send_mail
from EagleVision.models import Section, Watchlist

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
            message = f'There are {section.maxSeats - section.currentSeats} available seats for {section.title}. Register soon since seats may fill up quickly'
            print(message)
            #send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
        course_available.append({'title': section.title, 'available_seats': section.maxSeats - section.currentSeats})

    if course_available:
        # Send a single email if there are more than five seats available
        subject = 'Courses with Available Seats in Watchlist'
        message = '\n'.join([
            f'{course["title"]}: {course["available_seats"]} available seats'
            for course in course_available
        ])
        print()
        print(message)
        #send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])