import json, requests
import random
from datetime import timedelta, date

url = 'http://flythings.itg.es/api/observation/multiple'

headers = {'x-auth-token': 'PUT_YOUR_TOKEN',
           'workspace': 000, #PUT_YOUR_WORKSPACE
           'Content-Type': 'application/json'}

observations = []

def send(observations):
    print('Num observaciones: ', len(observations))
    r = requests.put(url, data=json.dumps({'observations': observations}), headers=headers)
    print(r.text)

def addObservation(foi, procedure, property, timestamp, value, uom):
    jsonMessage = {
        'foi': foi,
        'procedure': procedure,
        'observableProperty': property,
        'time': timestamp,
        'value': float(value),
        'uom': uom
    }
    observations.append(jsonMessage)


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


if __name__ == '__main__':
    initDate = date(2015, 1, 1)
    endDate = date(2017, 1, 1)
    for currentDate in daterange(initDate, endDate):
        addObservation("python","python","python", int(currentDate.strftime("%s"))*1000, random.randrange(30,70), "python")
    send(observations)

