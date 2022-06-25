
import json
import sys
import time

class Flighty():
  def __init__(self):
    self.base_url = 'https://flighty.ai'
    pass
  def create_organization(self, name):
    self.organization_name = name
    output = {'status': "Success", 'name': f'{name}', 'base_url': f'{self.base_url}/{name}'}
    self.wait_for(3)
    return json.dumps(output)
  def create(self, name):
    output = {'name': f'https://'}


  def wait_for(self, n):
    print('Working', end='')
    for i in range(n):
      print('.', end='')
      sys.stdout.flush()
      time.sleep(0.3)
  
      
    print('')