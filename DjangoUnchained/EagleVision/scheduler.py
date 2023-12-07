# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from django.core.mail import send_mail
from .models import Section, Watchlist

def check_and_notify():
    sections = Section.objects.all()

    for section in sections:
        watchlist_entries = Watchlist.objects.filter(section=section)

        for watchlist_entry in watchlist_entries:
            user = watchlist_entry.user
            if section.currentSeats < section.maxSeats:
                # Send email notification
                subject = f'Seats Available for {section.title}'
                message = f'There are {section.maxSeats - section.currentSeats} available seats for {section.title}.'
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

scheduler = BackgroundScheduler()
scheduler.add_job(check_and_notify, 'interval', minutes=60)  # Adjust the interval as needed
scheduler.start()
