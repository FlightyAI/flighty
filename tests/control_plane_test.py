#!/usr/bin/env python3

import json
import os
import requests
import unittest

base_url = 'http://127.0.0.1/api/v1'


class TestEndpoint(unittest.TestCase):
    '''TODO - Use in-memory DB to make these tests have no side-effects'''

    def test_endpoint_create(self):
        '''Test Endpoint create'''
        response = requests.post("/".join([base_url, 'endpoints', 'create']), data=json.dumps({'name': 'doc-rec'}))
        output = response.json()
        self.assertEqual(output['name'], 'doc-rec')

    def test_endpoint_list(self):
        '''Test filtering logic when listing endpoint'''
        requests.post("/".join([base_url, 'endpoints', 'create']), data = json.dumps({'name': 'doc-rec-list'}))
        output = requests.get("/".join([base_url, 'endpoints', 'list', '?name=doc-rec-list'])).json()
        self.assertEqual(output[0]['name'], 'doc-rec-list')

# Test model artifact create
class TestArtifact(unittest.TestCase):
    def test_model_artifact_create(self):
        '''Test that we get well-formed JSON with name value from model artifact create'''
        with open('./README.md', 'rb') as f:
            response = requests.post("/".join([base_url, 'artifacts', 'create']), 
                files={'file': f, 'name': (None, 'model-artifact'),
                'version': (None, 1), 'type': (None, 'model')}).json()
        self.assertEqual(response['name'], 'model-artifact')
    
    def test_code_artifact_create(self):
        '''Test that we get well-formed JSON with name value from code artifact create'''
        with open('./model_server/customer_code/Archive.zip', 'rb') as f:
            response = requests.post("/".join([base_url, 'artifacts', 'create']), 
                files={'file': f, 'name': (None, 'code-artifact'),
                'version': (None, 1), 'type': (None, 'code')}).json()
        self.assertEqual(response['name'], 'code-artifact')
    
    def test_artifact_list(self):
        '''Checks that artifact list returns well-formatted JSON'''
        output = requests.get("/".join([base_url, 'artifacts', 'list'])).json()
        # Note, can't rely on test execution order in unittest
        #self.assertEqual(len(output), 2)




if (__name__ == '__main__'):
    unittest.main()