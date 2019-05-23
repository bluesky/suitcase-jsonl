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


def test_file_prefix_formatting(file_prefix_list, example_data, tmp_path):
    '''Runs a test of the ``file_prefix`` formatting.
    ..note::
        Due to the `file_prefix_list` and `example_data` `pytest.fixture`'s
        this will run multiple tests each with a range of file_prefixes,
        detectors and event_types. See `suitcase.utils.conftest` for more info.
    '''
    collector = example_data()
    file_prefix = file_prefix_list()
    artifacts = export(collector, tmp_path, file_prefix=file_prefix)

    for name, doc in collector:
        if name == 'start':
            templated_file_prefix = file_prefix.format(
                start=doc).partition('-')[0]
            break

    if artifacts:
        unique_actual = set(str(artifact).split('/')[-1].partition('-')[0]
                            for artifact in artifacts['all'])
        assert unique_actual == set([templated_file_prefix])
