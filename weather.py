import threading
import requests

class Weather(threading.Thread):
    def __init__(self, queue=None):
        threading.Thread.__init__(self)
        self.queue = queue
    def run(self):
        requestLocationKey = requests.get('http://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey=p4ELZQs6MdrfP8AMCFGJ8CmQLF7KDehK&q=-6.279346,106.856874')
        if requestLocationKey.status_code == 200:
            responseLocationKey = requestLocationKey.json()
            locationKey = responseLocationKey['Key']

            requestsCurrentWeather = requests.get('http://dataservice.accuweather.com/currentconditions/v1/'+ locationKey +'?apikey=p4ELZQs6MdrfP8AMCFGJ8CmQLF7KDehK&language=id-ID')
            if requestsCurrentWeather.status_code == 200:
                responseCurrentWeather = requestsCurrentWeather.json()
                currentWeather = responseCurrentWeather[0]['WeatherText']
                print(currentWeather)
                self.queue.put({'name': 'Weather', 'result': currentWeather})
            else:
                print ('Request Current Weather Failed')
        else:
            print('Request Location Key Failed')
