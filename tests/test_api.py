import pytest

from tests.conftest import api, client
from tiny_web.api import Api
from tiny_web.middleware import Middleware


TEST_URL = 'http://testserver'


def test_func_route_create(api):
    @api.route('/home')
    def home(request, response):
        response.text = 'home'
        return response


def test_duplicate_route(api):
    @api.route('/home')
    def home(request, response):
        response.text = 'home'
        return response

    with pytest.raises(AssertionError):
        @api.route('/home')
        def home2(request, response):
            response.text = 'home'
            return response


def test_api_test_client_works(api, client):
    response_text = 'works'

    @api.route('/foo')
    def foo(request, response):
        response.text = response_text
        return response

    assert client.get(TEST_URL + '/foo').text == response_text


def test_parametrized_route(api, client):
    @api.route('/posts/{id}')
    def posts(request, response, id):
        response.text = f'post {id}'
        return response

    assert client.get(TEST_URL + '/posts/1').status_code == 200
    assert client.get(TEST_URL + '/posts/1').text == 'post 1'
    assert client.get(TEST_URL + '/posts/33').text == 'post 33'


def test_404(client):
    response = client.get(TEST_URL)

    assert response.status_code == 404
    assert response.text == '<h1>Page not found</h1>'


def test_class_based_view_get(api, client):
    @api.route('/posts')
    class PostsView:
        def get(self, request, response):
            id = request.GET.get('id')
            if id is None:
                response.text = 'posts'
            else:
                response.text = f'post {id}'
            return response

    assert client.get(TEST_URL + '/posts').text == 'posts'
    assert client.get(TEST_URL + '/posts?id=5').text == 'post 5'


def test_class_based_view_post(api, client):
    @api.route('/posts')
    class PostsView:
        def post(self, request, response):
            response.text = 'post created'
            return response

        def put(self, request, response):
            id = request.GET.get('id')
            response.text = f'post {id} updated'
            return response

        def delete(self, request, response):
            id = request.GET.get('id')
            response.text = f'post {id} deleted'
            return response

    assert client.post(TEST_URL + '/posts').text == 'post created'
    assert client.put(TEST_URL + '/posts?id=6').text == 'post 6 updated'
    assert client.delete(TEST_URL + '/posts?id=7').text == 'post 7 deleted'

    with pytest.raises(AttributeError):
        client.patch(TEST_URL + '/posts?id=1')


def test_alternative_add_route(api, client):
    def home(request, response):
        response.text = 'alternative'
        return response

    api.add_route('/home', home)

    assert client.get(TEST_URL + '/home').status_code == 200


def test_templates(api, client):

    title = 'Microframework'
    name = 'tiny-web'

    @api.route('/')
    def home(request, response):
        context = {
            'title': title,
            'name': name,
        }
        response.body = api.template('index.html', context)
        return response

    response = client.get(TEST_URL + '/')

    assert 'text/html' in response.headers['Content-Type']
    assert title in response.text
    assert name in response.text


def test_exception_handler(api, client):
    def on_exception(request, response, exception_class):
        response.text = 'Attribute error'
        return response

    api.add_custom_exception_handler(on_exception)

    @api.route('/')
    def home(request, response):
        raise AttributeError()

    response = client.get(TEST_URL + '/')

    assert response.text == 'Attribute error'


FILE_DIR = 'css'
FILE_NAME = 'main.css'
FILE_CONTENTS = 'body {background-color: red}'


def test_404_static_file(client):
    assert client.get(TEST_URL + '/static/main.css').status_code == 404


def _create_static(static_dir):
    asset = static_dir.mkdir(FILE_DIR).join(FILE_NAME)
    asset.write(FILE_CONTENTS)
    return asset


def test_static_is_served(tmpdir_factory):
    static_dir = tmpdir_factory.mktemp('static')
    _create_static(static_dir)
    api = Api(static_dir=str(static_dir))
    client = api.test_session()

    response = client.get(TEST_URL + f'/static/{FILE_DIR}/{FILE_NAME}')

    assert response.status_code == 200
    assert response.text == FILE_CONTENTS


def test_middleware_methods_are_called(api, client):
    process_request_called = False
    process_response_called = False

    class CallMiddlewareMethods(Middleware):
        def __init__(self, app):
            super().__init__(app)

        def process_request(self, request):
            nonlocal process_request_called
            process_request_called = True

        def process_response(self, response):
            nonlocal process_response_called
            process_response_called = True

    api.add_middleware(CallMiddlewareMethods)

    @api.route('/')
    def home(request, response):
        response.text = 'hello'
        return response

    client.get(TEST_URL + '/')

    assert process_request_called is True
    assert process_response_called is True


def test_allowed_method_for_func_based_views(api, client):

    @api.route('/', allowed_methods=['get', 'post'])
    def home(request, response):
        response.text = 'hello'
        return response

    assert client.get(TEST_URL + '/').status_code == 200
    assert client.post(TEST_URL + '/').status_code == 200

    with pytest.raises(AttributeError):
        client.delete(TEST_URL + '/')


def test_json_response(api, client):
    @api.route('/json')
    def json_handler(request, response):
        response.json = {'message': 'hello'}
        return response

    response = client.get(TEST_URL + '/json')

    assert response.headers['Content-Type'] == 'application/json'
    assert response.json()['message'] == 'hello'


def test_html_response(api, client):
    @api.route('/html')
    def html_handler(request, response):
        response.html = '<h1>Hello</h1>'
        return response

    response = client.get(TEST_URL + '/html')

    assert response.headers['Content-Type'] == 'text/html; charset=UTF-8'
    assert response.text == '<h1>Hello</h1>'


def test_plain_response(api, client):
    @api.route('/text')
    def text_handler(request, response):
        response.text = 'hello'
        return response

    response = client.get(TEST_URL + '/text')

    assert response.headers['Content-Type'] == 'text/plain; charset=UTF-8'
    assert response.text == 'hello'
