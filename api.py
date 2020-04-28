from typing import Dict, Callable, Iterator

from webob import Request, Response


class Api:
    def __init__(self):
        self.routes = {}

    def __call__(self, environ: Dict, start_response: Callable) -> Iterator:
        request = Request(environ)
        response = self.handle_request(request)
        return response(environ, start_response)

    def handle_request(self, request: Request) -> Response:
        pass
        handler = self.routes.get(request.path)
        response = handler(request, Response())
        return response

    def route(self, path: str):
        def wrapper(handler):
            self.routes[path] = handler
        return wrapper
