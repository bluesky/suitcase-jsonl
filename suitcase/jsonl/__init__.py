import event_model
from pathlib import Path
import suitcase.utils
from ._version import get_versions
import json

__version__ = get_versions()['version']
del get_versions


def export(gen, directory, file_prefix='{uid}',
           cls=event_model.NumpyEncoder, **kwargs):
    serializer = Serializer(directory, file_prefix, cls=cls, **kwargs)
    try:
        for item in gen:
            serializer(*item)
    finally:
        serializer.close()
    return serializer.artifacts


class Serializer(event_model.DocumentRouter):
    def __init__(self, directory, file_prefix='{uid}',
                 cls=event_model.NumpyEncoder, **kwargs):

        self._output_file = None
        self._file_prefix = file_prefix
        self._templated_file_prefix = ''
        self._kwargs = dict(cls=cls, **kwargs)
        self._start_found = False

        if isinstance(directory, (str, Path)):
            self._manager = suitcase.utils.MultiFileManager(directory)
        else:
            self._manager = directory

    @property
    def artifacts(self):
        # The manager's artifacts attribute is itself a property, and we must
        # access it anew each time to be sure to get the latest content.
        return self._manager.artifacts

    def _check_start(self, doc):
        if self._start_found:
            raise RuntimeError(
                "The serializer in suitcase-jsonl expects "
                "documents from one run only. Two `start` documents where "
                "sent to it")
        else:
            self._start_found = True
            self._templated_file_prefix = self._file_prefix.format(**doc)

    def _get_file(self):
        filename = (f'{self._templated_file_prefix}.jsonl')
        self._output_file = self._manager.open('all', filename, 'xt')

    def __call__(self, name, doc):
        if name == 'start':
            self._check_start(doc)
            self._get_file()

        line = "%s\n" % json.dumps((name, doc), **self._kwargs)
        self._output_file.write(line)
        return name, doc

    def close(self):
        self._manager.close()
