
import json
import random
import sys
import time

from os.path import exists

class Flighty():
  def __init__(self, docker_wait=25, deploy_wait=14, traffic_wait=5):
    with open('config.txt') as f:
      for line in f.readlines():
        parsed = line.split(' = ')
        if (parsed[0] == 'ORGANIZATION'):
          self.organization_name = parsed[1].rstrip().lower()
          # print(self.organization_name)
    self.base_url = f'https://flighty.ai/{self.organization_name}'
    self.endpoints = {}
    self.docker_wait = docker_wait
    self.deploy_wait = deploy_wait
    self.traffic_wait = traffic_wait
    
  def initialize(self):
    self.wait_for(1)
    return (f'Successfully initiated connection with organization {self.organization_name}, base URL {self.base_url}')

  def endpoint_exists(self, name):
    if name not in self.endpoints.keys():
      print(f'Endpoint {name} does not exist. Please create the endpoint first by calling create_endpoint()')
      return False
    return True

  def create_endpoint(self, name):
    if name in self.endpoints.keys():
        print(f'Endpoint with name {name} already exists. Please delete that endpoint or choose a different name')
        return ''
    self.endpoints[name] = {}
    #output = {'status': "Success", 'name': f'{name}', 'base_url': f'{self.base_url}/{name}'}
    self.wait_for(3)
    return (f'Successfully created endpoint with URL {self.base_url}/{name}')
    #return self.pretty_print_json(output)

  def create_model(self, endpoint, model_name, model_path='./model1'):
    if not self.endpoint_exists(endpoint):
      return ''

    if not exists(model_path):
      print(f'Model at path {model_path} not found. Please check the path and try again.')
      return ''

    if model_name in self.endpoints[endpoint].keys():
      print(f'Model with name {model_name} already exists behind endpoint {endpoint}. '
        'Please select a different name or delete the existing model before continuing.')
      return ''

    self.wait_for(1, f'Found model at {model_path}')
    self.wait_for(self.docker_wait, f'Creating Docker image for model {model_name}')
    self.wait_for(self.deploy_wait, f'Deploying model {model_name} behind endpoint {endpoint}')
    if len(self.endpoints[endpoint]) == 0:
      self.wait_for(self.traffic_wait, f'Updating endpoint to serve 100% of traffic with model {model_name}')
      self.endpoints[endpoint][model_name] = {'prod': 100, 'shadow': 0}
    else:
      self.endpoints[endpoint][model_name] = {'prod': 0, 'shadow': 0}
    return (f'Successfully deployed model {model_name}. To invoke this model directly, '
      f'call {self.base_url}/{endpoint}/{model_name}')


  def update_endpoint(self, endpoint, traffic):
    if not self.endpoint_exists(endpoint):
      return ''
    
    for model_name in traffic.keys():
      if model_name not in self.endpoints[endpoint].keys():
        print(f'You tried to adjust traffic for model name {model_name}, which does not exist'
          f'behind endpoint {endpoint}. Please create the model first with create_model')

    sum_check = 0
    models_not_yet_seen = set(self.endpoints[endpoint].keys())
    for model, traffic_split in traffic.items():
      try:
        prod = traffic_split["prod"]
        shadow = traffic_split["shadow"]
        if prod < 0 or shadow < 0:
          print(f'You entered in a negative traffic value for either prod or shadow for model {model}. '
          'Please enter a positive value and try again')
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

    if (abs(sum_check-100.) > 0.0001):
      print(f'You entered in a prod traffic split that sums to {sum_check}. Please enter in values that sum to 100')

    self.endpoints[endpoint] = traffic
    self.wait_for(self.traffic_wait, f'Updating traffic to endpoint {endpoint}')
    return f'Updated traffic for endpoint {endpoint} to be {self.pretty_print_json(traffic)}'


  
  def invoke(self, endpoint, model, data):
    test = list(range(0,50))
    random.shuffle(test)
    output = {'physician_preference': test[:10]}
    if model:
      self.wait_for(1, f'Invoking model {model} behind endpoint {endpoint}')
    else:
      self.wait_for(1, f'Invoking endpoint {endpoint}')
    return self.pretty_print_json(output)

  def show_endpoints(self):
    return self.pretty_print_json(self.endpoints)

  def pretty_print_json(self, input):
    return json.dumps(input, indent=4, sort_keys=True)

  def wait_for(self, n, status_message='Working'):
    print(status_message, end='')
    for i in range(n):
      print('.', end='')
      sys.stdout.flush()
      time.sleep(0.3)
  
      
    print('')

f = Flighty(docker_wait=1, deploy_wait=1, traffic_wait=1)

def initialize():
  print(f.initialize())

def create_endpoint(name):
  print(f.create_endpoint(name))

def create_model(endpoint, model_name, model_path):
  print(f.create_model(endpoint, model_name, model_path))

def invoke(endpoint, model=None, data=None):
  print(f.invoke(endpoint, model, data))

def update_endpoint(endpoint, traffic):
  traffic =  json.loads(traffic)
  print(f.update_endpoint(endpoint, traffic))

def show_endpoints():
  print(f.show_endpoints())
  
def demo_setup():
  global f
  #f = Flighty(docker_wait=1, deploy_wait=1, traffic_wait=1)
  initialize()
  create_endpoint('doc_rec')
  create_model('doc_rec', 'rules', 'model1')
  create_model('doc_rec', 'xgboost', 'model2')
  update_endpoint('doc_rec', traffic=json.dumps({'rules': {'prod': 100, 'shadow': 0}, 'xgboost': {'prod': 0, 'shadow': 5}}))
# def create_endpoint()

if (__name__ == '__main__'):
  demo_setup()