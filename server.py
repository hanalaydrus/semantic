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
        if request.id == 0:
            model = Model()
            model_camera = model.request_data_all()
            exit = False

            weather_queue = [multiprocessing.Queue(1) for x in range(0,len(model_camera))]
            client_weather = [Weather("client_weather", model_camera[x]["latitude"], model_camera[x]["longitude"], weather_queue[x]) for x in range(0,len(model_camera))]

            density_queue = [multiprocessing.Queue(1) for x in range(0,len(model_camera))]
            client_density = [ClientDensity(x+1, "density-service:50050", "client_density", density_queue[x]) for x in range(0,len(model_camera))]
            
            volume_queue = [multiprocessing.Queue(1) for x in range(0,len(model_camera))]
            client_volume = [ClientVolume(x+1, "volume-service:50051", "client_volume", volume_queue[x]) for x in range(0,len(model_camera))]

            # create thread density, volume, weather for all id
            for x in range(0,len(model_camera)):
                client_weather[x].start()
                client_density[x].start()
                client_volume[x].start()

            # join all client thread
            def join_thread():
                exit = True
                for x in range(0,len(model_camera)):
                    client_weather[x].stop()
                    client_density[x].stop()
                    client_volume[x].stop()

                    client_weather[x].join()
                    client_density[x].join()
                    client_volume[x].join()

                myLock.acquire(True)
                print("finish-thread, active: %d" % (threading.active_count()))
                # print(threading.enumerate())
                # print("finish akhir")
                myLock.release()

            context.add_callback(join_thread)
            # yield traffic city
            while not exit:
                sentence = ""

                weather_data = 0
                for queue_data in weather_queue:
                    weather_data_q = queue_data.get()
                    if "hujan" in weather_data_q["weather"].lower():
                        weather_data= weather_data + 1

                density_data = {"lancar" : 0, "ramai_lancar": 0, "padat": 0}
                for queue_data in density_queue:
                    density_data_q = queue_data.get()
                    if density_data_q["density"] != None:
                        if "lancar" in density_data_q["density"].lower():
                            density_data["lancar"] = density_data["lancar"] + 1
                        elif "ramai" in density_data_q["density"].lower():
                            density_data["ramai_lancar"] = density_data["ramai_lancar"] + 1
                        elif "padat" in density_data_q["density"].lower():
                            density_data["padat"] = density_data["ramai_lancar"] + 1


                volume_data = {"normal" : 0, "naik": 0, "turun": 0}
                for queue_data in volume_queue:
                    volume_data_q = queue_data.get()
                    if volume_data_q["percentage"] != None:
                        if volume_data_q["percentage"] == 0:
                            volume_data["naik"] = volume_data["naik"] + 1
                        elif volume_data_q["percentage"] > 0:
                            volume_data["normal"] = volume_data["normal"] + 1
                        elif volume_data_q["percentage"] < 0:
                            volume_data["turun"] = volume_data["turun"] + 1

                if weather_data == len(model_camera):
                    sentence = "Hujan mengguyur Kota Bandung."
                elif weather_data >= len(model_camera)/2 and weather_data < len(model_camera):
                    sentence = "Hujan mengguyur sebagian besar ruas jalan Kota Bandung."
                elif weather_data < len(model_camera)/2:
                    sentence = "Hujan mengguyur sebagian kecil ruas jalan Kota Bandung."

                if density_data["lancar"] == 0 and density_data["ramai_lancar"] == 0 and density_data["padat"] == 0:
                    print("density none")
                else:
                    if density_data["lancar"] == len(model_camera):
                        sentence = sentence + " Arus lalu lintas Kota Bandung terpantau lancar."
                    elif density_data["ramai_lancar"] == len(model_camera):
                        sentence = sentence + " Arus lalu lintas Kota Bandung terpantau ramai lancar."
                    elif density_data["padat"] == len(model_camera):
                        sentence = sentence + "Arus lalu lintas Kota Bandung terpantau ramai padat."
                    else:
                        if density_data["lancar"] < len(model_camera) or density_data["lancar"] > len(model_camera)/2:
                            sentence = sentence + " Arus lalu lintas Kota Bandung cenderung lancar."
                        elif density_data["ramai_lancar"] < len(model_camera) and density_data["ramai_lancar"] > len(model_camera)/2:
                            sentence = sentence + " Arus lalu lintas Kota Bandung cenderung ramai lancar."
                        elif density_data["padat"] < len(model_camera) or density_data["padat"] > len(model_camera)/2:
                            sentence = sentence + " Arus lalu lintas Kota Bandung cenderung ramai padat."
                        else:
                            sentence = sentence + " Arus lalu lintas Kota Bandung cenderung ramai lancar."
                    

                if volume_data["normal"] == 0 and volume_data["naik"] == 0 and volume_data["turun"] == 0:
                    print("volume none")
                else:
                    if volume_data["normal"] == len(model_camera):
                        sentence = sentence + " Volume kendaraan normal."
                    elif volume_data["naik"] == len(model_camera):
                        sentence = sentence + " Terjadi peningkatan volume kendaraan dibandingkan lalu lintas normal"
                    elif volume_data["turun"] == len(model_camera):
                        sentence = sentence + " Terjadi penurunan volume kendaraan dibandingkan lalu lintas normal."
                    else:
                        if volume_data["normal"] < len(model_camera) or volume_data["normal"] > len(model_camera)/2:
                            sentence = sentence + " Volume kendaraan cenderung normal."
                        elif volume_data["naik"] < len(model_camera) and volume_data["naik"] > len(model_camera)/2:
                            sentence = sentence + " Volume kendaraan cenderung meningkat."
                        elif volume_data["turun"] < len(model_camera) or volume_data["turun"] > len(model_camera)/2:
                            sentence = sentence + " Volume kendaraan cenderung menurun."
                        else:
                            sentence = sentence + " Volume kendaraan cenderung normal."
                    

                yield semanticContract_pb2.HelloReply(response="%s" % sentence)

        else:
        # model get camera data
            model = Model()
            model_camera = model.request_data(request.id)
            exit = False

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
                exit = True
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
            
            while not exit:
                density_data = density_queue.get()
                volume_data = volume_queue.get()
                weather_data = weather_queue.get()

                current_weather = weather_data["weather"]

                if density_data["density"] == None and volume_data["percentage"] != None:
                    if "hujan" in current_weather.lower():
                        if (volume_data["percentage"] > 0) :
                            sentence = ("Hujan mengguyur %s. Terjadi peningkatan volume kendaraan sebesar %d persen dibandingkan lalu lintas normal." % (model_camera["street_name"], volume_data["percentage"]))
                        elif (volume_data["percentage"] == 0) :
                            sentence = ("Hujan mengguyur %s. volume lalu lintas terpantau normal.")
                        else:
                            sentence = ("Hujan mengguyur %s. Terjadi penurunan volume kendaraan sebesar %d persen dibandingkan lalu lintas normal." % (model_camera["street_name"], volume_data["percentage"]))
                    else:
                        if (volume_data["percentage"] > 0) :
                            sentence = ("Pada %s, terjadi peningkatan volume kendaraan sebesar %d persen dibandingkan lalu lintas normal." % (model_camera["street_name"], volume_data["percentage"]))
                        elif (volume_data["percentage"] == 0) :
                            sentence = ("Pada %s, volume lalu lintas terpantau normal.")
                        else:
                            sentence = ("Pada %s, terjadi penurunan volume kendaraan sebesar %d persen dibandingkan lalu lintas normal." % (model_camera["street_name"], volume_data["percentage"]))
                
                elif density_data["density"] != None and volume_data["percentage"] == None:
                    if "hujan" in current_weather.lower():
                        sentence = ("Hujan mengguyur %s. Arus lalu lintas terpantau %s." % (model_camera["street_name"], density_data["density"].lower() ))
                    else:
                     sentence = ("%s terpantau %s." % (model_camera["street_name"], density_data["density"].lower() ))
                
                elif density_data["density"] != None and volume_data["percentage"] != None:
                    #########
                    if "hujan" in current_weather.lower():
                        sentence = ("Hujan mengguyur %s. Arus lalu lintas terpantau %s." % (model_camera["street_name"], density_data["density"].lower() ))
                    else:
                        sentence = ("%s terpantau %s." % (model_camera["street_name"], density_data["density"].lower() ))
                    ########
                    if (volume_data["percentage"] > 0) :
                        sentence = sentence + (" Terjadi peningkatan volume kendaraan sebesar %d persen dibandingkan lalu lintas normal." % (volume_data["percentage"]))
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
