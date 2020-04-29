import pytest

from tests.conftest import api, client


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
