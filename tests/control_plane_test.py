#!/usr/bin/env python3


import json
import os

import requests
import unittest


# If testing with Docker use this
base_url = 'http://127.0.0.1:8000' 

# If testing with full Kubernetes setup use this
base_url = 'http://127.0.0.1/api/v1'

class TestEndpoint(unittest.TestCase):
    '''TODO - Use in-memory DB to make these tests have no side-effects'''

    def test_endpoint_create(self):
        '''Test Endpoint create'''
        response = requests.post("/".join([base_url, 'endpoints', 'create']),
             data=json.dumps({'name': 'doc-rec'}))
        self.assertEqual(response.status_code, 200)

    def test_endpoint_list(self):
        '''Test filtering logic when listing endpoint'''
        requests.post("/".join([base_url, 'endpoints', 'create']), data = json.dumps({'name': 'doc-rec-list'}))
        output = requests.get("/".join([base_url, 'endpoints', 'list']) + '?name=doc-rec-list')
        self.assertEqual(output.status_code, 200)

# Test model artifact create
class TestArtifact(unittest.TestCase):
    def get_num_artifacts(self):
        return len(requests.get("/".join([base_url, 'artifacts', 'list'])).json())

    def test_model_artifact_create(self):
        '''Test that we get well-formed JSON with name value from model artifact create'''
        with open('./README.md', 'rb') as f:
            response = requests.post("/".join([base_url, 'artifacts', 'create']), 
                files={'file': f, 'name': (None, 'model-artifact'),
                'version': (None, 1), 'type': (None, 'model')})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_num_artifacts(), 1)
        response = requests.delete(url="/".join([base_url, 'artifacts', 'delete']),
            json={'name': 'model-artifact', 'version': 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_num_artifacts(), 0)

    
    def test_code_artifact_create(self):
        '''Test that we get well-formed JSON with name value from code artifact create'''
        with open('./model_server/customer_code/Archive.zip', 'rb') as f:
            response = requests.post("/".join([base_url, 'artifacts', 'create']), 
                files={'file': f, 'name': (None, 'code-artifact'),
                'version': (None, 1), 'type': (None, 'code')})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_num_artifacts(), 1)
        response = requests.delete(url="/".join([base_url, 'artifacts', 'delete']),
            json={'name': 'code-artifact', 'version': 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_num_artifacts(), 0)
    
    def test_delete_nonexistent_artifact(self):
        '''Checks that artifact delete returns what we expect'''
        response = requests.delete(url="/".join([base_url, 'artifacts', 'delete']),
            json={'name': 'this-artifact-shouldnot-exist', 'version': 1})
        self.assertEqual(response.status_code, 400)





if (__name__ == '__main__'):
    unittest.main()