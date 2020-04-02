# suitcase.jsonl

This is a suitcase subpackage for reading a particular file format.

## Installation

```
pip install suitcase-jsonl
```

## Quick Start

```
import suitcase.jsonl
docs = db[-1].documents(fill=True)
suitcase.jsonl.export(docs, 'my_exported_files/')
```

The exported file will be saved as
`my_exported_files/9b82da80-a966-427e-8701-32cd6b807692.jsonl`.
The file prefix `9b82da80-a966-427e-8701-32cd6b807692` is the unique ID of the
run. The default file prefix can be changed with the `file_prefix` keyword
argument. See the documentation link below.

## Documentation

See the [suitcase documentation](https://blueskyproject.io/suitcase).
