import os
from functools import wraps


class RangeFileWrapper:
    """FileWrapper with support for byte ranges.
    Borrowed from https://gist.github.com/dcwatson/cb5d8157a8fa5a4a046e"""

    def __init__(self, filelike, blksize=8192, offset=0, length=None):
        """Initialization function for iterable wrapper."""
        self.filelike = filelike
        self.filelike.seek(offset, os.SEEK_SET)
        self.remaining = length
        self.blksize = blksize

    def close(self):
        """Closes filelike."""
        if hasattr(self.filelike, 'close'):
            self.filelike.close()

    def __iter__(self):
        """Returns self as iterator."""
        return self

    def __next__(self):
        """Fetches next set of readable bytes."""
        if self.remaining is None:
            # If remaining is None, we're reading the entire file.
            data = self.filelike.read(self.blksize)
            if data:
                return data
            raise StopIteration()
        else:
            if self.remaining <= 0:
                raise StopIteration()
            data = self.filelike.read(min(self.remaining, self.blksize))
            if not data:
                raise StopIteration()
            self.remaining -= len(data)
            return data
