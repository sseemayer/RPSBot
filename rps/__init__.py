import numpy as np
import itertools

ALPHABET = 'rps'
POSSIBLE_EVENTS = list(itertools.product(ALPHABET, ALPHABET))

SCORES = {
    # you me    outcome
    ('r', 'r'): 0,
    ('r', 'p'): 1,
    ('r', 's'): -1,

    ('p', 'r'): -1,
    ('p', 'p'): 0,
    ('p', 's'): 1,

    ('s', 'r'): 1,
    ('s', 'p'): -1,
    ('s', 's'): 0
}


def count(seq, degree=0):
    """Compute the (possibly conditional) counts for fitting the markov chain.
    """
    assert degree >= 0

    n = len(POSSIBLE_EVENTS)
    out = np.zeros([n] * (degree + 1), dtype='uint32')

    if isinstance(seq, str):
        seq = [(e[0], e[1]) for e in seq.split(' ')]

    for event_and_history in zip(*(seq[i:] for i in range(degree + 1))):
        eahi = [POSSIBLE_EVENTS.index(e) for e in event_and_history]

        # TODO this can probably be done more elegantly
        o = out
        for i in eahi[:-1]:
            o = o[i]

        o[eahi[-1]] += 1

    return out


def p_marginal_pair(probs, pseudocounts=1):
    assert len(probs.shape) == 1
    assert probs.shape == (len(POSSIBLE_EVENTS), )

    out = np.empty((len(ALPHABET),))
    out[:] = pseudocounts

    for p, (y, m) in zip(probs, POSSIBLE_EVENTS):
        yi = ALPHABET.index(y)
        out[yi] += p

    return out / np.sum(out)


def best_strategy(marginal_probs):
    assert marginal_probs.shape == (len(ALPHABET), )

    outcomes = np.zeros((len(ALPHABET),))

    for im, m in enumerate(ALPHABET):
        outcomes[im] = sum((
            py * SCORES[(y, m)]
            for py, y in zip(marginal_probs, ALPHABET)
        ))

    i_best = np.argmax(outcomes)

    return ALPHABET[i_best], outcomes[i_best]
