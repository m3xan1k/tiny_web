from typing import Dict, Callable

from webob import Request, Response
from parse import parse


class Api:
    def __init__(self):
        self.routes = {}

    def __call__(self, environ: Dict, start_response: Callable) -> Response:
        request = Request(environ)
        response = self.handle_request(request)
        return response(environ, start_response)

    def handle_request(self, request: Request) -> Response:
        response = Response()
        handler, parsed_params = self.find_handler(request)
        if handler:
            return handler(request, response, **parsed_params)
        return self.not_found(response)

    def find_handler(self, request: Request):
        for path, handler in self.routes.items():
            parsed_params = parse(path, request.path)
            if parsed_params:
                return handler, parsed_params.named
        return None, None

    def route(self, path: str):
        def wrapper(handler):
            self.routes[path] = handler
        return wrapper

    def not_found(self, response):
        response.status_code = 404
        response.text = '<h1>Page not found</h1>'
        return response
