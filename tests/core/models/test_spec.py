import unittest
from dataclasses import FrozenInstanceError

from humanoid_core import BodyType, HumanoidSpec


class HumanoidSpecTests(unittest.TestCase):
    def test_all_five_presets_preserve_artist_choice(self):
        self.assertEqual(
            {preset.value for preset in BodyType},
            {"slim", "average", "muscular", "overweight", "obese"},
        )
        for preset in BodyType:
            with self.subTest(preset=preset):
                spec = HumanoidSpec(180, 80, preset)
                self.assertIs(spec.body_type, preset)
                self.assertEqual(spec.height_cm, 180.0)
                self.assertEqual(spec.weight_kg, 80.0)
                self.assertIsInstance(spec.height_cm, float)
                self.assertIsInstance(spec.weight_kg, float)

    def test_fractional_measurements_are_preserved(self):
        spec = HumanoidSpec(175.5, 72.25, BodyType.AVERAGE)
        self.assertEqual((spec.height_cm, spec.weight_kg), (175.5, 72.25))

    def test_invalid_measurement_values(self):
        for field in ("height_cm", "weight_kg"):
            for value in (0, -1, float("nan"), float("inf"), -float("inf"), 10**1000):
                with self.subTest(field=field, value=value):
                    inputs = dict(height_cm=180, weight_kg=80, body_type=BodyType.AVERAGE)
                    inputs[field] = value
                    with self.assertRaisesRegex(ValueError, field):
                        HumanoidSpec(**inputs)

    def test_invalid_measurement_types(self):
        for field in ("height_cm", "weight_kg"):
            for value in (True, False, "180", None, [], complex(1, 2)):
                with self.subTest(field=field, value=value):
                    inputs = dict(height_cm=180, weight_kg=80, body_type=BodyType.AVERAGE)
                    inputs[field] = value
                    with self.assertRaisesRegex(TypeError, field):
                        HumanoidSpec(**inputs)

    def test_body_type_requires_explicit_enum(self):
        for value in ("average", "unknown", None, 1):
            with self.subTest(value=value):
                with self.assertRaisesRegex(TypeError, "body_type"):
                    HumanoidSpec(180, 80, value)

    def test_spec_is_immutable(self):
        spec = HumanoidSpec(180, 80, BodyType.AVERAGE)
        with self.assertRaises(FrozenInstanceError):
            spec.height_cm = 190


if __name__ == "__main__":
    unittest.main()
