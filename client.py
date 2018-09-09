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

import grpc
import threading
import time

import densityContract_pb2
import densityContract_pb2_grpc

import volumeContract_pb2
import volumeContract_pb2_grpc

myLock = threading.Lock()

class ClientDensity(threading.Thread):
  def __init__(self, camera_id, ipaddress, threadName, data):
    threading.Thread.__init__(self)
    self.ipaddress = ipaddress
    self.camera_id = camera_id
    self.threadName = threadName
    self.data = data
    self.response = None

  def run(self):
    #Create connection
    channel = grpc.insecure_channel(self.ipaddress)
    while True:
      try:
        grpc.channel_ready_future(channel).result(timeout=5)
      except grpc.FutureTimeoutError:
        self.response = None
        self.data['density'] = 'timeout'
      else:
        stub = densityContract_pb2_grpc.GreeterStub(channel)
        response = stub.SayHello(densityContract_pb2.HelloRequest(id=self.camera_id))
        self.response = response
        try:
          for resp in self.response:
            self.data['density'] = resp.response
        except grpc.RpcError as e:
          if e.code() == grpc.StatusCode.CANCELLED:
            myLock.acquire(True)
            print('density cancelled')
            myLock.release()
            break
          elif e.code() == grpc.StatusCode.UNAVAILABLE:
            print('density unavailable')
            continue
  
  def stop(self):
    if self.response != None:
      self.response.cancel()

class ClientVolume(threading.Thread):
  def __init__(self, camera_id, ipaddress, threadName, data):
    threading.Thread.__init__(self)
    self.ipaddress = ipaddress
    self.camera_id = camera_id
    self.threadName = threadName
    self.data = data
    self.response = None

  def run(self):
    #Create connection
    channel = grpc.insecure_channel(self.ipaddress)
    while True:
      try:
        grpc.channel_ready_future(channel).result(timeout=5)
      except grpc.FutureTimeoutError:
        self.response = None
        self.data['percentage'] = 'timeout'
      else:
        stub = volumeContract_pb2_grpc.GreeterStub(channel)
        response = stub.SayHello(volumeContract_pb2.HelloRequest(id=self.camera_id))
        self.response = response
        try:
          for resp in self.response:
            self.data['percentage'] = resp.percentage
            self.data['volume'] = resp.volume
        except grpc.RpcError as e:
          if e.code() == grpc.StatusCode.CANCELLED:
            myLock.acquire(True)
            print('volume cancelled')
            myLock.release()
            break
          elif e.code() == grpc.StatusCode.UNAVAILABLE:
            print('volume unavailable')
            continue

  def stop(self):
    if self.response != None:
      self.response.cancel()
