import os
import pathlib
import sys

parent_directory = os.path.abspath(pathlib.Path('./..'))
sys.path.insert(0, parent_directory)

class Handler():
  def __init__(self):
    pass

  def predict(self, data, type="prod"):
    from flighty import Flighty
    # if item_ID in set of interesting IDs or if test_group = 'a', then invoke(handlerA) else invoke(handlerB)
    features = Flighty.invoke(endpoint='doc_rec', handler='gpu_featurizer', data=data)
    output = Flighty.invoke(endpoint='doc_rec', handler='xgboost', data={"inputs": features['output']})
    return output
