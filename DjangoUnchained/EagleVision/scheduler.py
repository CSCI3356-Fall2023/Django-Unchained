# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from django.core.mail import send_mail
from .models import Section, Watchlist
from .scheduled_jobs import change_seats_job, check_and_notify

def run_schedule():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_and_notify, 'cron', hour = '23')  
    scheduler.add_job(change_seats_job, 'cron', hour = '23')  
    scheduler.start()