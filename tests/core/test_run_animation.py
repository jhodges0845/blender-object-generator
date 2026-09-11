# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from object_core.animation import generate_run
from object_core.objects import get_provider
from object_core.providers.dog_animation import generate_dog_run


class RunAnimationTests(unittest.TestCase):
    def test_human_run_is_closed_and_faster_than_default_walk(self):
        clip = generate_run()
        self.assertAlmostEqual(clip.duration, 0.72)
        self.assertTrue(clip.tracks)
        names = {track.bone for track in clip.tracks}
        self.assertIn('upper_leg.left', names)
        self.assertIn('upper_leg.right', names)
        self.assertIn('upper_arm.left', names)
        self.assertIn('upper_arm.right', names)
        for track in clip.tracks:
            self.assertEqual(track.keys[0][1], track.keys[-1][1])

    def test_dog_run_is_closed_and_uses_all_four_limbs(self):
        clip = generate_dog_run()
        self.assertAlmostEqual(clip.duration, 0.64)
        names = {track.bone for track in clip.tracks}
        for bone in ('fore_upper.left', 'fore_upper.right', 'hind_upper.left', 'hind_upper.right'):
            self.assertIn(bone, names)
        for track in clip.tracks:
            self.assertAlmostEqual(track.keys[0][1], track.keys[-1][1])

    def test_human_and_dog_providers_advertise_run(self):
        human = get_provider('human_experimental')
        dog = get_provider('dog')
        self.assertTrue(human.supports_run)
        self.assertTrue(dog.supports_run)
        self.assertEqual(human.run(0.72, 1.0).duration, 0.72)
        self.assertEqual(dog.run(0.64, 1.0).duration, 0.64)

    def test_run_validation_rejects_bad_values(self):
        with self.assertRaises(ValueError):
            generate_run(0.2, 1.0)
        with self.assertRaises(ValueError):
            generate_dog_run(0.2, 1.0)
        with self.assertRaises(TypeError):
            generate_run(True, 1.0)


if __name__ == '__main__':
    unittest.main()
