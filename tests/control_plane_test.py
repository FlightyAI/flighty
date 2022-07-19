#!/usr/bin/env python3


import json
import os
import time

import requests
import unittest


# If testing with Docker use this
base_url = 'http://127.0.0.1:8000'

# If testing with full Kubernetes setup use this
# base_url = 'http://127.0.0.1/api/v1'


def get_num_artifacts():
    '''Return number of handlers that exist'''
    return len(requests.get(f'{base_url}/artifacts/list').json())

def get_num_handlers():
    '''Return number of handlers that exist'''
    return len(requests.get(f'{base_url}/handlers/list').json())

def create_artifact(**kwargs):
    '''Create artifact with specified args'''
    return requests.post(f'{base_url}/artifacts/create',
        files=kwargs)

def delete_artifact(**kwargs):
    '''Delete artifact with specified args'''
    return requests.delete(f'{base_url}/artifacts/delete',
        json=kwargs)

def create_endpoint(**kwargs):
    '''Create endpoint with specified args'''
    return requests.post(f'{base_url}/endpoints/create',
             json=kwargs)

def create_handler(**kwargs):
    '''Create handler with specified args'''
    return requests.post(f'{base_url}/handlers/create', 
        json=kwargs)

def get_handler(**kwargs):
    '''Get handler with specified args'''
    return requests.get(f'{base_url}/handlers/get', 
        json=kwargs)


def delete_handler(**kwargs):
    '''Delete specified handler'''
    return requests.delete(f'{base_url}/handlers/delete',
        json=kwargs)

def delete_endpoint(**kwargs):
    '''Delete specified endpoint'''
    return requests.delete(f'{base_url}/endpoints/delete',
        json=kwargs)

def invoke_endpoint(endpoint_name, **kwargs):
    '''Invokes the endpoint with provided arguments'''
    print(f'kwargs are {kwargs}')
    response = requests.post(f'http://127.0.0.1/{endpoint_name}/infer',
        json=kwargs)
    retry_count = 0

    # Envoy proxy returns 503s while it starts up, I guess should use a readiness probe
    while retry_count < 10 and response.status_code != 200:
        time.sleep(2)
        response = requests.post(f'http://127.0.0.1/{endpoint_name}/infer',
        json=kwargs)
        retry_count += 1
        print(f'invoke retry # {retry_count}, current response code {response.status_code}')
    return response


class TestInvoke(unittest.TestCase):
    # Create handler with customer code archive
    # Invoke that handler
    # We'll have to test this somewhere else because when testing locally 
    # the mounting of archives doesn't work
    pass

    # def test_invoke(self):
    #     '''Test that invoking dummy model works'''
    #     with open('./README.md', 'rb') as f:
    #         response = create_artifact(file=f, name=(None, 'model-artifact'),
    #             version=(None, 1), type=(None, 'model'))
    #         print(response.text)

    #     with open('./model_server/customer_code/Archive.zip', 'rb') as f:
    #         response = create_artifact(file=f, name=(None, 'code-artifact'),
    #             version=(None, 1), type=(None, 'code'))
    #         output = response.json()
    #         print(f"listing files at code artifact {os.listdir(output['path'])}")
    #     create_endpoint(name='doc-rec')
    #     response = create_handler(name='rules', version=1, model_artifact='model-artifact',
    #         code_artifact='code-artifact', model_artifact_version=1, code_artifact_version=1,
    #         endpoint='doc-rec')
    #     self.assertEqual(response.status_code, 200, msg=response.text)
    #     response = invoke_endpoint(endpoint_name='doc-rec', data = {'id':0, 'name': 'John Doe'})

    #     self.assertEqual(response.status_code, 200, msg=response.text)
    #     delete_handler(name='rules', version=1, endpoint='doc-rec')
    #     delete_artifact(name='model-artifact', version=1)
    #     delete_artifact(name='code-artifact', version=1)
    #     delete_endpoint(name='doc-rec')


class TestHandler(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Create model artifact
        with open('./README.md', 'rb') as f:
            create_artifact(file=f, name=(None, 'model-artifact'),
                version=(None, 1), type=(None, 'model'))

        # Create code artifact
        with open('./model_server/customer_code/Archive.zip', 'rb') as f:
            create_artifact(file=f, name=(None, 'code-artifact'),
                version=(None, 1), type=(None, 'code'))
        
        # Create endpoint
        create_endpoint(name='doc-rec')
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        delete_artifact(name='model-artifact', version=1)
        delete_artifact(name='code-artifact', version=1)
        delete_endpoint(name='doc-rec')
        return super().tearDownClass()

    def setUp(self):
        self.base_url = f'{base_url}/handlers'

    def test_get_handler(self):
        '''Should return a 400 if handler does not exist and a 200 if it does'''
        response = get_handler(name='doesnot_exist', version=0, endpoint='doc-rec')
        self.assertEqual(response.status_code, 400, msg=response.text)
        create_handler(name='rules', version=1, model_artifact='model-artifact',
            code_artifact='code-artifact', model_artifact_version=1, code_artifact_version=1,
            endpoint='doc-rec')
        response = get_handler(name='rules', version=1, endpoint='doc-rec')
        self.assertEqual(response.status_code, 200, msg=response.text)
        delete_handler(name='rules', version=1, endpoint='doc-rec')

    def test_duplicate_create(self):
        '''Should return a 400 if we create a handler with same name as existing'''
        create_handler(name='rules', version=1, model_artifact='model-artifact',
            code_artifact='code-artifact', model_artifact_version=1, code_artifact_version=1,
            endpoint='doc-rec')
        response = create_handler(name='rules', version=1, model_artifact='model-artifact',
            code_artifact='code-artifact', model_artifact_version=1, code_artifact_version=1,
            endpoint='doc-rec')
        self.assertEqual(response.status_code, 400, msg=response.text)
        delete_handler(name='rules', version=1, endpoint='doc-rec')
        

    def test_handler_create(self):
        '''Create a handler, check that it was created, then delete it'''
        response = create_handler(name='rules', version=1, model_artifact='model-artifact',
            code_artifact='code-artifact', model_artifact_version=1, code_artifact_version=1,
            endpoint='doc-rec')
        self.assertEqual(get_num_handlers(), 1, msg=response.text)
        response = delete_handler(name='rules', version=1, endpoint='doc-rec')
        self.assertEqual(get_num_handlers(), 0, msg=response.text)

    def test_delete_endpoint_with_handler(self):
        '''An endpoint with an associated handler should not be deleted'''
        create_handler(name='rules', version=1, model_artifact='model-artifact',
            code_artifact='code-artifact', model_artifact_version=1, code_artifact_version=1,
            endpoint='doc-rec')
        response = delete_endpoint(name='doc-rec')
        delete_handler(name='rules', version=1, endpoint='doc-rec')
        self.assertEqual(response.status_code, 400, msg=response.text)

    def test_delete_artifact_with_handler(self):
        '''An artifact with an associated handler should not be deleted'''
        create_handler(name='rules', version=1, model_artifact='model-artifact',
            code_artifact='code-artifact', model_artifact_version=1, code_artifact_version=1,
            endpoint='doc-rec')
        response = delete_artifact(name='code-artifact', version=1)
        delete_handler(name='rules', version=1, endpoint='doc-rec')
        self.assertEqual(response.status_code, 400, msg=response.text)


class TestEndpoint(unittest.TestCase):
    '''TODO - Use in-memory DB to make these tests have no side-effects'''

    def setUp(self):
        self.base_url = f'{base_url}/endpoints'

    def get_num_endpoints(self):
        '''Return number of endpoints that exist'''
        return len(requests.get(f'{self.base_url}/list').json())

    def test_endpoint_create(self):
        '''Test Endpoint create'''
        response = create_endpoint(name='doc-rec')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_num_endpoints(), 1)
        response = delete_endpoint(name='doc-rec')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_num_endpoints(), 0)

    def test_endpoint_list(self):
        '''Test filtering logic when listing endpoint'''
        create_endpoint(name='doc-rec-list')
        output = requests.get("/".join([base_url, 'endpoints', 'list']) + '?name=doc-rec-list')
        self.assertEqual(output.status_code, 200)
        response = delete_endpoint(name='doc-rec-list')
        self.assertEqual(response.status_code, 200)

    def test_delete_nonexistent_endpoint(self):
        '''Deleting a nonexisting endpoint should return a 400'''
        response = delete_endpoint(name='this-endpoint-should-not-exist')
        self.assertEqual(response.status_code, 400)



# Test model artifact create
class TestArtifact(unittest.TestCase):
    def get_num_artifacts(self):
        return len(requests.get("/".join([base_url, 'artifacts', 'list'])).json())

    def test_model_artifact_create(self):
        '''Test that we get well-formed JSON with name value from model artifact create'''
        with open('./README.md', 'rb') as f:
            response = create_artifact(file=f, name=(None, 'model-artifact'),
                version=(None, 1), type=(None, 'model'))
        self.assertEqual(response.status_code, 200, msg=response.text)
        self.assertEqual(self.get_num_artifacts(), 1)
        response = delete_artifact(name='model-artifact', version=1)
        self.assertEqual(response.status_code, 200, msg=response.text)
        self.assertEqual(self.get_num_artifacts(), 0)

    
    def test_code_artifact_create(self):
        '''Test that we get well-formed JSON with name value from code artifact create'''
        with open('./model_server/customer_code/Archive.zip', 'rb') as f:
            response = create_artifact(file=f, name=(None, 'code-artifact'),
                version=(None, 1), type=(None, 'code'))
        self.assertEqual(response.status_code, 200, msg=response.text)
        self.assertEqual(self.get_num_artifacts(), 1)
        response = delete_artifact(name='code-artifact', version=1)
        self.assertEqual(response.status_code, 200, msg=response.text)
        self.assertEqual(self.get_num_artifacts(), 0)
    
    def test_delete_nonexistent_artifact(self):
        '''Checks that artifact delete returns what we expect'''
        response = delete_artifact(name='should-not-exist-artifact', version=1)
        self.assertEqual(response.status_code, 400)





if (__name__ == '__main__'):
    unittest.main()