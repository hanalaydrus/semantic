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
from Queue import LifoQueue, Full
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
    self.response = None

  def run(self):
    if exitFlag:
      self.threadName.exit()
    #Create connection
    channel = grpc.insecure_channel(self.ipaddress)
    while True:
      # try:
      #   self.queue.put_nowait({'density': "Lancar"})
      # except Full:
      #   # print('dropped density')
      #   continue
      try:
        grpc.channel_ready_future(channel).result(timeout=5)
      except grpc.FutureTimeoutError:
        self.queue.put({'density': 'timeout'})
        self.response = None
      else:
        stub = densityContract_pb2_grpc.GreeterStub(channel)
        response = stub.SayHello(densityContract_pb2.HelloRequest(id=self.camera_id))
        self.response = response
        try:
          for resp in self.response:
            try:
              self.queue.put_nowait({'density': resp.response})
            except Full:
              continue
        except grpc.RpcError as e:
          if e.code() == grpc.StatusCode.CANCELLED:
            print('cancelled')
            break
          elif e.code() == grpc.StatusCode.UNAVAILABLE:
            print('unavailable')
            continue
  
  def stop(self):
    if self.response != None:
      self.response.cancel()

class ClientVolume(threading.Thread):
  def __init__(self, camera_id, ipaddress, threadName, queue=None):
    threading.Thread.__init__(self)
    self.ipaddress = ipaddress
    self.camera_id = camera_id
    self.threadName = threadName
    self.queue = queue
    self.response = None

  def run(self):
    if exitFlag:
      self.threadName.exit()
    #Create connection
    channel = grpc.insecure_channel(self.ipaddress)
    while True:
      # try:
      #   self.queue.put_nowait({'volume': 0, 'percentage': 10})
      # except Full:
      #   # print('dropped volume')
      #   continue
      try:
        grpc.channel_ready_future(channel).result(timeout=5)
      except grpc.FutureTimeoutError:
        self.queue.put({'percentage': 'timeout'})
        self.response = None
      else:
        stub = volumeContract_pb2_grpc.GreeterStub(channel)
        response = stub.SayHello(volumeContract_pb2.HelloRequest(id=self.camera_id))
        self.response = response
        try:
          for resp in self.response:
            try:
              self.queue.put({'volume': resp.volume, 'percentage': resp.percentage})
            except Full:
              continue
        except grpc.RpcError as e:
          if e.code() == grpc.StatusCode.CANCELLED:
            print('cancelled')
            break
          elif e.code() == grpc.StatusCode.UNAVAILABLE:
            print('unavailable')
            continue

  def stop(self):
    if self.response != None:
      self.response.cancel()
