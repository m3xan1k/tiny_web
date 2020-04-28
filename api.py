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
        response = Response()
        handler = self.routes.get(request.path)
        if handler:
            return handler(request, response)
        return self.not_found(response)

    def route(self, path: str):
        def wrapper(handler):
            self.routes[path] = handler
        return wrapper

    def not_found(self, response):
        response.status_code = 404
        response.text = '<h1>Page not found</h1>'
        return response
