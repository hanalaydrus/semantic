from Queue import LifoQueue, Full
import requests
import threading
import time

exitFlag = 0
myLock = threading.Lock()

def set_start_request(startRequest):
    startRequest = True

class Weather(threading.Thread):
    def __init__(self, threadName, latitude, longitude, data):
        threading.Thread.__init__(self)
        self.threadName = threadName
        self.latitude = latitude
        self.longitude = longitude
        self.data = data
        self.startRequest = True
        self.weather = "unavailable"
        self.startService = True
        self.timer = threading.Timer(600, set_start_request, args=(self.startRequest,))

    def run(self):
        while self.startService:
            if self.startRequest:
                try:
                    requestLocationKey = requests.get("http://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey=zUAxVR88QcZr5j4hpl4IxMUnuxixTnfd&q="+ self.latitude +","+ self.longitude)
                except Exception:
                    print("Request Failed, problem with connection")
                    try:
                        self.data.put_nowait({'weather': self.weather})
                    except Full:
                      continue

                if requestLocationKey.status_code == 200:
                    responseLocationKey = requestLocationKey.json()
                    locationKey = responseLocationKey["Key"]
                    try:
                        requestsCurrentWeather = requests.get("http://dataservice.accuweather.com/currentconditions/v1/"+ locationKey +"?apikey=zUAxVR88QcZr5j4hpl4IxMUnuxixTnfd&language=id-ID")
                    except Exception:
                        print("Request Failed, problem with connection")
                        try:
                            self.data.put_nowait({'weather': self.weather})
                        except Full:
                            continue

                    if requestsCurrentWeather.status_code == 200:
                        responseCurrentWeather = requestsCurrentWeather.json()
                        self.weather = responseCurrentWeather[0]["WeatherText"]
                    else:
                        print ("Request Current Weather Failed")
                else:
                    print("Request Location Key Failed")
                self.startRequest = False
                self.timer.start()

            try:
                self.data.put_nowait({'weather': self.weather})
            except Full:
                continue

    def stop(self):
        self.startService = False
        self.timer.cancel()

