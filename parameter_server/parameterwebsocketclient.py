import websocket
import json
import tensorflow as tf
import numpy as np
from tensorsparkmodel import TensorSparkModel
import download_mnist
import pickle
import math
​
class TensorSparkWorker():
   def __init__(self):
      self.model = TensorSparkModel()
      self.websock = websocket.create_connection('ws://localhost:55555')
      self.minibatch_size = 50
      self.iteration = 0
​
   def train_partition(self, partition):
      return [self.train(x) for x in partition]
​
   def train(self, data):
      print 'TensorSparkWorker().train iteration %d' % self.iteration
      if len(data) is 0:
         return 1
      accuracy = self.model.train(data)
      self.iteration += 1
​
      if self.time_to_push(self.iteration):
         self.push_gradients()
​
      if self.time_to_pull(self.iteration):
         self.request_parameters()
​
      return accuracy
​
   def test_partition(self, partition):
      return [self.test(x) for x in partition]
​
   def test(self, data):
      print 'TensorSparkWorker().test "%s"' % data
      if len(data) is 0:
         return 1.0
      self.request_parameters()
      accuracy = self.model.test(data)
      return accuracy
#      self.model.
​
   def time_to_pull(self, iteration):
      return iteration % 50 == 0 
#      return True
​
   def time_to_push(self, iteration):
      return iteration % 50 == 0
#      return True
​
   def request_parameters(self):
      request_model_message = {'type':'client_requests_parameters'}
      self.websock.send(json.dumps(request_model_message))
      print 'requesting parameters'
      parameters = pickle.loads(self.websock.recv())
      print 'received parameters'
      self.model.assign_parameters(parameters)
​
   def push_gradients(self):
      print 'pushing gradients'
      gradient = pickle.dumps(self.model.get_gradients())
      gradient_update_message = {'type':'client_gives_gradient', 'gradient':gradient}
      self.websock.send(json.dumps(gradient_update_message))
      print 'pushed gradients'
​