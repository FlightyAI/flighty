import os
import pathlib
import random
import sys


class Model():
  def __init__(self):
      pass

  def predict(data, type="prod"):
    output = []
    for _ in range(128):
      output.append(random.random())

    return {'output': output}