# tiny_web
Python WSGI micro-framework to build api/site

![purpose](https://img.shields.io/badge/purpose-learning-green.svg)
![PyPI](https://img.shields.io/pypi/v/tiny_web)
[![Build Status](https://travis-ci.com/m3xan1k/tiny_web.svg?branch=master)](https://travis-ci.com/m3xan1k/tiny_web)
[![codecov](https://codecov.io/gh/m3xan1k/tiny_web/branch/master/graph/badge.svg)](https://codecov.io/gh/m3xan1k/tiny_web)



Demo toy-blog: http://tinyblog666.herokuapp.com/

Source code of toy-blog: https://github.com/m3xan1k/tiny_blog

## Installation

```shell
pip install tiny_web
```

## Quickstart

```python
from tiny_web.api import Api

app = Api()


# Basic route
@app.route("/home")
def home(request, response):
    response.text = "Hello from the HOME page"
    return response


# Parametrized route
@app.route("/hello/{name}")
def greeting(request, response, name):
    response.text = f"Hello, {name}"
    return response


'''
Class based controller.
Class methods are handlers for http request methods
'''
@app.route("/book")
class BooksResource:
    def get(self, req, resp):
        resp.text = "Books Page"
        return response

    def post(self, req, resp):
        resp.text = "Endpoint to create a book"
        return response


'''
You can response with templates.
Templates may be served in "templates" folder.
Jinja2 used as a template engine.
'''
@app.route("/template")
def template_handler(req, resp):
    resp.body = app.template(
        "index.html", context={"name": "Bumbo", "title": "Best Framework"}).encode()
    return response


'''
You also can use query string parameters.
"tiny_web" uses "webob" library to wrap requests and responses.
So if query looks like "/users?name=john" you can handle params like this.
See more on https://docs.pylonsproject.org/projects/webob/en/stable/reference.html
'''
@app.route("/users")
def users(request, response):
    name = request.GET.get("name")
    response.html = f"Hello {name}"
    return response


'''
You may use helpers for html or json
'''
@app.route("/users")
def users(request, response):
    response.html = app.template("users.html")
    return response


@app.route("/items")
def users(request, response):
    items = [{'id': 1, 'name': 'item_1'}, {'id': 2, 'name': 'item_2'}]
    response.json = {'items': items}
    return response
```

### Unit Tests

The recommended way of writing unit tests is with [pytest](https://docs.pytest.org/en/latest/). There are two built in fixtures
that you may want to use when writing unit tests with Bumbo. The first one is `app` which is an instance of the main `API` class:

```python
def test_route_overlap_throws_exception(app):
    @app.route("/")
    def home(req, resp):
        resp.text = "Welcome Home."

    with pytest.raises(AssertionError):
        @app.route("/")
        def home2(req, resp):
            resp.text = "Welcome Home2."
```

The other one is `client` that you can use to send HTTP requests to your handlers. It is based on the famous [requests](http://docs.python-requests.org/en/master/) and it should feel very familiar:

```python
def test_parameterized_route(app, client):
    @app.route("/{name}")
    def hello(req, resp, name):
        resp.text = f"hey {name}"

    assert client.get("http://testserver/john").text == "hey john"
```

## Templates

The default folder for templates is `templates`. You can change it when initializing the main `Api()` class:

```python
app = Api(templates_dir="templates_dir_name")
```

Then you can use HTML files in that folder like so in a handler:

```python
@app.route("/show/template")
def handler_with_template(req, resp):
    resp.html = app.template(
        "example.html", context={"title": "Hello", "body": "World!"})
```

## Static Files

Just like templates, the default folder for static files is `static` and you can override it:

```python
app = Api(static_dir="static_dir_name")
```

Then you can use the files inside this folder in HTML files:

```html
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <title>{{title}}</title>

  <link href="/static/main.css" rel="stylesheet" type="text/css">
</head>

<body>
    <h1>{{body}}</h1>
    <p>This is a paragraph</p>
</body>
</html>
```

Also you may want use custom 404 page, just make '404.html' in the root of templates folder.

### Middleware

You can create custom middleware classes by inheriting from the `tiny_web.middleware.Middleware` class and overriding its two methods
that are called before and after each request:

```python
from tiny_web.api import Api
from tiny_web.middleware import Middleware


app = Api()


class SimpleCustomMiddleware(Middleware):
    def process_request(self, req):
        print("Before dispatch", req.url)

    def process_response(self, req, res):
        print("After dispatch", req.url)


app.add_middleware(SimpleCustomMiddleware)
```


TODO:
- [x] Templates
- [x] Exceptions
- [x] Static files
- [x] Middlewares
- [x] Documentation
- [x] Build package
- [x] Dockerize and deploy demo
