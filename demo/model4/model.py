import os
import pathlib
import random
import sys

parent_directory = os.path.abspath(pathlib.Path('./..'))
sys.path.insert(0, parent_directory)

import flighty as f

class Model():
  def __init__(self):
    pass

  def predict(self, data, type="prod"):
    features = f.invoke(endpoint='doc_rec', model='gpu_featurizer', data='lol')
    test = list(range(0,50))
    random.shuffle(test)
    output = {'physician_preference': test[:10]}
    return output

def predict(data, type="prod"):
    features = f.invoke(endpoint='doc_rec', model='gpu_featurizer', data='lol')
    test = list(range(0,50))
    random.shuffle(test)
    output = {'physician_preference': test[:10]}
    return output