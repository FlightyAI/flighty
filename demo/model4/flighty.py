import os
import random
import sys

current_directory = os.path.dirname(__file__)
parent_directory = os.path.abspath(os.path.dirname(os.path.dirname(current_directory)))
print(parent_directory)
sys.path.insert(0, parent_directory)

from snowflake_log import log_to_snowflake

def invoke(model, data):
  output = []
  for _ in range(128):
    output.append(random.random())

  log_to_snowflake(data, False, 'doc_rec', model, output)
  
  return output