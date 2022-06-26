
import copy
import json
from locale import currency
import os
import random
import sys
import time

current_directory = os.path.abspath(os.path.dirname(__file__))
parent_directory = os.path.abspath(os.path.dirname(current_directory))
print(current_directory, parent_directory)
sys.path.insert(0, parent_directory)
sys.path.insert(0, current_directory)

from os.path import exists
from model1 import model as model1
from model2 import model as model2
from model3.densenet_onnx import model as model3
from model4 import model as model4
from snowflake_log import log_to_snowflake


class Flighty():
  endpoints = {}
  def __init__(self, docker_wait=25, deploy_wait=14, traffic_wait=5):
    with open('config.txt') as f:
      for line in f.readlines():
        parsed = line.split(' = ')
        if (parsed[0] == 'ORGANIZATION'):
          Flighty.organization_name = parsed[1].rstrip().lower()

    Flighty.base_url = f'https://flighty.ai/{Flighty.organization_name}'
    Flighty.docker_wait = docker_wait
    Flighty.deploy_wait = deploy_wait
    Flighty.traffic_wait = traffic_wait
    
  @classmethod
  def initialize(cls):
    cls.wait_for(1)
    return (f'Successfully initiated connection with organization {cls.organization_name}, base URL {cls.base_url}')

  @classmethod
  def endpoint_exists(cls, name):
    if name not in cls.endpoints.keys():
      print(f'Endpoint {name} does not exist. Please create the endpoint first by calling create_endpoint()')
      return False
    return True

  @classmethod
  def create_endpoint(cls, name):
    if name in cls.endpoints.keys():
        print(f'Endpoint with name {name} already exists. Please delete that endpoint or choose a different name')
        return ''
    cls.endpoints[name] = {}

    cls.wait_for(3)
    return (f'Successfully created endpoint with URL {cls.base_url}/{name}')


  @classmethod
  def create_model(cls, endpoint, model_name, model_path='./model1'):
    if not cls.endpoint_exists(endpoint):
      return ''

    if not exists(model_path):
      print(f'Model at path {model_path} not found. Please check the path and try again.')
      return ''

    if model_name in cls.endpoints[endpoint].keys():
      print(f'Model with name {model_name} already exists behind endpoint {endpoint}. '
        'Please select a different name or delete the existing model before continuing.')
      return ''

    if model_path == 'model1':
      model = model1
    elif model_path == 'model2':
      model = model2
    elif model_path == 'model3':
      model = model3
    elif model_path == 'model4':
      model = model4
    # elif model_path == 'model4':
    #   model = model4
    if model_path != 'model4':
      model = model.Model()
    else:
      pass
    cls.wait_for(1, f'Found model at {model_path}')
    cls.wait_for(cls.docker_wait, f'Creating Docker image for model {model_name}')
    cls.wait_for(cls.deploy_wait, f'Deploying model {model_name} behind endpoint {endpoint}')
    if len(cls.endpoints[endpoint]) == 0:
      cls.wait_for(cls.traffic_wait, f'Updating endpoint to serve 100% of traffic with model {model_name}')
      cls.endpoints[endpoint][model_name] = {'pyobj': model, 'prod': 100, 'shadow': 0}
    else:
      cls.endpoints[endpoint][model_name] = {'pyobj': model, 'prod': 0, 'shadow': 0}
    return (f'Successfully deployed model {model_name}. To invoke this model directly, '
      f'call {cls.base_url}/{endpoint}/{model_name}')


  def update_endpoint(cls, endpoint, traffic):
    if not cls.endpoint_exists(endpoint):
      return ''
    
    for model_name in traffic.keys():
      if model_name not in cls.endpoints[endpoint].keys():
        print(f'You tried to adjust traffic for model name {model_name}, which does not exist'
          f'behind endpoint {endpoint}. Please create the model first with create_model')

 
    models_not_yet_seen = set(cls.endpoints[endpoint].keys())
    new_traffic = copy.deepcopy(cls.endpoints[endpoint])
    for model, traffic_split in traffic.items():
      sum_check = 0
      try:
        prod = traffic_split["prod"]
        shadow = traffic_split["shadow"]
        new_traffic[model]["prod"] = prod
        new_traffic[model]["shadow"] = shadow
        if prod < 0 or shadow < 0:
          print(f'You entered in a negative traffic value for either prod or shadow for model {model}. '
          'Please enter a positive value and try again.')
          return ''
        if shadow > 100:
          print(f'You entered a value of {shadow} for shadow traffic to model {model}.'
          'Please enter a value less than 100 and try again.')
          return ''
        sum_check += prod
        models_not_yet_seen.remove(model)
      except KeyError:
        print(f'We were unable to parse your traffic update. '
          'For each model, please pass a dictionary with both \"prod\" and \"shadow\" as keys')
        return ''
      
    if len(models_not_yet_seen):
        print(f'When trying to update traffic, we saw no values passed for the following models: {models_not_yet_seen}'
          'Please pass prod and shadow traffic values for all models')
        return ''

    if (abs(sum_check-100.) > 0.0001):
      print(f'You entered in a prod traffic split that sums to {sum_check}. Please enter in values that sum to 100')
      return ''
    

    cls.endpoints[endpoint] = new_traffic
    cls.wait_for(cls.traffic_wait, f'Updating traffic to endpoint {endpoint}')
    return f'Updated traffic for endpoint {endpoint} to be {cls.pretty_print_json(traffic)}'

  @classmethod
  def invoke(cls, endpoint='doc_rec', model=None, data=None):
    if model:
      cls.wait_for(1, f'Invoking model {model} behind endpoint {endpoint}')
      output = cls.endpoints[endpoint][model]['pyobj'].predict(data)
      log_to_snowflake(data, False, endpoint, model, output)
    else:
      cls.wait_for(1, f'Invoking endpoint {endpoint}')
      traffic_number = random.randint(0, 99)
      current_sum = 0
      for model_name, details in cls.endpoints[endpoint].items():
        if details["prod"] > 0:
          current_sum += details["prod"]
          if current_sum > traffic_number: # do our prod traffic split
            output = cls.endpoints[endpoint][model_name]['pyobj'].predict(data)
            log_to_snowflake(data, True, endpoint, model_name, output)
          if details["shadow"] > traffic_number: # replicate to shadow if necessary
            shadow_out = cls.endpoints[endpoint][model_name]['pyobj'].predict(data, type="shadow")
            log_to_snowflake(data, False, endpoint, model_name, shadow_out)
    return cls.pretty_print_json(output)

  def show_endpoints(cls):
    return cls.pretty_print_json(cls.endpoints)

  def pretty_print_json(input):
    return json.dumps(input, indent=4, sort_keys=True)

  @classmethod
  def wait_for(cls, n, status_message='Working'):
    print(status_message, end='')
    for i in range(n):
      print('.', end='')
      sys.stdout.flush()
      time.sleep(0.3)
  
      
    print('')
print('about to invoke flighty')

f = Flighty(docker_wait=1, deploy_wait=1, traffic_wait=1)

def initialize():
  print(f.initialize())

def create_endpoint(name):
  print(f.create_endpoint(name))

def create_model(endpoint, model_name, model_path):
  print(f.create_model(endpoint, model_name, model_path))

def invoke(endpoint=None, model=None, data=None):
  print(f.invoke(endpoint, model, data))

def update_endpoint(endpoint, traffic):
  traffic =  json.loads(traffic)
  print(f.update_endpoint(endpoint, traffic))

def show_endpoints():
  print(f.show_endpoints())
  
def demo_setup():
  initialize()
  create_endpoint('doc_rec')
  create_model('doc_rec', 'rules', 'model1')
  create_model('doc_rec', 'xgboost', 'model2')
  update_endpoint('doc_rec', traffic=json.dumps({'rules': {'prod': 100, 'shadow': 0}, 'xgboost': {'prod': 0, 'shadow': 100}}))


  # test shadow traffic logic
  invoke('doc_rec', None, {'Survey_responses': {1: 'I am looking for help'}})

  # Test GPU model alone
  create_model('doc_rec', 'gpu_featurizer', 'model3')
  invoke('doc_rec', 'gpu_featurizer', {'Survey_responses': {1: 'I am looking for help'}})

  # Add in CPU model that invokes GPU model
  create_model('doc_rec', 'hybrid_cpu_gpu', 'model4')
  invoke('doc_rec', 'hybrid_cpu_gpu', {'Survey_responses': {1: 'I am looking for help'}})

# def create_endpoint()

if (__name__ == '__main__'):
  demo_setup()