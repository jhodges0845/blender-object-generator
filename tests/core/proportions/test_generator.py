# SPDX-License-Identifier: GPL-3.0-or-later
import unittest
from dataclasses import FrozenInstanceError, fields, replace
from math import isfinite

from object_core import BodyType, HumanoidSpec, generate_proportions


class ProportionTests(unittest.TestCase):
    def test_supported_range_has_positive_dimensions_and_correct_height(self):
        for height in (120, 180, 240):
            for weight in (30, 80, 300):
                for body_type in BodyType:
                    with self.subTest(height=height, weight=weight, preset=body_type):
                        result = generate_proportions(HumanoidSpec(height, weight, body_type))
                        self.assertAlmostEqual(result.standing_height_cm, height)
                        for field in fields(result):
                            value = getattr(result, field.name)
                            self.assertTrue(isfinite(value) and value > 0)

    def test_reference_character_dimensions(self):
        result = generate_proportions(HumanoidSpec(180, 80, BodyType.AVERAGE))
        self.assertAlmostEqual(result.head_height_cm, 23.4)
        self.assertAlmostEqual(result.shoulder_width_cm, 41.4)
        self.assertAlmostEqual(result.waist_width_cm, 28.8)
        self.assertAlmostEqual(result.upper_leg_length_cm, 45)

    def test_weight_increases_girth_without_lengthening_skeleton(self):
        spec = HumanoidSpec(180, 80, BodyType.AVERAGE)
        light = generate_proportions(spec)
        heavy = generate_proportions(replace(spec, weight_kg=120))
        for name in ("waist_width_cm", "waist_depth_cm", "thigh_thickness_cm",
                     "chest_depth_cm", "upper_arm_thickness_cm"):
            self.assertGreater(getattr(heavy, name), getattr(light, name))
        for name in ("head_height_cm", "torso_length_cm", "upper_leg_length_cm",
                     "lower_leg_length_cm", "upper_arm_length_cm", "forearm_length_cm"):
            self.assertEqual(getattr(heavy, name), getattr(light, name))

    def test_geometrically_scaled_character_preserves_shape(self):
        small = generate_proportions(HumanoidSpec(160, 60, BodyType.MUSCULAR))
        large = generate_proportions(HumanoidSpec(200, 60 * 1.25 ** 3, BodyType.MUSCULAR))
        for field in fields(small):
            self.assertAlmostEqual(getattr(large, field.name), getattr(small, field.name) * 1.25)

    def test_presets_have_distinct_intended_shapes_at_same_weight(self):
        results = {kind: generate_proportions(HumanoidSpec(180, 80, kind)) for kind in BodyType}
        ordered = [BodyType.SLIM, BodyType.AVERAGE, BodyType.OVERWEIGHT, BodyType.OBESE]
        waists = [results[kind].waist_width_cm for kind in ordered]
        self.assertTrue(all(left < right for left, right in zip(waists, waists[1:])))
        muscular, average = results[BodyType.MUSCULAR], results[BodyType.AVERAGE]
        self.assertGreater(muscular.shoulder_width_cm, average.shoulder_width_cm)
        self.assertGreater(muscular.upper_arm_thickness_cm, average.upper_arm_thickness_cm)
        self.assertLess(muscular.waist_width_cm, average.waist_width_cm)

    def test_generator_limits_are_separate_from_input_contract(self):
        for name, value in (("height_cm", 119.9), ("height_cm", 240.1),
                            ("weight_kg", 29.9), ("weight_kg", 300.1)):
            with self.subTest(name=name, value=value):
                spec = replace(HumanoidSpec(180, 80, BodyType.AVERAGE), **{name: value})
                with self.assertRaisesRegex(ValueError, name):
                    generate_proportions(spec)

    def test_result_is_deterministic_and_immutable(self):
        spec = HumanoidSpec(180, 80, BodyType.AVERAGE)
        result = generate_proportions(spec)
        self.assertEqual(result, generate_proportions(spec))
        self.assertEqual(spec, HumanoidSpec(180, 80, BodyType.AVERAGE))
        with self.assertRaises(FrozenInstanceError):
            result.waist_width_cm = 0

    def test_invalid_spec_type(self):
        with self.assertRaisesRegex(TypeError, "HumanoidSpec"):
            generate_proportions(None)

    def test_output_contract_rejects_invalid_dimensions(self):
        result = generate_proportions(HumanoidSpec(180, 80, BodyType.AVERAGE))
        for field in fields(result):
            for value in (0, -1, float("nan"), float("inf")):
                with self.subTest(field=field.name, value=value):
                    with self.assertRaisesRegex(ValueError, field.name):
                        replace(result, **{field.name: value})
