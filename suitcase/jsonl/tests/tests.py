import json
from event_model import NumpyEncoder
from suitcase.jsonl import export


def test_export(tmp_path, example_data):
    documents = example_data()
    artifacts = export(documents, tmp_path)
    filepath, = artifacts['all']
    with open(filepath) as file:
        actual = [json.loads(line) for line in file]
    expected = [json.loads(json.dumps(doc, cls=NumpyEncoder))
                for doc in documents]
    assert actual == expected
