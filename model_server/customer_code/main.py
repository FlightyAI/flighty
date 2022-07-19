from fastapi import File
from . import helper

import flighty
import logging
import os
from pydantic import BaseModel

logger = logging.getLogger('customer_main')

class User(BaseModel):
    id: int
    name = 'John Doe'

def init():
    '''Sample init method'''
    logger.info('We just initialized hi gopal')
    helper.say_hello()
    dir = flighty.get_model_path(name='first-artifact', version=2)
    logger.info(f"Get model path returns {dir}")
    try:
        logging.info(f"model files are {os.listdir(dir)}")
    except FileNotFoundError:
        logging.info(f"artifact directory was not found")


def predict(data : User):
    '''Sample predict method with pydantic typing'''
    logger.info('Predict called with data %s', data)
