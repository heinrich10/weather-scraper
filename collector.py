import json
import os
from celery import Celery
from weather import Weather
from base import Session
from pytz import timezone

host = os.environ['REDIS_HOST']
port = os.environ['REDIS_PORT']

app = Celery('tasks', broker='redis://' + host + ':' + port + '/0')

@app.task(name='saveData')
def save(data):
	d = json.loads(data)
	session = Session()

	# check if data is in the DB
	q = session.query(Weather) \
	.filter(Weather.dt == d['dt']) \
	.filter(Weather.city == d['city']) \
	.count()
	print(q)

	# if data is not in db, save it
	if q <= 0:
		w = Weather(d['temp'], d['temp_min'], d['temp_max'], d['dt'], d['humidity'], d['city'])
		session.add(w)
		session.commit()
		session.close()
		print(str(data) + 'is saved')
	else:
		print('not saved')
	return