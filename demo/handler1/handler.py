import os
import pathlib
import random
import sys

parent_directory = os.path.abspath(pathlib.Path('./..'))
sys.path.insert(0, parent_directory)

class Handler():
  def __init__(self):
    from flighty import Flighty
    name = 'rules'
    artifact_path = Flighty.get_artifact_path(name=name)
    print(f'Got artifact {name} from path {artifact_path}')

  def predict(data, type="prod"):
    test = list(range(0,50))
    random.shuffle(test)
    output = {'physician_preference': test[:10]}
  
    return output