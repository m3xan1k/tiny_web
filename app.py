from webob import Request, Response

from api import Api


app = Api()


@app.route('/')
def home(request: Request, response: Response) -> Response:
    response.text = '<h1>Home</h1>'
    return response


@app.route('/about')
def about(request, response) -> Response:
    response.text = '<h1>About</h1>'
    return response
