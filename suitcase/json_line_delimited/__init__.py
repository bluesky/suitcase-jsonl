import event_model
from pathlib import Path
import suitcase.utils
from ._version import get_versions


__version__ = get_versions()['version']
del get_versions


# Suitcase subpackages must follow strict naming and interface conventions. The
# public API must include Serializer and should include export if it is
# intended to be user-facing.


def export(gen, directory, file_prefix, **kwargs):
    serializer = Serializer(directory, file_prefix, **kwargs)
    try:
        for item in gen:
            serializer(*item)
    finally:
        serializer.close()

     return serializer.artifacts


class Serializer(event_model.DocumentRouter):
    def __init__(self, directory, file_prefix, **kwargs):
        if isinstance(directory, (str, Path)):
            self.manager = suitcase.utils.MultiFileManager(directory)
        else:
            self.manager = directory
        self.artifacts = self.manager._artifacts  # Expose as public.
        ...

    def close(self):
        ...
