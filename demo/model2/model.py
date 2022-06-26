import random

class Model():
  def __init__(self, snowflake_user, snowflake_password, snowflake_account):
    pass

  def predict(self, data, type="prod"):
    test = list(range(0,50))
    random.shuffle(test)
    output = {'physician_preference': test[:10]}
    return output