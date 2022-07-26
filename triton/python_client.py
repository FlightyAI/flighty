import tritonclient.http as httpclient
import numpy as np

triton_client = httpclient.InferenceServerClient(url='localhost:8000')

def infer():
    inputs = []
    outputs = []
    inputs.append(httpclient.InferInput('INPUT0', [1, 16], "INT32"))
    inputs.append(httpclient.InferInput('INPUT1', [1, 16], "INT32"))

    sample_input = np.random.randint(100, size=(1, 16), dtype=np.int32)
    # Initialize the data
    inputs[0].set_data_from_numpy(sample_input, binary_data=False)
    inputs[1].set_data_from_numpy(sample_input, binary_data=True)

    outputs.append(httpclient.InferRequestedOutput('OUTPUT0', binary_data=True))
    outputs.append(httpclient.InferRequestedOutput('OUTPUT1',
                                                   binary_data=False))
    query_params = {'test_1': 1, 'test_2': 2}
    results = triton_client.infer(
        'simple',
        inputs,
        outputs=outputs,
        query_params=query_params)

    return results.get_response()

if __name__ == ('__main__'):
    for i in range(1000):
        print(infer())