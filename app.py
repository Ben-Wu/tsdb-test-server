from argparse import ArgumentParser

from flask import Flask, Response, request

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/print', methods=['POST'])
def print_request():
    print(request.get_data(as_text=True))
    return Response('{}', mimetype='application/json')


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', default=5000)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    app.run(host=args.host, port=args.port)
