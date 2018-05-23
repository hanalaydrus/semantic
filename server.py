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

from Queue import LifoQueue
from concurrent import futures
from datetime import datetime

from client import ClientDensity, ClientVolume 
from weather import Weather
from model import Model

import time
import threading
import string
import random
import logging
import grpc
import numpy

import semanticContract_pb2
import semanticContract_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
exitFlag = 0
concurrent = 0

def TimestampMillisec64():
    return int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() * 1000)

class Greeter(semanticContract_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        global concurrent
        i = 0
        log = []
        concurrent = concurrent + 1
        camera_id = request.id % 10
        random_id = str(request.id)
        # model get camera data
        model = Model()
        model_camera = model.request_data(camera_id)

        # thread client density
        client_density_queue = LifoQueue(1)
        client_density = ClientDensity(camera_id, "density-service:50050", "client_density", queue=client_density_queue)
        client_density.start()

        # thread client volume
        client_volume_queue = LifoQueue(1)
        client_volume = ClientVolume(camera_id, "volume-service:50051", "client_volume", queue=client_volume_queue)
        client_volume.start()

        # thread client volume
        client_weather_queue = LifoQueue(1)
        client_weather = Weather("client_volume", model_camera['latitude'], model_camera['longitude'], queue=client_weather_queue)
        client_weather.start()

        def join_thread():
            client_density.stop()
            client_volume.stop()
            client_weather.stop()
            
            client_density.join()
            client_volume.join()
            client_weather.join()

        context.add_callback(join_thread)

        while True:
            density_queue = client_density_queue.get()
            volume_queue = client_volume_queue.get()
            weather_queue = client_weather_queue.get()

            current_weather = weather_queue['weather']

            if density_queue['density'] == 'timeout' and volume_queue['percentage'] != 'timeout':
                if "hujan" in current_weather.lower():
                    if (volume_queue['percentage'] > 0) :
                        sentence = ("Hujan mengguyur %s. Terjadi kenaikan volume kendaraan sebesar %d persen dibandingkan lalu lintas normal." % (model_camera['street_name'], volume_queue['percentage']))
                    elif (volume_queue['percentage'] == 0) :
                        sentence = ("Hujan mengguyur %s. volume lalu lintas terpantau normal.")
                    else:
                        sentence = ("Hujan mengguyur %s. terjadi penurunan volume kendaraan sebesar %d persen dibandingkan lalu lintas normal." % (model_camera['street_name'], volume_queue['percentage']))
                else:
                    if (volume_queue['percentage'] > 0) :
                        sentence = ("Pada %s, terjadi kenaikan volume kendaraan sebesar %d persen dibandingkan lalu lintas normal." % (model_camera['street_name'], volume_queue['percentage']))
                    elif (volume_queue['percentage'] == 0) :
                        sentence = ("Pada %s, volume lalu lintas terpantau normal.")
                    else:
                        sentence = ("Pada %s, terjadi penurunan volume kendaraan sebesar %d persen dibandingkan lalu lintas normal." % (model_camera['street_name'], volume_queue['percentage']))
            
            elif density_queue['density'] != 'timeout' and volume_queue['percentage'] == 'timeout':
                if "hujan" in current_weather.lower():
                    sentence = ("Hujan mengguyur %s. Arus lalu lintas terpantau %s." % (model_camera['street_name'], density_queue['density'].lower() ))
                else:
                 sentence = ("%s terpantau %s." % (model_camera['street_name'], density_queue['density'].lower() ))
            
            else:
                #########
                if "hujan" in current_weather.lower():
                    sentence = ("Hujan mengguyur %s. Arus lalu lintas terpantau %s." % (model_camera['street_name'], density_queue['density'].lower() ))
                else:
                    sentence = ("%s terpantau %s." % (model_camera['street_name'], density_queue['density'].lower() ))
                ########
                if (volume_queue['percentage'] > 0) :
                    sentence = sentence + ("Terjadi kenaikan volume kendaraan sebesar %d persen dibandingkan lalu lintas normal." % (volume_queue['percentage']))
                elif (volume_queue['percentage'] == 0) :
                    sentence = sentence + ("Volume lalu lintas normal.")
                else:
                    sentence = sentence + ("Terjadi penurunan volume kendaraan sebesar %d persen dibandingkan lalu lintas normal." % (volume_queue['percentage']))

            yield semanticContract_pb2.HelloReply(response='%s' % sentence)

            log.append([random_id, TimestampMillisec64(), str(concurrent)])
            i = i + 1
            if i == 1000:
                a = numpy.asarray(log)
                numpy.savetxt("cc"+random_id+".csv", a, fmt="%s", delimiter=",")
                print("finish logging cc: %d" % concurrent)
                concurrent = concurrent - 1

        

class Server(threading.Thread):
    def __init__(self, threadName):
        threading.Thread.__init__(self)
        self.threadName = threadName

    def run(self):
        if exitFlag:
            self.threadName.exit()
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=21))
        semanticContract_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)

        server.add_insecure_port('[::]:50049')
        server.start()

        print("server listening on port 50049")
              
        try:
            while True:
                time.sleep(_ONE_DAY_IN_SECONDS)
        except KeyboardInterrupt:
            server.stop(0)
