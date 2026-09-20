import itertools
import unittest
from unittest.mock import patch

import numpy as np
import numba
import bots
import experiments as ex
import stats


class SimulationTests(unittest.TestCase):
    def test_seed_collision_repair(self):
        # This particular cell had a duplicate in the raw SeedSequence output.
        seeds = ex.make_seeds(20260920, 2, 14, 21, 1000)
        self.assertEqual(len(np.unique(seeds)), 1000)
        np.testing.assert_array_equal(seeds, ex.make_seeds(20260920, 2, 14, 21, 1000))
        shared = set()
        a = ex.make_seeds(1, 7, 1, 21, 20, shared)
        b = ex.make_seeds(1, 7, 1, 21, 20, shared)
        self.assertEqual(len(set(a) & set(b)), 0)

    def test_all_strategy_histories(self):
        for kind, name in enumerate(ex.NAMES):
            if name == 'Random':
                continue
            for size in range(7):
                for history in itertools.product('CN', repeat=size):
                    bot = getattr(bots, name)()
                    bot.history = list(history)
                    trailing_n = len(history) - len(''.join(history).rstrip('N'))
                    trailing_c = len(history) - len(''.join(history).rstrip('C'))
                    result = ex.action(kind, -1 if not history else int(history[-1] == 'C'),
                                       trailing_n, trailing_c, 'N' in history)
                    self.assertEqual(result, int(bot.move() == 'C'), (name, history))

    def test_matches_against_original(self):
        # Feed identical random draws through the readable (non-JIT) fast engine
        # and the original engine, including random strategy and rounding edges.
        for error in (0, 0.025, 0.05, 0.5, 1):
            for a, b in itertools.product(range(9), repeat=2):
                def run(original):
                    rng = np.random.RandomState(123)
                    with patch('numpy.random.poisson', side_effect=lambda n: rng.poisson(n)), \
                         patch('numpy.random.randint', side_effect=lambda low, high: rng.randint(low, high)), \
                         patch('numpy.random.random', side_effect=rng.random_sample), \
                         patch('stats.randint', side_effect=lambda low, high: rng.randint(low, high + 1)), \
                         patch('bots.choice', side_effect=lambda _: 'C' if rng.random_sample() < 0.5 else 'N'), \
                         patch('experiments.action', ex.action.py_func):
                        if original:
                            return stats.match(getattr(bots, ex.NAMES[a])(), getattr(bots, ex.NAMES[b])(), error, 15)
                        return ex.play.py_func(a, b, 15, error)
                self.assertEqual(run(True), run(False), (a, b, error))

    def test_population_and_reproducibility(self):
        seeds = np.arange(12, dtype=np.uint32)
        a = ex.sample(7, 0.125, 100, seeds)
        np.testing.assert_array_equal(a.sum(axis=1), 36)
        self.assertTrue((a >= 0).all())
        np.testing.assert_array_equal(a, ex.sample(7, 0.125, 100, seeds))
        threads = numba.get_num_threads()
        try:
            numba.set_num_threads(1)
            np.testing.assert_array_equal(a, ex.sample(7, 0.125, 100, seeds))
        finally:
            numba.set_num_threads(threads)
        np.testing.assert_array_equal(ex.replicate(7, 0.1, 0, 1), np.full(9, 4))

    def test_stable_ties_match_original(self):
        # Zero rounds means all scores tie, exercising stable selection ordering.
        initial = {name: 4 for name in ex.NAMES}
        expected = stats.simulate_evolution(initial, n=0, elim=3, generations=10)
        actual = ex.replicate(0, 0, 10, 1)
        np.testing.assert_array_equal(actual, [expected.get(name, 0) for name in ex.NAMES])


if __name__ == '__main__':
    unittest.main()
