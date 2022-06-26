import json

from flighty import Flighty

Flighty.initialize()
Flighty.create_endpoint('doc_rec')
Flighty.create_model('doc_rec', 'rules', 'model1')
Flighty.create_model('doc_rec', 'xgboost', 'model2')
Flighty.update_endpoint('doc_rec', traffic={'rules': {'prod': 100, 'shadow': 0}, 'xgboost': {'prod': 0, 'shadow': 100}})


# test shadow traffic logic
Flighty.invoke('doc_rec', None, {'Survey_responses': {1: 'I am looking for help'}})

# Test GPU model alone
Flighty.create_model('doc_rec', 'gpu_featurizer', 'model3')
Flighty.invoke('doc_rec', 'gpu_featurizer', {'Survey_responses': {1: 'I am looking for help'}})

# Add in CPU model that invokes GPU model
Flighty.create_model('doc_rec', 'hybrid_cpu_gpu', 'model4')
Flighty.invoke('doc_rec', 'hybrid_cpu_gpu', {'Survey_responses': {1: 'I am looking for help'}})
