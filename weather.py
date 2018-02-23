import requests

class Weather():
    def run(latitude, longitude):
        requestLocationKey = requests.get('http://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey=p4ELZQs6MdrfP8AMCFGJ8CmQLF7KDehK&q='+ latitude +','+ longitude)
        if requestLocationKey.status_code == 200:
            responseLocationKey = requestLocationKey.json()
            locationKey = responseLocationKey['Key']

            requestsCurrentWeather = requests.get('http://dataservice.accuweather.com/currentconditions/v1/'+ locationKey +'?apikey=p4ELZQs6MdrfP8AMCFGJ8CmQLF7KDehK&language=id-ID')
            if requestsCurrentWeather.status_code == 200:
                responseCurrentWeather = requestsCurrentWeather.json()
                currentWeather = responseCurrentWeather[0]['WeatherText']
            else:
                print ('Request Current Weather Failed')
                currentWeather = ""
        else:
            print('Request Location Key Failed')
            currentWeather = ""
        
        return currentWeather
