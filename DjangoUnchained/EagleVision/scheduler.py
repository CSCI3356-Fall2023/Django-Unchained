# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from django.core.mail import send_mail
from .models import Section, Watchlist
from .scheduled_jobs import change_seats_job, check_and_notify

def run_schedule():
    scheduler = BackgroundScheduler()
    print("here")
    scheduler.add_job(check_and_notify, 'cron', second='10')  # Adjust the interval as needed
    scheduler.add_job(change_seats_job, 'cron', second='15')
    scheduler.start()