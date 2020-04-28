from typing import Dict, Callable, Tuple, Optional

from webob import Request, Response
from parse import parse


class Api:
    def __init__(self):
        self.routes = {}

    def __call__(self, environ: Dict, start_response: Callable) -> Response:
        """Interface to interact with WSGI"""
        request = Request(environ)
        response = self.handle_request(request)
        return response(environ, start_response)

    def handle_request(self, request: Request) -> Response:
        """Sends request to handler and returns generated response"""
        response = Response()
        handler, parsed_params = self.find_handler(request)
        if handler:
            return handler(request, response, **parsed_params)
        return self.not_found(response)

    def find_handler(self, request: Request) -> Optional[Tuple[Callable, Dict]]:
        """Check if requested path in routes dict and return callback"""
        for path, handler in self.routes.items():
            parsed_params = parse(path, request.path)
            if parsed_params:
                return handler, parsed_params.named
        return None, None

    def route(self, path: str) -> Callable:
        """Decorator for check route duplicates and add to routes dict"""
        assert self.routes.get(path) is None, f'{path} route already exists'

        def wrapper(handler):
            self.routes[path] = handler
        return wrapper

    def not_found(self, response: Response) -> Response:
        """Handler for not existed request paths"""
        response.status_code = 404
        response.text = '<h1>Page not found</h1>'
        return response
