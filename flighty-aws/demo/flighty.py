
import copy
import json
import os
import random
import sys
import time

current_directory = os.path.abspath(os.path.dirname(__file__))
parent_directory = os.path.abspath(os.path.dirname(current_directory))
sys.path.insert(0, parent_directory)
sys.path.insert(0, current_directory)

from os.path import exists
from handler1 import handler as handler1
from handler2 import handler as handler2
from handler3.densenet_onnx import handler as handler3
from handler4 import handler as handler4
from snowflake_log import log_to_snowflake


class Flighty():
  endpoints = {}
  cache = {}
  artifacts = {}
  cache_enabled = False
  def __init__(self, ):
    pass

  @classmethod
  def initialize(cls, docker_wait=25, deploy_wait=14, traffic_wait=5, name='cerebral'):
    cls.base_url = f'https://flighty.ai/{name}'
    cls.docker_wait = docker_wait
    cls.deploy_wait = deploy_wait
    cls.traffic_wait = traffic_wait
    cls.wait_for(1)
    return (f'Successfully initiated connection with organization {name}, base URL {cls.base_url}')

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
  def create_handler(cls, endpoint, name, folder_path='./handler1', 
    docker_image='701906161514.dkr.ecr.us-west-1.amazonaws.com/flighty-repository:1', artifacts=[]):
    # We assume there exists a file called 'handler.py' in the folder pointed at by 'folder_path'
    if not cls.endpoint_exists(endpoint):
      return ''

    if not exists(folder_path):
      print(f'Handler at path {folder_path} not found. Please check the path and try again.')
      return ''

    if name in cls.endpoints[endpoint].keys():
      print(f'Handler with name {name} already exists behind endpoint {endpoint}. '
        'Please select a different name or delete the existing handler before continuing.')
      return ''

    if folder_path == './handler1':
      handler = handler1
    elif folder_path == './handler2':
      handler = handler2
    elif folder_path == './handler3':
      handler = handler3
    elif folder_path == './handler4':
      handler = handler4
    handler = handler.Handler()

    # create cache entry to avoid key errors in invoke()
    cls.cache[name] = {}
    cls.wait_for(1, f'Found handler at {folder_path}')
    cls.wait_for(cls.docker_wait, f'Using specified Docker image at {docker_image}')
    cls.wait_for(cls.deploy_wait, f'Deploying handler {name} behind endpoint {endpoint}')

    # Serve 100% of prod traffic with this handler, if it's the first handler behind the endpoint
    if len(cls.endpoints[endpoint]) == 0:
      cls.wait_for(cls.traffic_wait, f'Updating endpoint to serve 100% of traffic with handler {name}')
      cls.endpoints[endpoint][name] = {'pyobj': handler, 'prod': 100, 'shadow': 0}
    else:
      cls.endpoints[endpoint][name] = {'pyobj': handler, 'prod': 0, 'shadow': 0}
    return (f'Successfully deployed handler {name}. To invoke this handler directly, '
      f'call {cls.base_url}/{endpoint}/{name}')

  @classmethod
  def update_endpoint(cls, endpoint, traffic):
    if not cls.endpoint_exists(endpoint):
      return ''
    
    for name in traffic.keys():
      if name not in cls.endpoints[endpoint].keys():
        print(f'You tried to adjust traffic for handler name {name}, which does not exist'
          f'behind endpoint {endpoint}. Please create the handler first with create_handler')

 
    handlers_not_yet_seen = set(cls.endpoints[endpoint].keys())
    new_traffic = copy.deepcopy(cls.endpoints[endpoint])
    sum_check = 0
    for handler, traffic_split in traffic.items():
      try:
        prod = traffic_split["prod"]
        shadow = traffic_split["shadow"]
        new_traffic[handler]["prod"] = prod
        new_traffic[handler]["shadow"] = shadow
        if prod < 0 or shadow < 0:
          print(f'You entered in a negative traffic value for either prod or shadow for handler {handler}. '
          'Please enter a positive value and try again.')
          return ''
        if shadow > 100:
          print(f'You entered a value of {shadow} for shadow traffic to handler {handler}.'
          'Please enter a value less than 100 and try again.')
          return ''
        sum_check += prod
        handlers_not_yet_seen.remove(handler)
      except KeyError:
        print(f'We were unable to parse your traffic update. '
          'For each handler, please pass a dictionary with both \"prod\" and \"shadow\" as keys')
        return ''
      
    if len(handlers_not_yet_seen):
        print(f'When trying to update traffic, we saw no values passed for the following handlers: {handlers_not_yet_seen}'
          'Please pass prod and shadow traffic values for all handlers')
        return ''

    if (abs(sum_check-100.) > 0.0001):
      print(f'You entered in a prod traffic split that sums to {sum_check}. Please enter in values that sum to 100')
      return ''
    

    cls.endpoints[endpoint] = new_traffic
    cls.wait_for(cls.traffic_wait, f'Updating traffic to endpoint {endpoint}')
    return f'Updated traffic for endpoint {endpoint} to be {traffic}'

  @classmethod
  def get_artifact_path(cls, name, version=None):
    artifact = cls.artifacts[name]
    if version is None: # assume latest
      version = max(artifact.keys())
    return artifact[version]

  @classmethod
  def upload_artifact(cls, name, folder_path=None, version=None):
    if not exists(folder_path):
      raise FileNotFoundError(f'Artifact at path {folder_path} not found. Please check the path and try again')
    
    folder_path = os.path.abspath(folder_path)

    try:
      artifact = cls.artifacts[name]
      latest_version = max(artifact.keys())
      if version is None:
        version = latest_version + 1 # no version supplied, auto-increment
    except KeyError: # artifact does not exist, need to create a new one
      if version and version > 0:
        raise NameError(f'Artifact {name} not found. To create a new artifact with this name, leave version empty or pass in a value of 0')
      else:
        cls.artifacts[name] = artifact = {0: None}
        version = 0
    
    if version in artifact.keys() or version - 1 in artifact.keys():
      artifact[version] = folder_path
    else:
      raise KeyError(f'You specified version {version} for artifact {name} but latest version was {latest_version}. '
      f'Specify a version no larger than the {latest_version + 1} and try again.')
      
    print(f'Successfully created artifact with version {version} and name {name} from path {folder_path}')
    

  @classmethod
  def invoke(cls, endpoint='doc_rec', handler=None, data=None):
    t1 = time.time()
    cache_hit = False
    if handler:
      cls.wait_for(1, f'Invoking handler {handler} behind endpoint {endpoint}')
      if cls.cache_enabled:
        try:
          output = cls.cache[handler][json.dumps(data)]
          cache_hit = True
        except KeyError:
          pass
      if not(cache_hit):
        output = cls.endpoints[endpoint][handler]['pyobj'].predict(data)
      log_to_snowflake(data, False, endpoint, handler, output, time.time()-t1)
    else:
      cls.wait_for(1, f'Invoking endpoint {endpoint}')
      traffic_number = random.randint(0, 99)
      current_sum = 0
      for name, details in cls.endpoints[endpoint].items():
        if details["prod"] > 0:
          current_sum += details["prod"]
          if current_sum > traffic_number: # do our prod traffic split
            
            if cls.cache_enabled:
              try:
                output = cls.cache[name][json.dumps(data)]
                cache_hit = True
              except KeyError:
                pass
            if not(cache_hit):
              output = cls.endpoints[endpoint][name]['pyobj'].predict(data)
            log_to_snowflake(data, True, endpoint, name, output, time.time()-t1)
        if details["shadow"] > traffic_number: # replicate to shadow if necessary
          shadow_out = cls.endpoints[endpoint][name]['pyobj'].predict(data, type="shadow")
          log_to_snowflake(data, False, endpoint, name, shadow_out, time.time()-t1)

    if cls.cache_enabled:
      cache_key = json.dumps(data)
      cls.cache[handler][cache_key] = output
    return output

  @classmethod
  def enable_caching(cls, endpoint, ttl):
    cls.cache_enabled = True

  @classmethod
  def show_endpoints(cls):
    for endpoint in cls.endpoints:
      print(f'Endpoint: {endpoint}')
      for handler in cls.endpoints[endpoint]:
        print(f"Handler {handler}, prod traffic {cls.endpoints[endpoint][handler]['prod']}, "
          f"shadow traffic {cls.endpoints[endpoint][handler]['shadow']}")

  @classmethod
  def wait_for(cls, n, status_message='Working'):
    print(status_message, end='')
    for i in range(n):
      print('.', end='')
      sys.stdout.flush()
      time.sleep(0.3)
  
      
    print('')
