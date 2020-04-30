from typing import Dict, Callable, Tuple, Optional, List
import inspect
import os
from jinja2 import Environment, FileSystemLoader

from webob import Request
from parse import parse
from requests import Session
from wsgiadapter import WSGIAdapter
from whitenoise import WhiteNoise

from tiny_web.middleware import Middleware
from tiny_web.response import Response


class Api:
    def __init__(self, templates_dir: str = 'templates', static_dir: str = 'static'):
        self.routes = {}
        self.templates = Environment(
            loader=FileSystemLoader(os.path.abspath(templates_dir))
        )
        self.exception_handler = None
        self.whitenoise = WhiteNoise(self.wsgi_app, root=static_dir)
        self.middleware = Middleware(self)

    def __call__(self, environ: Dict, start_response: Callable) -> Response:
        """Interface to interact with WSGI"""
        path: str = environ['PATH_INFO']

        '''Check if static files request then call whitenoise'''
        if path.startswith('/static'):
            environ['PATH_INFO'] = path[len('/static'):]
            return self.whitenoise(environ, start_response)

        return self.middleware(environ, start_response)

    def wsgi_app(self, environ: Dict, start_response: Callable) -> Response:
        """Incapsulated entrypoint to app"""
        request = Request(environ)
        response = self.handle_request(request)
        return response(environ, start_response)

    def handle_request(self, request: Request) -> Response:
        """Sends request to handler and returns generated response"""
        response = Response()
        handler_data, kwargs = self.find_handler(request)
        try:
            if handler_data:
                handler = handler_data['handler']
                allowed_methods = handler_data['allowed_methods']
                if inspect.isclass(handler):
                    handler = self.find_class_method(request, handler)
                else:
                    if not request.method.lower() in set(allowed_methods):
                        raise AttributeError('Method not allowed', request.method.lower())
                return handler(request, response, **kwargs)
            return self.not_found(response)
        except Exception as e:
            if self.exception_handler is None:
                raise e
            return self.exception_handler(request, response, e)

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

    def route(self, path: str, allowed_methods: Optional[List] = None) -> Callable:
        """Decorator for check route duplicates and add to routes dict"""
        def wrapper(handler):
            self.add_route(path, handler, allowed_methods)
        return wrapper

    def add_route(self, path: str, handler: Callable,
                  allowed_methods: Optional[List] = None) -> None:
        """Another style for route register"""
        assert self.routes.get(path) is None, f'{path} route already exists'
        if allowed_methods is None:
            allowed_methods = ['get', 'post', 'put', 'delete', 'patch', 'options']
        self.routes[path] = {'handler': handler, 'allowed_methods': allowed_methods}
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
        html = self.templates.get_template(template).render(**context)
        return html

    def add_custom_exception_handler(self, exception_handler: Callable) -> None:
        self.exception_handler = exception_handler

    def add_middleware(self, middleware: Middleware) -> None:
        self.middleware.add(middleware)
