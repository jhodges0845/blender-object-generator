# SPDX-License-Identifier: GPL-3.0-or-later
import unittest
from humanoid_core.animation.idle import generate_idle


class IdleTests(unittest.TestCase):
    def test_closed_cycle_and_scaled_motion(self):
        clip = generate_idle(6, 1)
        stronger = generate_idle(6, 2)
        self.assertEqual(clip, generate_idle(6, 1))
        for track, doubled in zip(clip.tracks, stronger.tracks):
            self.assertEqual(track.keys[0], (0, 0))
            self.assertEqual(track.keys[-1], (6, 0))
            self.assertNotEqual(track.keys[16][1], 0)
            self.assertEqual(doubled.keys[16][1], 2 * track.keys[16][1])
            self.assertTrue(all(a[0] < b[0] for a, b in zip(track.keys, track.keys[1:])))
        self.assertFalse(any(t.bone == 'root' or 'leg' in t.bone or 'foot' in t.bone for t in clip.tracks))

    def test_invalid_settings(self):
        for value in (True, '4', None, float('nan'), float('inf'), 0, -1, 21):
            with self.subTest(value=value), self.assertRaises((TypeError, ValueError)):
                generate_idle(value)
        for value in (False, 0, 3, float('nan')):
            with self.assertRaises((TypeError, ValueError)):
                generate_idle(strength=value)
