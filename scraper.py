import requests
import json
import os
from celery import Celery
from datetime import datetime, timedelta
from pytz import timezone

host = os.environ['REDIS_HOST']
port = os.environ['REDIS_PORT']

API_KEY = '48bbaebf7c231fd1aa7bb98ef93d6f39'
HK = 1819730
SG = 1880251

cel = Celery('tasks', broker='redis://' + host + ':' + port + '/0')

@cel.task(name='scrapeData')
def scrape():
	queryString = {
		'id': str(HK) + ',' + str(SG),
		'APPID': API_KEY,
		'units': 'metric'
	}

	r = requests.get('http://api.openweathermap.org/data/2.5/group', params=queryString)

	if r.status_code == 200:
		data = r.json()['list']
		for d in data:
			city = 'XX'
			if d['id'] == HK:
				city = 'HK'
			elif d['id'] == SG:
				city = 'SG'
			data = {
				'temp': d['main']['temp'],
				'temp_min': d['main']['temp_min'],
				'temp_max': d['main']['temp_max'],
				'humidity': d['main']['humidity'],
				'dt': d['dt'],
				'city': city
			}
			# save to DB
			cel.send_task('saveData', kwargs={'data':json.dumps(data)})

		# compute next action
		nextTime = datetime.now(timezone('Asia/Hong_Kong')) + timedelta(minutes=1)
		cel.send_task('scrapeData', eta=nextTime, queue='timer')
		return
	elif r.status_code == 429:
		print('429 retrying much later')
		nextTime = datetime.now(timezone('Asia/Hong_Kong')) + timedelta(hours=1)
		cel.send_task('scrapeData', eta=nextTime, queue='timer')
		# do something
	else:
		# do another
		print('warn users, there is an error')
		nextTime = datetime.now(timezone('Asia/Hong_Kong')) + timedelta(hours=1)
		cel.send_task('scrapeData', eta=nextTime, queue='timer')

#start task
scrape()
