import os
import pathlib
import sys

parent_directory = os.path.abspath(pathlib.Path('./..'))
sys.path.insert(0, parent_directory)

class Model():
  def __init__(self):
    pass

  def predict(self, data, type="prod"):
    from flighty import Flighty
    features = Flighty.invoke(endpoint='doc_rec', model='gpu_featurizer', data=data)
    output = Flighty.invoke(endpoint='doc_rec', model='xgboost', data={"inputs": features['output']})
    return output
