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
myLock = threading.Lock()

class Greeter(semanticContract_pb2_grpc.GreeterServicer):

    def SayHello(self, request, context):
        # while True:
        #     def join_thread():
        #         myLock.acquire(True)
        #         print("finish-thread active: %d" % (threading.active_count()))
        #         print(threading.enumerate())
        #         myLock.release()

        #     context.add_callback(join_thread)

        #     yield semanticContract_pb2.HelloReply(response='Hello')
        # model get camera data
        model = Model()
        model_camera = model.request_data(request.id)

        # thread client density
        density_data = {'density' : 'timeout'}
        client_density = ClientDensity(request.id, "density-service:50050", "client_density", density_data)
        client_density.start()

        # thread client volume
        volume_data = {'volume': 'timeout', 'percentage': 'timeout'}
        client_volume = ClientVolume(request.id, "volume-service:50051", "client_volume", volume_data)
        client_volume.start()

        # thread client volume
        weather_data = {'weather' : 'unavailable'}
        client_weather = Weather("client_weather", model_camera['latitude'], model_camera['longitude'], weather_data)
        client_weather.start()

        myLock.acquire(True)
        print("start-thread active: %d" % (threading.active_count()))
        print(threading.enumerate())
        myLock.release()

        def join_thread():
            client_density.stop()
            client_volume.stop()
            client_weather.stop()
            
            client_density.join()
            client_volume.join()
            client_weather.join()

            myLock.acquire(True)
            print("finish-thread active: %d" % (threading.active_count()))
            # print(threading.enumerate())
            myLock.release()

        context.add_callback(join_thread)
        
        while True:
            current_weather = weather_data['weather']

            if density_data['density'] == 'timeout' and volume_data['percentage'] != 'timeout':
                if "hujan" in current_weather.lower():
                    if (volume_data['percentage'] > 0) :
                        sentence = ("Hujan mengguyur %s. Terjadi kenaikan volume kendaraan sebesar %d persen dibandingkan lalu lintas normal." % (model_camera['street_name'], volume_data['percentage']))
                    elif (volume_data['percentage'] == 0) :
                        sentence = ("Hujan mengguyur %s. volume lalu lintas terpantau normal.")
                    else:
                        sentence = ("Hujan mengguyur %s. terjadi penurunan volume kendaraan sebesar %d persen dibandingkan lalu lintas normal." % (model_camera['street_name'], volume_data['percentage']))
                else:
                    if (volume_data['percentage'] > 0) :
                        sentence = ("Pada %s, terjadi kenaikan volume kendaraan sebesar %d persen dibandingkan lalu lintas normal." % (model_camera['street_name'], volume_data['percentage']))
                    elif (volume_data['percentage'] == 0) :
                        sentence = ("Pada %s, volume lalu lintas terpantau normal.")
                    else:
                        sentence = ("Pada %s, terjadi penurunan volume kendaraan sebesar %d persen dibandingkan lalu lintas normal." % (model_camera['street_name'], volume_data['percentage']))
            
            elif density_data['density'] != 'timeout' and volume_data['percentage'] == 'timeout':
                if "hujan" in current_weather.lower():
                    sentence = ("Hujan mengguyur %s. Arus lalu lintas terpantau %s." % (model_camera['street_name'], density_data['density'].lower() ))
                else:
                 sentence = ("%s terpantau %s." % (model_camera['street_name'], density_data['density'].lower() ))
            
            else:
                #########
                if "hujan" in current_weather.lower():
                    sentence = ("Hujan mengguyur %s. Arus lalu lintas terpantau %s." % (model_camera['street_name'], density_data['density'].lower() ))
                else:
                    sentence = ("%s terpantau %s." % (model_camera['street_name'], density_data['density'].lower() ))
                ########
                if (volume_data['percentage'] > 0) :
                    sentence = sentence + ("Terjadi kenaikan volume kendaraan sebesar %d persen dibandingkan lalu lintas normal." % (volume_data['percentage']))
                elif (volume_data['percentage'] == 0) :
                    sentence = sentence + ("Volume lalu lintas normal.")
                else:
                    sentence = sentence + ("Terjadi penurunan volume kendaraan sebesar %d persen dibandingkan lalu lintas normal." % (volume_data['percentage']))
            
            yield semanticContract_pb2.HelloReply(response='%s' % sentence)


class Server(threading.Thread):
    def __init__(self, threadName):
        threading.Thread.__init__(self)
        self.threadName = threadName

    def run(self):
        executor = futures.ThreadPoolExecutor(max_workers=10)
        server = grpc.server(executor)
        semanticContract_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)

        server.add_insecure_port('[::]:50049')
        server.start()

        print("server listening on port 50049")
              
        try:
            while True:
                time.sleep(_ONE_DAY_IN_SECONDS)
        except KeyboardInterrupt:
            server.stop(0)
