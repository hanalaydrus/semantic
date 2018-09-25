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
from Queue import Empty
from concurrent import futures

from client import ClientDensity, ClientVolume 
from weather import Weather
from model import Model

import time
import threading
import multiprocessing

import grpc

import semanticContract_pb2
import semanticContract_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

myLock = threading.Lock()

class Greeter(semanticContract_pb2_grpc.GreeterServicer):

    def SayHello(self, request, context):
        # model get camera data
        model = Model()
        model_camera = model.request_data(request.id)

        # thread client density
        density_queue = multiprocessing.Queue(1)
        client_density = ClientDensity(request.id, "density-service:50050", "client_density", density_queue)
        client_density.start()

        # thread client volume
        volume_queue = multiprocessing.Queue(1)
        client_volume = ClientVolume(request.id, "volume-service:50051", "client_volume", volume_queue)
        client_volume.start()

        # thread client volume
        weather_queue = multiprocessing.Queue(1)
        client_weather = Weather("client_weather", model_camera["latitude"], model_camera["longitude"], weather_queue)
        client_weather.start()

        def join_thread():
            client_density.stop()
            client_volume.stop()
            client_weather.stop()

            client_density.join()
            client_volume.join()
            client_weather.join()

            myLock.acquire(True)
            print("finish-thread %d active: %d" % (request.id,threading.active_count()))
            # print(threading.enumerate())
            # print("finish akhir")
            myLock.release()

        context.add_callback(join_thread)
        
        while True:
            density_data = density_queue.get()
            volume_data = volume_queue.get()
            weather_data = weather_queue.get()

            current_weather = weather_data["weather"]

            if density_data["density"] == "timeout" and volume_data["percentage"] != "timeout":
                if "hujan" in current_weather.lower():
                    if (volume_data["percentage"] > 0) :
                        sentence = ("Hujan mengguyur %s. Terjadi kenaikan volume kendaraan sebesar %d persen dibandingkan lalu lintas normal." % (model_camera["street_name"], volume_data["percentage"]))
                    elif (volume_data["percentage"] == 0) :
                        sentence = ("Hujan mengguyur %s. volume lalu lintas terpantau normal.")
                    else:
                        sentence = ("Hujan mengguyur %s. Terjadi penurunan volume kendaraan sebesar %d persen dibandingkan lalu lintas normal." % (model_camera["street_name"], volume_data["percentage"]))
                else:
                    if (volume_data["percentage"] > 0) :
                        sentence = ("Pada %s, terjadi kenaikan volume kendaraan sebesar %d persen dibandingkan lalu lintas normal." % (model_camera["street_name"], volume_data["percentage"]))
                    elif (volume_data["percentage"] == 0) :
                        sentence = ("Pada %s, volume lalu lintas terpantau normal.")
                    else:
                        sentence = ("Pada %s, terjadi penurunan volume kendaraan sebesar %d persen dibandingkan lalu lintas normal." % (model_camera["street_name"], volume_data["percentage"]))
            
            elif density_data["density"] != "timeout" and volume_data["percentage"] == "timeout":
                if "hujan" in current_weather.lower():
                    sentence = ("Hujan mengguyur %s. Arus lalu lintas terpantau %s." % (model_camera["street_name"], density_data["density"].lower() ))
                else:
                 sentence = ("%s terpantau %s." % (model_camera["street_name"], density_data["density"].lower() ))
            
            elif density_data["density"] != "timeout" and volume_data["percentage"] != "timeout":
                #########
                if "hujan" in current_weather.lower():
                    sentence = ("Hujan mengguyur %s. Arus lalu lintas terpantau %s." % (model_camera["street_name"], density_data["density"].lower() ))
                else:
                    sentence = ("%s terpantau %s." % (model_camera["street_name"], density_data["density"].lower() ))
                ########
                if (volume_data["percentage"] > 0) :
                    sentence = sentence + (" Terjadi kenaikan volume kendaraan sebesar %d persen dibandingkan lalu lintas normal." % (volume_data["percentage"]))
                elif (volume_data["percentage"] == 0) :
                    sentence = sentence + (" Volume lalu lintas normal.")
                else:
                    sentence = sentence + (" Terjadi penurunan volume kendaraan sebesar %d persen dibandingkan lalu lintas normal." % (volume_data["percentage"]))
            else:
                sentence = ("%s." % (model_camera["street_name"]))

            yield semanticContract_pb2.HelloReply(response="%s" % sentence)


class Server(threading.Thread):
    def __init__(self, threadName):
        threading.Thread.__init__(self)
        self.threadName = threadName

    def run(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=20))
        semanticContract_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)

        server.add_insecure_port("[::]:50049")
        server.start()

        print("server listening on port 50049")
              
        try:
            while True:
                time.sleep(_ONE_DAY_IN_SECONDS)
        except KeyboardInterrupt:
            server.stop(0)
