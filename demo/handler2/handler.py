import os
import pathlib
import random
import sys

parent_directory = os.path.abspath(pathlib.Path('./..'))
sys.path.insert(0, parent_directory)

class Handler():
  def __init__(self):
    from flighty import Flighty
    artifact = 'xgboost'
    artifact_path = Flighty.get_artifact_path(name=artifact)
    print(f'Got path {artifact_path} for artifact {artifact}')

  def predict(self, data, type="prod"):
    test = list(range(0,50))
    random.shuffle(test)
    output = {'physician_preference': test[:10]}
    return output