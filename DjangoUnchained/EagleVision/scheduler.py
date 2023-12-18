# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from .scheduled_jobs import change_seats_job, check_and_notify, load_courses

def run_schedule():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_and_notify, 'cron', second = '30')  
    scheduler.add_job(change_seats_job, 'cron', second = '30')  
    scheduler.add_job(load_courses, 'interval', minutes = 1)
    scheduler.start()
    