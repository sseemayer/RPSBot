#!/usr/bin/env python
import numpy as np

from flask import Flask, session, request, jsonify
from flask_cors import CORS

import rps
import pickle
import random

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = 'opwjdpwqhjfipqgf0q3gh9076'


def get_counts():

    counts = session.get('counts')

    if counts is None:
        n_ev = len(rps.POSSIBLE_EVENTS)
        counts = np.zeros((n_ev, n_ev), dtype='uint64')

    else:
        counts = pickle.loads(counts)

    return counts


def set_counts(counts):
    session['counts'] = pickle.dumps(counts, protocol=pickle.HIGHEST_PROTOCOL)


@app.route('/api/reset', methods=['POST'])
def reset_session():
    """Reset the counts currently stored in the user session"""

    session.clear()

    return "200 OK"


@app.route('/api/event', methods=['POST'])
def log_event():

    current_event = request.form.get('event')
    if not current_event:
        raise Exception('Missing required parameter "event"!')

    current_event = tuple(*current_event.split())
    if current_event not in rps.POSSIBLE_EVENTS:
        raise Exception('Invalid event!')

    last_event = session.get('last_event')

    if last_event is not None:
        counts = get_counts()
        counts += rps.count([last_event, current_event], degree=1)
        set_counts(counts)

        print(counts)

    session['last_event'] = current_event

    return "200 OK"


@app.route('/api/counts')
def show_counts():
    counts = get_counts()

    return jsonify({
        ''.join(ctx): {
            ''.join(ev): float(counts[ic, ie])
            for ie, ev in enumerate(rps.POSSIBLE_EVENTS)
        }
        for ic, ctx in enumerate(rps.POSSIBLE_EVENTS)
    })


@app.route('/api/predict')
def predict():
    last_event = session.get('last_event')
    counts = get_counts()

    if last_event is not None:
        lei = rps.POSSIBLE_EVENTS.index(last_event)
        p_1 = rps.p_marginal_pair(counts[lei, :])

        best_strategy, exp = rps.best_strategy(p_1)
    else:
        p_1 = np.empty((len(rps.ALPHABET),))
        p_1[:] = 1. / 3
        best_strategy, exp = random.choice('rps'), 0

    return jsonify({
        'best_strategy': best_strategy,
        'expected_outcome': exp,
        'predicted_plays': dict(zip(rps.ALPHABET, p_1)),
    })


if __name__ == "__main__":
    app.run(debug=True)
