import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('flighty')

logger.info('Flighty was imported')

def get_model_path(name, version = None):
  if not version:
    # need to get the latest
    return f'/code/flighty-files/{name}'
  else:
    return f'/code/flighty-files/{name}/{version}'
  