from server import Server

if __name__ == '__main__':
    
    serverSemantic = Server()
    # getWeather = Weather(queue=clientServerQueue)

    serverSemantic.start()
    # getWeather.start()
    
