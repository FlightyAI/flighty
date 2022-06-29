import os
import pathlib
import random
import sys

parent_directory = os.path.abspath(pathlib.Path('./..'))
sys.path.insert(0, parent_directory)

class Handler():
  def __init__(self):
    pass

  def predict(data, type="prod"):
    test = list(range(0,50))
    random.shuffle(test)
    output = {'physician_preference': test[:10]}
  
    return output