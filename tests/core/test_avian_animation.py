# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from object_core.objects import get_provider
from object_core.providers.avian_animation import generate_avian_flight, generate_avian_idle


class AvianAnimationTests(unittest.TestCase):
    def test_provider_exposes_idle_and_flight_without_run(self):
        provider = get_provider("avian")
        self.assertTrue(provider.supports_idle)
        self.assertTrue(provider.supports_locomotion)
        self.assertTrue(provider.supports_flight)
        self.assertFalse(provider.supports_run)
        self.assertEqual(provider.locomotion_label, "Flight")

    def test_idle_is_closed_and_moves_head_wings_and_tail(self):
        clip = generate_avian_idle(4.0, 1.0)
        self.assertEqual(clip, generate_avian_idle(4.0, 1.0))
        by_bone = {track.bone: track for track in clip.tracks}
        self.assertTrue({"neck", "head", "wing.upper.left", "wing.upper.right",
                         "tail.1", "tail.2"}.issubset(by_bone))
        for track in clip.tracks:
            self.assertAlmostEqual(track.keys[0][1], track.keys[-1][1])

    def test_flight_is_closed_symmetric_and_uses_both_wing_segments(self):
        clip = generate_avian_flight(0.9, 1.0)
        stronger = generate_avian_flight(0.9, 2.0)
        self.assertEqual(clip, generate_avian_flight(0.9, 1.0))
        by_bone = {track.bone: track for track in clip.tracks}
        self.assertTrue({"wing.upper.left", "wing.upper.right",
                         "wing.lower.left", "wing.lower.right",
                         "spine", "neck", "tail.1", "tail.2"}.issubset(by_bone))
        left = by_bone["wing.upper.left"]
        right = by_bone["wing.upper.right"]
        self.assertAlmostEqual(left.keys[0][1], -right.keys[0][1])
        self.assertAlmostEqual(left.keys[0][1], left.keys[-1][1])
        for base, doubled in zip(clip.tracks, stronger.tracks):
            self.assertEqual(len(base.keys), 17)
            self.assertTrue(all(a[0] < b[0] for a, b in zip(base.keys, base.keys[1:])))
            self.assertAlmostEqual(doubled.keys[0][1], 2 * base.keys[0][1])

    def test_animation_validation_rejects_shared_control_outliers(self):
        for generator, bad_durations in ((generate_avian_idle, (0.5, 21.0)),
                                         (generate_avian_flight, (0.4, 4.1))):
            for duration in bad_durations:
                with self.subTest(generator=generator.__name__, duration=duration):
                    with self.assertRaises(ValueError):
                        generator(duration=duration)
            for strength in (0.0, 2.1, float("nan"), True):
                with self.subTest(generator=generator.__name__, strength=strength):
                    with self.assertRaises((TypeError, ValueError)):
                        generator(strength=strength)


if __name__ == "__main__":
    unittest.main()
