"""Limited checks for the HW07 trajectory interpolation."""

import unittest

import numpy as np

from homework.hw07.trajectory import interpolate, waypoint_times

TIMES = np.array([0.0, 1.0, 3.0, 4.0])
PATH = np.array([[0.0, 0.0], [1.0, 0.5], [2.0, -0.5], [2.5, 0.0]])


class InterpolationChecks(unittest.TestCase):
    def test_passes_through_every_waypoint(self):
        for t, q in zip(TIMES, PATH):
            np.testing.assert_allclose(interpolate(TIMES, PATH, t)[0], q, atol=1e-12)

    def test_starts_and_ends_at_rest(self):
        for t in (TIMES[0], TIMES[-1]):
            np.testing.assert_allclose(interpolate(TIMES, PATH, t)[1], 0, atol=1e-12)

    def test_velocity_is_continuous_at_an_interior_waypoint(self):
        before = interpolate(TIMES, PATH, 1.0 - 1e-7)[1]
        after = interpolate(TIMES, PATH, 1.0 + 1e-7)[1]
        np.testing.assert_allclose(before, after, atol=1e-5)
        # The average of the neighboring slopes [1, 0.5] and [0.5, -0.5].
        np.testing.assert_allclose(after, [0.75, 0.0], atol=1e-5)

    def test_holds_the_endpoints_outside_the_time_range(self):
        q, dq = interpolate(TIMES, PATH, -2.0)
        np.testing.assert_allclose(q, PATH[0])
        q, dq = interpolate(TIMES, PATH, 10.0)
        np.testing.assert_allclose(q, PATH[-1])
        np.testing.assert_allclose(dq, 0)

    def test_supplied_times_start_at_zero_and_increase(self):
        times = waypoint_times(PATH, max_speed=0.5)
        self.assertEqual(times[0], 0)
        self.assertAlmostEqual(times[1], 2.0)  # largest change 1 rad at 0.5 rad/s


if __name__ == "__main__":
    unittest.main()
