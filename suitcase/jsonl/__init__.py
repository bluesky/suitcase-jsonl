import event_model
from pathlib import Path
import suitcase.utils
from ._version import get_versions
import json

__version__ = get_versions()['version']
del get_versions


def export(gen, directory, file_prefix='{start[uid]}',
           cls=event_model.NumpyEncoder, **kwargs):

    """
    Export a stream of documents to a newline-delimited JSON file.

    All documents are recorded as seperate lines with the form [name, doc].
    This creates a file named: ``<directory>/<file_prefix>.jsonl``

    .. note::

        This can alternatively be used to write data to generic buffers rather
        than creating files on disk. See the documentation for the
        ``directory`` parameter below.

    Parameters
    ----------
    gen : generator
        expected to yield ``(name, document)`` pairs
    directory : string, Path or Manager.
        For basic uses, this should be the path to the output directory given
        as a string or Path object. Use an empty string ``''`` to place files
        in the current working directory.
        In advanced applications, this may direct the serialized output to a
        memory buffer, network socket, or other writable buffer. It should be
        an instance of ``suitcase.utils.MemoryBufferManager`` and
        ``suitcase.utils.MultiFileManager`` or any object implementing that
        interface. See the suitcase documentation
        (http://nsls-ii.github.io/suitcase) for details.
    file_prefix : str, optional
        The first part of the filename of the generated output files. This
        string may include templates as in
        ``{start[proposal_id]}-{start[sample_name]}-``,
        which are populated from the RunStart document. The default value is
        ``{start[uid]}`` which is guaranteed to be present and unique. A more
        descriptive value depends on the application and is therefore left to
        the user.
    cls : Encoder class, optional
        A ``json.JSONEncoder`` class that is used for parsing the documents
        into valid json objects. The default is ``event_model.NumpyEncoder``
        which also converts all numpy objects into built-in python objects.

    Returns
    -------
    artifacts : dict
        Maps 'labels' to lists of artifacts (e.g. filepaths)

    Examples
    --------
    Generate files with unique-identifier names in the current directory.

    >>> export(gen, '')

    Generate files with more readable metadata in the file names.

    >>> export(gen, '', '{start[plan_name]}-{start[motors]}-')

    Include the experiment's start time formatted as YYYY-MM-DD_HH-MM.

    >>> export(gen, '', '{start[time]:%Y-%m-%d_%H:%M}-')

    Place the files in a different directory, such as on a mounted USB stick.

    >>> export(gen, '/path/to/my_usb_stick')
    """

    with Serializer(directory, file_prefix, cls=cls, **kwargs) as serializer:
        for item in gen:
            serializer(*item)

    return serializer.artifacts


class Serializer(event_model.DocumentRouter):

    """
    Serialize a stream of documents to a json line delimited file.

    All documents are recorded as seperate lines with the form (name, doc) This
    creates a file named: ``<directory>/<file_prefix>.jsonl``
    .. note::
        This can alternatively be used to write data to generic buffers rather
        than creating files on disk. See the documentation for the
        ``directory`` parameter below.
    Parameters
    ----------
    gen : generator
        expected to yield ``(name, document)`` pairs
    directory : string, Path or Manager.
        For basic uses, this should be the path to the output directory given
        as a string or Path object. Use an empty string ``''`` to place files
        in the current working directory.
        In advanced applications, this may direct the serialized output to a
        memory buffer, network socket, or other writable buffer. It should be
        an instance of ``suitcase.utils.MemoryBufferManager`` and
        ``suitcase.utils.MultiFileManager`` or any object implementing that
        interface. See the suitcase documentation
        (http://nsls-ii.github.io/suitcase) for details.
    file_prefix : str, optional
        The first part of the filename of the generated output files. This
        string may include templates as in
        ``{start[proposal_id]}-{start[sample_name]}-``,
        which are populated from the RunStart document. The default value is
        ``{start[uid]}`` which is guaranteed to be present and unique. A more
        descriptive value depends on the application and is therefore left to
        the user.
    cls : Encoder class, optional
        A ``json.JSONEncoder`` class that is used for parsing the documents
        into valid json objects. The default is ``event_model.NumpyEncoder``
        which also converts all numpy objects into built-in python objects.
    flush : boolean
        Flush the file to disk after each document. As a consequence, writing
        the full document stream is slower but each document is immediately
        available for reading. False by default.

    Examples
    --------
    Generate files with unique-identifier names in the current directory.

    >>> export(gen, '')

    Generate files with more readable metadata in the file names.

    >>> export(gen, '', '{start[plan_name]}-{start[motors]}-')

    Include the experiment's start time formatted as YYYY-MM-DD_HH-MM.

    >>> export(gen, '', '{start[time]:%Y-%m-%d_%H:%M}-')

    Place the files in a different directory, such as on a mounted USB stick.

    >>> export(gen, '/path/to/my_usb_stick')
    """

    def __init__(self, directory, file_prefix='{start[uid]}',
                 cls=event_model.NumpyEncoder, flush=False, **kwargs):

        self._output_file = None
        self._file_prefix = file_prefix
        self._templated_file_prefix = ''
        self._kwargs = dict(cls=cls, **kwargs)
        self._flush = flush
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
            self._templated_file_prefix = self._file_prefix.format(start=doc)

    def _get_file(self):
        filename = (f'{self._templated_file_prefix}.jsonl')
        self._output_file = self._manager.open('all', filename, 'xt')

    def __call__(self, name, doc):
        if name == 'start':
            self._check_start(doc)
            self._get_file()

        line = "%s\n" % json.dumps((name, doc), **self._kwargs)
        self._output_file.write(line)
        if self._flush:
            self._output_file.flush()
        return name, doc

    def stop(self, doc):
        self.close()

    def close(self):
        self._manager.close()

    def __enter__(self):
        return self

    def __exit__(self, *exception_details):
        self.close()
