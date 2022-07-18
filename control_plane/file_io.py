'''Methods to handle file I/O of artifacts'''

import logging
import os
import shutil

import crud


logger = logging.getLogger('file_io')

def get_artifact_dir_path(name, version):
    '''Return the path to the directory of the given flighty artifact'''
    base_artifact_path = os.path.join('flighty-files', name, str(version))
    artifact_dir_path = os.path.join(os.path.dirname(os.path.abspath('__file__')),
        base_artifact_path)
    return artifact_dir_path


def write_artifact(file, name, version):
    '''Writes artifact directory to database and unpacks .zip files automatically'''
    artifact_dir_path = get_artifact_dir_path(name, version)
    artifact_file_path = os.path.join(artifact_dir_path, file.filename)

    # Write file to mounted volume in a place that handlers
    # will be able to find it
    os.makedirs(artifact_dir_path, exist_ok=True)
    with open(artifact_file_path, 'wb') as f:
        f.write(file.file.read())
        logger.info("wrote file out to path %s", artifact_file_path)

    # unpack zip file if it is a zip
    try:
        shutil.unpack_archive(artifact_file_path, artifact_dir_path)
        logger.info('archive deteced, unpacking...')

        # Delete the zip file we just unpacked
        os.remove(artifact_file_path)
    except shutil.ReadError as _: # not a zip file, so we can't unpack it
        pass
    
    return artifact_dir_path

def delete_artifact(db, name, version):
    '''Deletes the directory at the path specified in the database'''
    artifact = crud.get_artifact(db=db, name=name, version=version)
    shutil.rmtree(artifact.path)