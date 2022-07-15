from fastapi import File
from . import helper

import flighty
import logging
import os
from pydantic import BaseModel

logger = logging.getLogger('main')

class User(BaseModel):
    id: int
    name = 'John Doe'

def init():
  logger.info('We just initialized')
  dir = flighty.get_model_path(name='first-artifact', version=2)
  logger.info(f"Get model path returns {dir}")
  try:
    logging.info(f"files are {os.listdir(dir)}")
  except FileNotFoundError:
    logging.info(f"artifact directory was not found")
    pass

def predict(data : User):
  logger.info(f'Predict called with data {data}')
