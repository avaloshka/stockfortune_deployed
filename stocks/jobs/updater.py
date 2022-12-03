from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .jobs import Millioner

def start():
	scheduler = BackgroundScheduler()
	millioner = Millioner()

	scheduler.add_job(millioner.run_in_order(), 'interval', seconds=60*60*4)
	scheduler.start()