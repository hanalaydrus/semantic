# Copyright 2015 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""The Python implementation of the GRPC helloworld.Greeter server."""

from queue import LifoQueue
from concurrent import futures

from client import ClientDensity, ClientVolume 
from weather import Weather
from model import Model

import time
import threading

import grpc

import semanticContract_pb2
import semanticContract_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

class Greeter(semanticContract_pb2_grpc.GreeterServicer):

    def SayHello(self, request, context):
        # model get camera data
        model_camera = Model.run(request.id)

        # thread client density
        client_density_queue = LifoQueue()
        client_density = ClientDensity(request.id, "localhost:50050", "client_density", queue=client_density_queue)
        client_density.start()

        # thread client volume
        client_volume_queue = LifoQueue()
        client_volume = ClientVolume(request.id, "localhost:50051", "client_volume", queue=client_volume_queue)
        client_volume.start()

        while True:
            density_queue = client_density_queue.get()
            volume_queue = client_volume_queue.get()

            # current_weather = Weather.run(model_camera['latitude'],model_camera['longitude'])
            # if "hujan" in current_weather.lower():
            #     sentence = ("Hujan mengguyur %s. Arus lalu lintas terpantau %s." % (model_camera['street_name'], density_queue['density'].lower() ))
            # else:
            sentence = ("%s terpantau %s." % (model_camera['street_name'], density_queue['density'].lower() ))

            if (volume_queue['percentage'] > 0) :
                sentence = sentence + (" Terjadi kenaikan volume kendaraan sebesar %d persen dibandingkan lalu lintas normal." % (volume_queue['percentage']))
            elif (volume_queue['percentage'] == 0) :
                sentence = sentence + (" Volume lalu lintas normal.")
            else:
                sentence = sentence + (" Terjadi penurunan volume kendaraan sebesar %d persen dibandingkan lalu lintas normal." % (volume_queue['percentage']))
            
            yield semanticContract_pb2.HelloReply(response='%s' % sentence)

class Server(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        semanticContract_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
        server.add_insecure_port('[::]:50049')
        server.start()
              
        try:
            while True:
                time.sleep(_ONE_DAY_IN_SECONDS)
        except KeyboardInterrupt:
            server.stop(0)
