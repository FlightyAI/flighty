from flighty import Flighty

# Initialize endpoint with two handlers, one receiving only shadow traffic
Flighty.initialize(name='great_clinic', docker_wait=1, deploy_wait=1, traffic_wait=1)
Flighty.create_endpoint(name='doc_rec')
Flighty.upload_artifact(name='rules', folder_path='./models/rules')
Flighty.create_handler(endpoint='doc_rec', name='rules', folder_path='./handler1')
Flighty.show_endpoints()
Flighty.create_handler(endpoint='doc_rec', name='xgboost', folder_path='./handler2')
Flighty.upload_artifact(name='rules', folder_path='./models/xgboost')
Flighty.update_endpoint(endpoint='doc_rec', traffic={'rules': {'prod': 100, 'shadow': 0}, 'xgboost': {'prod': 0, 'shadow': 100}})

# Test shadow traffic logic
Flighty.invoke(endpoint='doc_rec', handler=None, data={'Survey_responses': {1: 'I have some pain in my knee'}})

# Test GPU handler alone
Flighty.upload_artifact(name='rules', folder_path='./models/gpu_featurizer')
Flighty.create_handler(endpoint='doc_rec', name='gpu_featurizer', folder_path='./handler3')
Flighty.invoke(endpoint='doc_rec', handler='gpu_featurizer', data={'Survey_responses': {1: 'I am afraid of needles'}})

# Add in CPU handler that invokes GPU handler
Flighty.create_handler(endpoint='doc_rec', name='hybrid_cpu_gpu', folder_path='./handler4')
Flighty.invoke(endpoint='doc_rec', handler='hybrid_cpu_gpu', data={'Survey_responses': {1: 'I do not like to climb stairs'}})

# Enable caching
Flighty.enable_caching(endpoint='doc_rec', ttl=3600)
Flighty.invoke(endpoint='doc_rec', handler='hybrid_cpu_gpu', data={'Survey_responses': {1: 'I am looking for help'}})
Flighty.invoke(endpoint='doc_rec', handler='hybrid_cpu_gpu', data={'Survey_responses': {1: 'I am looking for help'}})