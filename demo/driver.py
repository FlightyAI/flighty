from flighty import Flighty

Flighty.initialize(name='great_clinic')
Flighty.create_endpoint(name='doc_rec')
Flighty.create_model(endpoint='doc_rec', model_name='rules', model_path='model1')
Flighty.show_endpoints()
Flighty.create_model(endpoint='doc_rec', model_name='xgboost', model_path='model2')
Flighty.update_endpoint(endpoint='doc_rec', traffic={'rules': {'prod': 100, 'shadow': 0}, 'xgboost': {'prod': 0, 'shadow': 100}})

# test shadow traffic logic
Flighty.invoke(endpoint='doc_rec', model=None, data={'Survey_responses': {1: 'I have some pain in my knee'}})

# Test GPU model alone
Flighty.create_model(endpoint='doc_rec', model_name='gpu_featurizer', model_path='model3')
Flighty.invoke(endpoint='doc_rec', model='gpu_featurizer', data={'Survey_responses': {1: 'I am afraid of needles'}})

# Add in CPU model that invokes GPU model
Flighty.create_model(endpoint='doc_rec', model_name='hybrid_cpu_gpu', model_path='model4')
Flighty.invoke(endpoint='doc_rec', model='hybrid_cpu_gpu', data={'Survey_responses': {1: 'I do not like to climb stairs'}})

# Enable caching
Flighty.enable_caching(endpoint='doc_rec', ttl=3600)
Flighty.invoke(endpoint='doc_rec', model='hybrid_cpu_gpu', data={'Survey_responses': {1: 'I am looking for help'}})
Flighty.invoke(endpoint='doc_rec', model='hybrid_cpu_gpu', data={'Survey_responses': {1: 'I am looking for help'}})