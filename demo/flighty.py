
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
  cache = {}
  cache_enabled = False
  def __init__(self, ):
    pass

  @classmethod
  def initialize(cls, docker_wait=25, deploy_wait=14, traffic_wait=5):
    this_directory = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(this_directory, 'config.txt')) as f:
      for line in f.readlines():
        parsed = line.split(' = ')
        if (parsed[0] == 'ORGANIZATION'):
          cls.organization_name = parsed[1].rstrip().lower()

    cls.base_url = f'https://flighty.ai/{cls.organization_name}'
    cls.docker_wait = docker_wait
    cls.deploy_wait = deploy_wait
    cls.traffic_wait = traffic_wait
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
    model = model.Model()

    # create cache entry to avoid key errors in invoke()
    cls.cache[model_name] = {}
    cls.wait_for(1, f'Found model at {model_path}')
    cls.wait_for(cls.docker_wait, f'Creating Docker image for model {model_name}')
    cls.wait_for(cls.deploy_wait, f'Deploying model {model_name} behind endpoint {endpoint}')

    # Serve 100% of prod traffic with this model, if it's the first model behind the endpoint
    if len(cls.endpoints[endpoint]) == 0:
      cls.wait_for(cls.traffic_wait, f'Updating endpoint to serve 100% of traffic with model {model_name}')
      cls.endpoints[endpoint][model_name] = {'pyobj': model, 'prod': 100, 'shadow': 0}
    else:
      cls.endpoints[endpoint][model_name] = {'pyobj': model, 'prod': 0, 'shadow': 0}
    return (f'Successfully deployed model {model_name}. To invoke this model directly, '
      f'call {cls.base_url}/{endpoint}/{model_name}')

  @classmethod
  def update_endpoint(cls, endpoint, traffic):
    if not cls.endpoint_exists(endpoint):
      return ''
    
    for model_name in traffic.keys():
      if model_name not in cls.endpoints[endpoint].keys():
        print(f'You tried to adjust traffic for model name {model_name}, which does not exist'
          f'behind endpoint {endpoint}. Please create the model first with create_model')

 
    models_not_yet_seen = set(cls.endpoints[endpoint].keys())
    new_traffic = copy.deepcopy(cls.endpoints[endpoint])
    sum_check = 0
    for model, traffic_split in traffic.items():
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
    t1 = time.time()
    cache_hit = False
    if model:
      cls.wait_for(1, f'Invoking model {model} behind endpoint {endpoint}')
      if cls.cache_enabled:
        try:
          output = cls.cache[model][json.dumps(data)]
          cache_hit = True
        except KeyError:
          pass
      if not(cache_hit):
        output = cls.endpoints[endpoint][model]['pyobj'].predict(data)
      log_to_snowflake(data, False, endpoint, model, output, time.time()-t1)
    else:
      cls.wait_for(1, f'Invoking endpoint {endpoint}')
      traffic_number = random.randint(0, 99)
      current_sum = 0
      for model_name, details in cls.endpoints[endpoint].items():
        if details["prod"] > 0:
          current_sum += details["prod"]
          if current_sum > traffic_number: # do our prod traffic split
            
            if cls.cache_enabled:
              try:
                output = cls.cache[model_name][json.dumps(data)]
                cache_hit = True
              except KeyError:
                pass
            if not(cache_hit):
              output = cls.endpoints[endpoint][model_name]['pyobj'].predict(data)
            log_to_snowflake(data, True, endpoint, model_name, output, time.time()-t1)
          if details["shadow"] > traffic_number: # replicate to shadow if necessary
            shadow_out = cls.endpoints[endpoint][model_name]['pyobj'].predict(data, type="shadow")
            log_to_snowflake(data, False, endpoint, model_name, shadow_out, time.time()-t1)

    if cls.cache_enabled:
      cache_key = json.dumps(data)
      cls.cache[model][cache_key] = output
    return output

  @classmethod
  def enable_caching(cls):
    cls.cache_enabled = True

  @classmethod
  def show_endpoints(cls):
    return cls.pretty_print_json(cls.endpoints)

  @classmethod
  def pretty_print_json(cls, input):
    return json.dumps(input, indent=4, sort_keys=True)

  @classmethod
  def wait_for(cls, n, status_message='Working'):
    print(status_message, end='')
    for i in range(n):
      print('.', end='')
      sys.stdout.flush()
      time.sleep(0.3)
  
      
    print('')
