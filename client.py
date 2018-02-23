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

"""The Python implementation of the GRPC helloworld.Greeter client."""

from __future__ import print_function

import grpc
import threading
import time

import densityContract_pb2
import densityContract_pb2_grpc

import volumeContract_pb2
import volumeContract_pb2_grpc

exitFlag = 0

class ClientDensity(threading.Thread):
  def __init__(self, camera_id, ipaddress, threadName, queue=None):
    threading.Thread.__init__(self)
    self.ipaddress = ipaddress
    self.camera_id = camera_id
    self.threadName = threadName
    self.queue = queue
  
  def run(self):
    if exitFlag:
      self.threadName.exit()
    channel = grpc.insecure_channel(self.ipaddress)
    stub = densityContract_pb2_grpc.GreeterStub(channel)
    response = stub.SayHello(densityContract_pb2.HelloRequest(id=self.camera_id))
    for resp in response:
      # print('Density : '+ resp.response)
      self.queue.put({'density': resp.response})

class ClientVolume(threading.Thread):
  def __init__(self, camera_id, ipaddress, threadName, queue=None):
    threading.Thread.__init__(self)
    self.ipaddress = ipaddress
    self.camera_id = camera_id
    self.threadName = threadName
    self.queue = queue
  
  def run(self):
    if exitFlag:
      self.threadName.exit()
    channel = grpc.insecure_channel(self.ipaddress)
    stub = volumeContract_pb2_grpc.GreeterStub(channel)
    response = stub.SayHello(volumeContract_pb2.HelloRequest(id=self.camera_id))
    for resp in response:
      self.queue.put({'volume': resp.volume, 'percentage': resp.percentage})
