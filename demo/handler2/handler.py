import random

class Handler():
  def __init__(self):
    pass

  def predict(self, data, type="prod"):
    test = list(range(0,50))
    random.shuffle(test)
    output = {'physician_preference': test[:10]}
    return output