"""Reproducible, compiled Monte Carlo replication of stats.py's nine-bot model."""
import argparse
import csv
import json
import platform
import time
from pathlib import Path

import numpy as np
import numba
from numba import njit, prange

NAMES = ['Random', 'Cooperator', 'Cheater', 'Copycat', 'Copykitten',
         'Copy3kitten', 'NegtiveCopycat', 'NegtiveCopykitten', 'Grudger']


def make_seeds(seed, length, error_index, error_points, samples, seen=None):
    key = [seed, length, error_index, error_points]
    seeds = np.random.SeedSequence(key).generate_state(samples)
    if seen is None:
        seen = set()
    for i in range(samples):
        attempt = 0
        while int(seeds[i]) in seen:
            attempt += 1
            seeds[i] = np.random.SeedSequence(key + [i, attempt]).generate_state(1)[0]
        seen.add(int(seeds[i]))
    return seeds


@njit(cache=True)
def action(kind, last, betrayals, cooperations, ever):
    # 1 = cooperate; counters describe the opponent's realized moves.
    if kind == 0:
        return int(np.random.random() < 0.5)
    if kind == 1:
        return 1
    if kind == 2:
        return 0
    if kind == 3:
        return 1 if last == -1 else last
    if kind == 4:
        return int(betrayals < 2)
    if kind == 5:
        return int(betrayals < 3)
    if kind == 6:
        return 0 if last == -1 else last
    if kind == 7:
        return int(cooperations >= 2)
    return int(not ever)


@njit(cache=True)
def play(a, b, length, error):
    la = lb = -1
    da = db = ca = cb = 0
    ea = eb = False
    sa = sb = 0
    for _ in range(np.random.poisson(length)):
        x = action(a, la, da, ca, ea)
        y = action(b, lb, db, cb, eb)
        # Preserve randint(0, 100) < error_rate * 100 from stats.py.
        if x and np.random.randint(0, 101) < error * 100:
            x = 0
        if y and np.random.randint(0, 101) < error * 100:
            y = 0
        sa += 3 * y - x
        sb += 3 * x - y
        la, lb = y, x
        da, db = (da + 1 if not y else 0), (db + 1 if not x else 0)
        ca, cb = (ca + 1 if y else 0), (cb + 1 if x else 0)
        ea, eb = ea or not y, eb or not x
    return sa, sb


@njit(cache=True)
def replicate(length, error, generations, seed):
    np.random.seed(seed)
    population = np.repeat(np.arange(9), 4)
    for _ in range(generations):
        scores = np.zeros(36, dtype=np.int64)
        for i in range(36):
            for j in range(i + 1, 36):
                a, b = play(population[i], population[j], length, error)
                scores[i] += a
                scores[j] += b
        # Python's original sort is stable: ties keep population order.
        order = np.argsort(-scores, kind='mergesort')
        ranked = population[order]
        population[:33] = ranked[:33]
        population[33:] = ranked[:3]
    counts = np.zeros(9, dtype=np.int64)
    for kind in population:
        counts[kind] += 1
    return counts


@njit(cache=True, parallel=True)
def sample(length, error, generations, seeds):
    counts = np.empty((len(seeds), 9), dtype=np.int64)
    for i in prange(len(seeds)):
        counts[i] = replicate(length, error, generations, seeds[i])
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--samples', type=int, default=1000)
    parser.add_argument('--lengths', type=int, nargs='+', default=list(range(1, 11)) + [100])
    parser.add_argument('--error-points', type=int, default=21)
    parser.add_argument('--generations', type=int, default=100)
    parser.add_argument('--seed', type=int, default=20260920)
    parser.add_argument('--threads', type=int, default=8)
    parser.add_argument('--output', type=Path, default=Path('results/high_sample'))
    parser.add_argument('--resume', action='store_true', help='Reuse cells with matching parameters and seeds')
    args = parser.parse_args()
    if args.samples < 2 or args.error_points < 2 or args.generations < 0 or min(args.lengths) < 0:
        parser.error('Need samples >= 2, error-points >= 2, and nonnegative lengths/generations')
    numba.set_num_threads(args.threads)
    args.output.mkdir(parents=True, exist_ok=True)
    metadata = {k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()}
    previous_elapsed = 0
    saved_rates = {}
    if args.resume and (args.output / 'metadata.json').exists():
        previous = json.loads((args.output / 'metadata.json').read_text())
        for key in ('samples', 'lengths', 'error_points', 'generations', 'seed'):
            if previous[key] != metadata[key]:
                parser.error(f'Cannot resume: {key} differs from saved metadata')
        previous_elapsed = previous.get('elapsed_seconds', 0)
        if (args.output / 'summary.csv').exists():
            with (args.output / 'summary.csv').open() as handle:
                for row in csv.DictReader(handle):
                    index = round(float(row['error_rate']) * 2 * (args.error_points - 1))
                    saved_rates[(int(row['length']), index)] = float(row['error_rate'])
    metadata.update(python=platform.python_version(), numpy=np.__version__, numba=numba.__version__,
                    strategies=NAMES, population=36, elimination=3,
                    error_model='cooperation-only; randint(0,100) < 100 * nominal_error',
                    uncertainty='pointwise normal 95% Monte Carlo CI of mean final population share')
    (args.output / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    rows = []
    used_seeds = set()
    start = time.perf_counter()
    for length in args.lengths:
        for error_index, error in enumerate(np.round(np.linspace(0, 0.5, args.error_points), 12)):
            # Independent streams for cells and replicates; unaffected by thread scheduling.
            seeds = make_seeds(args.seed, length, error_index, args.error_points, args.samples, used_seeds)
            path = args.output / f'runs_n{length}_e{error_index:02d}.npz'
            counts = None
            if args.resume and path.exists():
                with np.load(path) as saved:
                    if saved_rates.get((length, error_index)) == error and saved['seeds'].shape == seeds.shape:
                        candidate = saved['counts']
                        if candidate.shape == (args.samples, 9) and (candidate >= 0).all() and (candidate.sum(axis=1) == 36).all():
                            counts = candidate
                            changed = saved['seeds'] != seeds
                            if changed.any():
                                counts[changed] = sample(length, error, args.generations, seeds[changed])
                if counts is not None and changed.any():
                    np.savez_compressed(path, counts=counts, seeds=seeds)
            if counts is None:
                counts = sample(length, error, args.generations, seeds)
                np.savez_compressed(path, counts=counts, seeds=seeds)
            shares = counts / 36
            means = shares.mean(axis=0)
            ses = shares.std(axis=0, ddof=1) / np.sqrt(args.samples)
            for k, name in enumerate(NAMES):
                rows.append(dict(length=length, error_rate=error, strategy=name, samples=args.samples,
                                 mean_share=means[k], standard_error=ses[k],
                                 ci95_low=max(0, means[k] - 1.96 * ses[k]),
                                 ci95_high=min(1, means[k] + 1.96 * ses[k]),
                                 first30_mean_share=shares[:30, k].mean()))
            # Save each completed cell, so interrupted runs retain their results.
            with (args.output / 'summary.csv').open('w', newline='') as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
            print(f'n={length:3} error={error:.3f}: {args.samples} runs; elapsed {time.perf_counter()-start:.1f}s', flush=True)
    metadata['elapsed_seconds'] = previous_elapsed + time.perf_counter() - start
    (args.output / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')


if __name__ == '__main__':
    main()
