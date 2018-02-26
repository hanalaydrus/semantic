import requests
import threading
import time

exitFlag = 0

def set_start_request(startRequest):
    startRequest = True

class Weather(threading.Thread):
    def __init__(self, threadName, latitude, longitude, queue=None):
        threading.Thread.__init__(self)
        self.threadName = threadName
        self.latitude = latitude
        self.longitude = longitude
        self.queue = queue
        self.startRequest = True
        self.weather = "unavailable"
        self.startService = True

    def run(self):
        if exitFlag:
            self.threadName.exit()
        while self.startService:
            if self.startRequest:
                try:
                    requestLocationKey = requests.get('http://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey=zUAxVR88QcZr5j4hpl4IxMUnuxixTnfd&q='+ self.latitude +','+ self.longitude)
                except Exception:
                    print("Request Failed, problem with connection")
                    self.queue.put({'weather': self.weather})
                    continue

                if requestLocationKey.status_code == 200:
                    responseLocationKey = requestLocationKey.json()
                    locationKey = responseLocationKey['Key']
                    try:
                        requestsCurrentWeather = requests.get('http://dataservice.accuweather.com/currentconditions/v1/'+ locationKey +'?apikey=zUAxVR88QcZr5j4hpl4IxMUnuxixTnfd&language=id-ID')
                    except Exception:
                        print("Request Failed, problem with connection")
                        self.queue.put({'weather': self.weather})
                        continue

                    if requestsCurrentWeather.status_code == 200:
                        responseCurrentWeather = requestsCurrentWeather.json()
                        self.weather = responseCurrentWeather[0]['WeatherText']
                    else:
                        print ('Request Current Weather Failed')
                else:
                    print('Request Location Key Failed')
                self.startRequest = False
                t = threading.Timer(600, set_start_request(self.startRequest))
                t.start()

            self.queue.put({'weather': self.weather})

    def stop(self):
        self.startService = False