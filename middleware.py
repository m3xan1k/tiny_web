from typing import Callable, Dict

from webob import Request, Response


class Middleware:
    def __init__(self, app: Callable) -> None:
        self.app = app

    def __call__(self, environ: Dict, start_response: Callable) -> Response:
        """Incapsulated entrypoint to app"""
        request = Request(environ)
        response = self.app.handle_request(request)
        return response(environ, start_response)

    def add(self, middleware_cls: object) -> None:
        self.app = middleware_cls(self.app)

    def handle_request(self, request: Request) -> Response:
        self.process_request(request)
        response: Response = self.app.handle_request(request)
        self.process_response(response)
        return response

    def process_request(self, request: Request) -> Request:
        pass

    def process_response(self, response: Response) -> Response:
        pass
