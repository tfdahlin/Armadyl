import io
import os
import re
from wsgiref.util import FileWrapper

from pycnic.core import Handler as PycnicHandler

from .statuses import STATUSES
from .util import RangeFileWrapper


class BaseHandler(PycnicHandler):
    def __init__(self, version=None):
        super().__init__()
        self.version = version

    # GET and OPTIONS must always be supported.
    # OPTIONS is automatically handled by pycnic
    # GET will return 501 Not Implemented by default
    def get(self):
        return self.HTTP(501)

    def HTTP(self, code, data=None, error=None):
        json_response = {
            'status_code': code,
            'status': STATUSES[code],
            'data': data,
            'error': error
        }
        if self.version:
            json_response['version'] = self.version

        self.response.status_code = code
        return json_response

    def parse_form_data(self):
        """Processes multipart/form-data requests into a dict.

        Keys of the dict are field names. Each value is a dict with a
        'metadata' and 'data' dict. Metadata contains metadata about the
        field, data is the actual input data.

        Return format:
        {
            '<field name>': {
                'metadata': {
                    key: value  # e.g. 'name': 'username'
                },
                'data': Bytes  # e.g. b'Crash Override'
            },
            ...
        }
        """
        result = {}

        content_body = self.request.body
        marker = content_body.split(b'\r\n', 1)[0]
        all_content = [x.strip() for x in content_body.split(marker)[1:-1]]
        form_data = [x.split(b'\r\n\r\n') for x in all_content]

        for element in form_data:
            curr_element = {
                'metadata': {},
                'data': None,
            }
            raw_metadata = element[0]
            if b'\r\n' in raw_metadata:
                disposition, content_type = raw_metadata.split(b'\r\n')
            else:
                disposition = raw_metadata

            # Remove excess spaces, then split appropriately
            # and drop "Content-Disposition: form-data; "
            metadata = disposition.strip().split(b'; ')[1:]
            for component in metadata:
                key, value = component.decode('utf-8').split('=', 1)
                value = value[1:-1]
                curr_element['metadata'][key] = value

            curr_element['data'] = element[1]
            element_name = curr_element['metadata']['name']
            result[element_name] = curr_element
            #result.append(curr_element)

        return result


class JsonEndpoint(BaseHandler):
    ...


class ServeFile(BaseHandler):
    def get_wrapper(self, filelike, blksize=8192, offset=0, length=None):
        """Fetches either a wsgi FileWrapper or a RangeFileWrapper.

        As a side effect, this will also automatically set the Content-Length
        header. If relevant, the Content-Range header will also be set.

        Returns:
            BaseHandler.HTTP(416) for out-of-bounds range requests
            RangeFileWrapper for in-bounds range requests
            wsgiref.util.FileWrapper for in-bound non-range requests
        Raises:
            OSError, if file could not be opened.
        """
        if isinstance(filelike, (str, bytes, os.PathLike, int)):
            file_size = os.path.getsize(filelike)
            opened_file = open(filelike, 'rb')
        elif isinstance(filelike, io.IOBase):
            file_size = filelike.getbuffer().nbytes
            opened_file = filelike
        else:
            raise Exception('Unhandled filelike')

        range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)
        self.response.set_header('Accept-Ranges', 'bytes')
        if 'Range' in self.request.headers and range_re.match(self.request.headers['Range']):
            range_match = range_re.match(self.request.headers['Range'])
            first_byte, last_byte = range_match.groups()
            if int(first_byte) > file_size:
                # Return errors for out-of-bounds requests
                return self.HTTP(416)

            # If we encounter a range header, but the start/end is missing
            #  use default values that will give the entirety of the file
            #  e.g. 1092- will yield bytes 1092-<EOF>, and -1092 will yield
            #  bytes 0-1092.
            first_byte = int(first_byte) if first_byte else 0
            last_byte = int(last_byte) if last_byte else file_size - 1

            # Truncate bytes read to final byte
            if last_byte >= file_size:
                last_byte = file_size - 1

            length = last_byte - first_byte + 1
            self.response.set_header(
                'Content-Length',
                str(length)
            )
            self.response.set_header(
                'Content-Range',
                f'bytes {first_byte}-{last_byte}/{file_size}'
            )
            self.response.status_code = 206
            wrapper = RangeFileWrapper(opened_file, offset=first_byte, length=length)
            return wrapper
        else:
            self.response.set_header('Content-Length', str(file_size))
            self.response.status_code = 200
            wrapper = FileWrapper(opened_file)
            return wrapper
