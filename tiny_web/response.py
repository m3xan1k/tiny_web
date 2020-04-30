from typing import Dict, Callable
import json

from webob import Response as WebobResponse


class Response:

    def __init__(self):
        self.json = None
        self.html = None
        self.text = None
        self.content_type = None
        self.body = b''
        self.status_code = 200

    def __call__(self, environ: Dict, start_response: Callable) -> WebobResponse:
        self.set_body_and_content_type()
        response = WebobResponse(body=self.body, status=self.status_code,
                                 content_type=self.content_type)
        return response(environ, start_response)

    def set_body_and_content_type(self):
        if self.json is not None:
            self.content_type = 'application/json'
            self.body: bytes = json.dumps(self.json).encode('utf-8')

        if self.html is not None:
            self.content_type = 'text/html'
            self.body: bytes = self.html.encode()

        if self.text is not None:
            self.content_type = 'text/plain'
            self.body = self.text
