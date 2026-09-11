# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from object_core.objects import get_provider


class QuadrupedAnimationTests(unittest.TestCase):
    def setUp(self):
        self.provider = get_provider("quadruped")

    def test_quadruped_declares_idle_locomotion_and_run_support(self):
        self.assertTrue(self.provider.supports_idle)
        self.assertTrue(self.provider.supports_locomotion)
        self.assertTrue(self.provider.supports_run)

    def test_idle_is_closed_and_targets_quadruped_upper_body_and_tail(self):
        clip = self.provider.idle(4.0, 1.0)
        self.assertEqual(clip.duration, 4.0)
        names = {track.bone for track in clip.tracks}
        self.assertEqual(names, {"spine", "neck", "head", "tail.1", "tail.2", "tail.3"})
        for track in clip.tracks:
            self.assertAlmostEqual(track.keys[0][0], 0.0)
            self.assertAlmostEqual(track.keys[-1][0], clip.duration)
            self.assertAlmostEqual(track.keys[0][1], track.keys[-1][1])

    def test_walk_uses_diagonal_quadruped_gait_and_is_closed(self):
        clip = self.provider.locomotion(1.2, 1.0)
        tracks = {track.bone: track for track in clip.tracks}
        required = {
            "fore_upper.left", "fore_upper.right", "fore_lower.left", "fore_lower.right",
            "hind_upper.left", "hind_upper.right", "hind_lower.left", "hind_lower.right",
            "spine", "neck", "tail.1", "tail.2", "tail.3",
        }
        self.assertEqual(set(tracks), required)
        for track in tracks.values():
            self.assertAlmostEqual(track.keys[0][1], track.keys[-1][1])
        self.assertAlmostEqual(tracks["fore_upper.left"].keys[0][1],
                               tracks["hind_upper.right"].keys[0][1] * (24.0 / 22.0))
        self.assertLess(tracks["fore_upper.left"].keys[0][1] *
                        tracks["fore_upper.right"].keys[0][1], 0.0)
        self.assertLess(tracks["hind_upper.left"].keys[0][1] *
                        tracks["hind_upper.right"].keys[0][1], 0.0)

    def test_animation_validation_matches_shared_provider_ranges(self):
        for method in (self.provider.idle, self.provider.locomotion, self.provider.run):
            for duration, strength in ((True, 1.0), (1.2, True), (float("nan"), 1.0), (1.2, 0.0)):
                with self.assertRaises((TypeError, ValueError)):
                    method(duration, strength)


if __name__ == "__main__":
    unittest.main()
