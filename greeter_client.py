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

import helloworld_pb2
import helloworld_pb2_grpc

exitFlag = 0

class Client(threading.Thread):
  def __init__(self, name, ipaddress, threadName, queue=None):
    threading.Thread.__init__(self)
    self.ipaddress = ipaddress
    self.name = name
    self.threadName = threadName
    self.queue = queue
  
  def run(self):
    if exitFlag:
      self.threadName.exit()
    channel = grpc.insecure_channel(self.ipaddress)
    stub = helloworld_pb2_grpc.GreeterStub(channel)
    response = stub.SayHello(helloworld_pb2.HelloRequest(name='you'))
    for resp in response:
      # print(self.name +' '+ resp.message)
      self.queue.put({'name': self.name, 'result': resp.message})
