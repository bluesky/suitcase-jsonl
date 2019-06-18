# suitcase.jsonl

This is a suitcase subpackage for reading a particular file format.

## Installation

```
pip install suitcase-jsonl
```

## Common use cases
The common use case for this file format in streaming mode is to attach a
RunRouter to the RunEngine (RE) using the following lines:

```python
# create a factory that will use the serializer to create on-the-fly files.
def factory(name, start_doc):
    # the following creates a serializer that will close the file when the stop
    # document is sent to it.
    serializer = suitcase.jsonl.Serializer(directory='...',
                                         file_prefix='...')
    serializer(name, start_doc)
    # ensure that any further documents from the RunRouter are processed.
    return [serializer], []

# generate the RunRouter from the factory and subscribe it to the RunEngine
rr = event_model.RunRouter([factory])
RE.subscribe(rr)
```

For a simple 'count' scan the file output will look like the following with
each document type found on a new line in the file:

```python
["start", {"uid": "cd92fe6d-bcef-44cf-9624-205d7faa8164",
           "time": 1560865593.134833, "plan_name": "count", "num_points": 1,
           "plan_type": "generator",
           "hints": {"dimensions": [[["time"], "primary"]]}, "scan_id": 3,
           "num_intervals": 0, "detectors": ["det"],
           "plan_args": {"detectors":
                         ["SynGauss(name='det', value=1.0,
                                    timestamp=1560865377.9802923)"],
                         "num": 1},
           "versions": {"ophyd": "1.3.0.post285+gbebb617",
                        "bluesky": "1.4.1+343.ga4fc28ec"}}]
["descriptor", {"run_start": "cd92fe6d-bcef-44cf-9624-205d7faa8164",
                "time": 1560865593.13851,
                "data_keys": {"det": {"source": "SIM:det", "dtype": "number",
                              "shape": [], "precision": 3,
                              "object_name": "det"}},
                "uid": "ce14d1cb-2534-4910-88da-0c1425aef920",
                "configuration":{"det":
                    {"data": {"det": 1.0},
                     "timestamps": {"det": 1560865593.1378844},
                     "data_keys": {"det": {"source": "SIM:det",
                                           "dtype": "number", "shape": [],
                                           "precision": 3}}}},
                "name": "primary", "hints": {"det": {"fields": ["det"]}},
                "object_keys": {"det": ["det"]}}]
["event_page", {"time": [1560865593.140267],
                "uid": ["bb2886e5-0ea2-4cd5-9381-2b5f530d1929"],
                "seq_num": [1],
                "descriptor": "ce14d1cb-2534-4910-88da-0c1425aef920",
                "filled": {}, "data": {"det": [1.0]},
                "timestamps": {"det": [1560865593.1378844]}}]
["stop", {"run_start": "cd92fe6d-bcef-44cf-9624-205d7faa8164",
          "time": 1560865593.1410978,
          "uid": "7e43d05b-50b8-4b97-b4d0-41c7ffb778d1",
          "exit_status": "success", "reason": "",
          "num_events": {"primary": 1}}]
```

If for some reason only the start document is required, then the following can
be used to create the factory:

```python
import event_model
import suitcase.jsonl

def factory(name, start_doc):
    # The following ensures that the file will be closed after the start doc is
    # written into the file.
    with suitcase.jsonl.Serializer(directory='...',
                                   file_prefix='...') as serializer:
        serializer(name, start_doc)
    # We do not need any further documents from the RunRouter.
    return [], []

rr = event_model.RunRouter([factory])
RE.subscribe(rr)
```

The same count scan from above will then have a single line file with the
structure like:

```
["start", {"uid": "cd92fe6d-bcef-44cf-9624-205d7faa8164",
           "time": 1560865593.134833, "plan_name": "count", "num_points": 1,
           "plan_type": "generator",
           "hints": {"dimensions": [[["time"], "primary"]]}, "scan_id": 3,
           "num_intervals": 0, "detectors": ["det"],
           "plan_args": {"detectors":
                         ["SynGauss(name='det', value=1.0,
                                    timestamp=1560865377.9802923)"],
                         "num": 1},
           "versions": {"ophyd": "1.3.0.post285+gbebb617",
                        "bluesky": "1.4.1+343.ga4fc28ec"}}]

```

