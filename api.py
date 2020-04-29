from typing import Dict, Callable, Tuple, Optional
import inspect
import os
from jinja2 import Environment, FileSystemLoader

from webob import Request, Response
from parse import parse
from requests import Session
from wsgiadapter import WSGIAdapter


class Api:
    def __init__(self, templates_dir: str = 'templates'):
        self.routes = {}
        self.templates = Environment(
            loader=FileSystemLoader(os.path.abspath(templates_dir))
        )

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
            if inspect.isclass(handler):
                handler = self.find_class_method(request, handler)
            return handler(request, response, **parsed_params)
        return self.not_found(response)

    def find_handler(self, request: Request) -> Optional[Tuple[Callable, Dict]]:
        """Check if requested path in routes dict and return callback"""
        for path, handler in self.routes.items():
            parsed_params = parse(path, request.path)
            if parsed_params:
                return handler, parsed_params.named
        return None, None

    def find_class_method(self, request: Request, handler: object) -> Callable:
        """Find handler for class-based view depending on request method"""
        http_verb = request.method.lower()
        method = getattr(handler(), http_verb, None)
        if method is None:
            raise AttributeError('Method not allowed', request.method)
        return method

    def route(self, path: str) -> Callable:
        """Decorator for check route duplicates and add to routes dict"""
        def wrapper(handler):
            self.add_route(path, handler)
        return wrapper

    def add_route(self, path: str, handler: Callable) -> None:
        """Another style for route register"""
        assert self.routes.get(path) is None, f'{path} route already exists'
        self.routes[path] = handler
        return None

    def not_found(self, response: Response) -> Response:
        """Handler for not existed request paths"""
        response.status_code = 404
        response.text = '<h1>Page not found</h1>'
        return response

    def test_session(self, base_url='http://testserver'):
        """Test environment"""
        session = Session()
        session.mount(prefix=base_url, adapter=WSGIAdapter(self))
        return session

    def template(self, template: str, context: Optional[Dict] = None) -> bytes:
        if context is None:
            context = {}
        html_bytes = self.templates.get_template(template).render(**context).encode()
        return html_bytes
