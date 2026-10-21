"""Independent algebra checks for the optimization literature review.

Uses only the standard library. This is not a hardware implementation or an
ISA/noise benchmark. It checks all computational-basis columns, including
complex phases, for the listed small instances; linearity then covers arbitrary
inputs (including inputs entangled with a reference).

Run: python3 research/verify_candidate_identities.py
"""

import json
import math


def one(state, q, matrix):
    out = state.copy()
    bit = 1 << q
    for i in range(len(state)):
        if not i & bit:
            a, b = state[i], state[i | bit]
            out[i] = matrix[0][0] * a + matrix[0][1] * b
            out[i | bit] = matrix[1][0] * a + matrix[1][1] * b
    return out


H = ((2**-0.5, 2**-0.5), (2**-0.5, -2**-0.5))
S = ((1, 0), (0, 1j))
SDG = ((1, 0), (0, -1j))
Z = ((1, 0), (0, -1))


def cz(state, a, b):
    return [-v if (i >> a) & (i >> b) & 1 else v
            for i, v in enumerate(state)]


def cx(state, a, b):
    out = [0j] * len(state)
    for i, v in enumerate(state):
        out[i ^ (1 << b) if (i >> a) & 1 else i] = v
    return out


def pauli(state, label):
    out = [0j] * len(state)
    for i, v in enumerate(state):
        j, phase = i, 1
        for q, p in enumerate(reversed(label)):
            bit = (i >> q) & 1
            if p in "XY":
                j ^= 1 << q
            if p == "Y":
                phase *= -1j if bit else 1j
            elif p == "Z" and bit:
                phase *= -1
        out[j] += phase * v
    return out


def rotate(state, label, theta):
    return [math.cos(theta) * a - 1j * math.sin(theta) * b
            for a, b in zip(state, pauli(state, label))]


def deviation(a, b):
    return max(abs(x - y) for x, y in zip(a, b))


def basis(n, k):
    return [complex(i == k) for i in range(1 << n)]


def star_branch(label, theta, column, outcome):
    n = len(label)
    state = basis(n + 1, column)
    support = [(q, p) for q, p in enumerate(reversed(label)) if p != "I"]
    for q, p in support:
        if p == "Y":
            state = one(state, q, SDG)
        if p in "XY":
            state = one(state, q, H)
    state = one(state, n, H)
    for q, _ in support:
        state = cz(state, q, n)
    c, s = math.cos(theta), -1j * math.sin(theta)
    state = one(state, n, ((c, s), (s, c)))  # Rx(2 theta)
    state = state[outcome * (1 << n):(outcome + 1) * (1 << n)]
    for q, p in support:
        if outcome:
            state = one(state, q, Z)
        if p in "XY":
            state = one(state, q, H)
        if p == "Y":
            state = one(state, q, S)
    return state


def check_star():
    labels = ("Z", "X", "Y", "ZZ", "XY", "YY", "ZZZ", "XYZ",
              "YIX", "ZZZZ", "YXIZ", "XZZX", "XYZXY", "ZIXIY")
    angles = (-0.7, 0, 0.173, 0.4, math.pi / 8, math.pi / 4, math.pi / 2)
    worst, count = 0.0, 0
    for label in labels:
        for theta in angles:
            for column in range(1 << len(label)):
                expected = [v / math.sqrt(2)
                            for v in rotate(basis(len(label), column), label, theta)]
                for outcome in (0, 1):
                    worst = max(worst, deviation(
                        star_branch(label, theta, column, outcome), expected))
                    count += 1
    return dict(branch_column_checks=count, max_amplitude_error=worst)


def check_compressed_blocks():
    worst, count = 0.0, 0
    for n in range(2, 9):
        for block_size in range(1, n + 1):
            groups = [list(range(i, min(n, i + block_size)))
                      for i in range(0, n, block_size)]
            edges = [(a, b) for g in groups for a, b in zip(g, g[1:])]
            roots = {g[-1] for g in groups}
            label = "".join("Z" if q in roots else "I" for q in reversed(range(n)))
            for theta in (-0.37, 0.4):
                for column in range(1 << n):
                    state = basis(n, column)
                    expected = rotate(state, "Z" * n, theta)
                    for a, b in edges:
                        state = cx(state, a, b)
                    state = rotate(state, label, theta)
                    for a, b in reversed(edges):
                        state = cx(state, a, b)
                    worst = max(worst, deviation(state, expected))
                    count += 1
    return dict(column_checks=count, max_amplitude_error=worst,
                limitation="Inner root rotation is ideal; routing and dynamic implementation are not tested.")


def check_shared_pair():
    worst, count = 0.0, 0
    for alpha, beta in ((0.4, 0.4), (-0.17, 0.63), (math.pi / 8, -0.29)):
        for column in range(32):
            state = basis(5, column)
            expected = rotate(rotate(state, "XZZZX", alpha), "YZZZY", beta)
            for q in (1, 2, 3):
                state = cz(state, 0, q)
            state = rotate(rotate(state, "XIIIX", alpha), "YIIIY", beta)
            for q in (1, 2, 3):
                state = cz(state, 0, q)
            worst = max(worst, deviation(state, expected))
            count += 1
    return dict(column_checks=count, max_amplitude_error=worst,
                limitation="The two-qubit core is exact here; a native KAK decomposition is not tested.")


def check_phase_diagnostic():
    n, theta = 5, 0.4
    state = rotate(basis(n, 0), "X" * n, theta)
    negative = rotate(basis(n, 0), "X" * n, -theta)
    def expectation(s):
        return sum(a.conjugate() * b for a, b in zip(s, pauli(s, "XXXXY"))).real
    return dict(probability_difference=max(abs(abs(a)**2 - abs(b)**2)
                                          for a, b in zip(state, negative)),
                positive_angle_yxxxx=expectation(state),
                negative_angle_yxxxx=expectation(negative),
                predicted_positive=-math.sin(2 * theta))


def main():
    result = dict(star=check_star(), compressed_blocks=check_compressed_blocks(),
                  shared_pair=check_shared_pair(), phase_diagnostic=check_phase_diagnostic())
    assert all(result[k]["max_amplitude_error"] < 1e-12
               for k in ("star", "compressed_blocks", "shared_pair"))
    phase = result["phase_diagnostic"]
    assert phase["probability_difference"] < 1e-12
    assert abs(phase["positive_angle_yxxxx"] - phase["predicted_positive"]) < 1e-12
    result["status"] = "passed"
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
