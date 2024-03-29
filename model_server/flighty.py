import logging

logger = logging.getLogger('flighty')

logger.info('Flighty was imported')

def get_model_path(name, version = None):
  if version is None:
    # need to get the latest
    return f'/code/flighty-files/{name}'
  else:
    return f'/code/flighty-files/{name}/{version}'
  