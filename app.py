
import flask
from flask import jsonify, request

from weather import Weather
from base import Session

MAX_LIMIT = 20

app = flask.Flask(__name__)

@app.route('/')
def main():
    return 'ok'


@app.route('/weather', methods=['GET'])
def getWeather():
    city = request.args.get('city')
    start = request.args.get('start')
    end = request.args.get('end')
    limit = request.args.get('limit')
    
    session = Session()
    weather = _filter(session, city, start, end, limit)
    data = []
    for w in weather:
        d = w.__dict__
        d['temp'] = float(d['temp'])
        del d['_sa_instance_state']
        data.append(d)
    session.close()
    return jsonify(data)

def _filter(session, city, start, end, limit):
    q = session.query(Weather)

    if city is not None:
        q = q.filter(Weather.city == city)

    if start is not None:
        q = q.filter(Weather.dt >= start)

    if end is not None:
        q = q.filter(Weather.dt <= end)

    if limit is not None:
        q = q.limit(limit)
    else:
        q = q.limit(MAX_LIMIT)

    return q.all()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002)
