from argparse import ArgumentParser

from flask import Flask, Response, request
import requests

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/print', methods=['POST'])
def print_request():
    print(request.get_data(as_text=True))
    return Response('{}', mimetype='application/json')


@app.route('/symbols', methods=['POST'])
def get_symbols():
    payload = request.get_data()
    print('')
    try:
        response = requests.post('https://symbols.mozilla.org/symbolicate/v5', payload)
        response.raise_for_status()
        print('Good:')
        print(payload)
        return Response(response.text, mimetype='application/json')
    except requests.HTTPError:
        print('Error:')
        print(payload)
        return Response('{}', mimetype='application/json')


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', default=5000)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    app.run(host=args.host, port=args.port)
