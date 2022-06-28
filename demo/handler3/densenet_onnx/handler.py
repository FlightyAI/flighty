import random
import time


class Handler():
  def __init__(self):
      pass

  def predict(data, type="prod"):
    output = []
    for _ in range(128):
      output.append(random.random())
    time.sleep(0.5)

    return {'output': output}