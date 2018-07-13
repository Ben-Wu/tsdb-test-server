from argparse import ArgumentParser

import requests
import ujson as json
from flask import Flask, Response, request
from siggen.generator import SignatureGenerator

app = Flask(__name__)

generator = SignatureGenerator()


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/print', methods=['POST'])
def print_request():
    print(request.get_data(as_text=True))
    return Response('{}', mimetype='application/json')


@app.route('/sendToInflux', methods=['POST'])
def send_to_influx():
    data = json.loads(request.get_data(as_text=True))
    url = data['url']
    payload = data['payload']

    response = requests.post(url, payload)
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        print(e.message)
        print(payload)
        return Response(e.message, mimetype='text/plain')

    return Response("good", mimetype='text/plain')


@app.route('/symbols', methods=['POST'])
def get_symbols():
    payload = request.get_data()
    print('')
    try:
        response = requests.post('https://symbols.mozilla.org/symbolicate/v5', payload)
        response.raise_for_status()
        print('Good:')
        print(payload)
        #print('Response:')
        #print(response.text)
        print('Signature:')
        crash_data = response.json()
        symbolicated = {'crashing_thread': 0, 'threads': []}
        for frames in crash_data['results'][0]['stacks']:
            symbolicated['threads'].append({'frames': frames})
        try:
            print(generator.generate(symbolicated)['signature'])
        except KeyError:
            print('no signature')
        return Response(response.text, mimetype='application/json')
    except requests.HTTPError:
        print('Error:')
        print(payload)
        return Response('{}', mimetype='application/json')


@app.route('/symbols/<int:crashing_thread>', methods=['POST'])
def get_signature(crashing_thread):
    payload = request.get_data()
    print('')
    try:
        response = requests.post('https://symbols.mozilla.org/symbolicate/v5', payload)
        response.raise_for_status()
        print('Good:')
        print(payload)
        #print('Response:')
        #print(response.text)
        print('Signature:')
        crash_data = response.json()
        symbolicated = {'crashing_thread': crashing_thread, 'threads': []}
        for frames in crash_data['results'][0]['stacks']:
            symbolicated['threads'].append({'frames': frames})
        signature = generator.generate(symbolicated)['signature']
        print(signature)
        return Response(signature, mimetype='text/plain')
    except requests.HTTPError:
        print('Error:')
        print(payload)
        return Response('', mimetype='application/json')


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', default=5000)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    app.run(host=args.host, port=args.port)
