from queue import Queue

from greeter_client import Client
from greeter_server import Server

if __name__ == '__main__':
    clientServerQueue = Queue()
    clientVolume = Client("Volume","localhost:50051", "clientVolume", queue=clientServerQueue)
    clientDensity = Client("Density","localhost:50050", "clientDensity", queue=clientServerQueue)
    serverSemantic = Server(queue=clientServerQueue)

    clientVolume.start()
    clientDensity.start()
    serverSemantic.start()
