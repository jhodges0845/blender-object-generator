# SPDX-License-Identifier: GPL-3.0-or-later
import unittest
from object_core.objects import OBJECT_TYPES, get_provider, validate_provider
from types import SimpleNamespace
from unittest.mock import patch
from object_core.models.mesh import ObjectMesh


class ObjectProviderTests(unittest.TestCase):
    def test_providers_share_mesh_contract_and_publish_capabilities(self):
        for provider in OBJECT_TYPES.values():
            values = {field.key: field.default for field in provider.parameters}
            mesh = provider.mesh(values)
            self.assertIsInstance(mesh, ObjectMesh)
            self.assertEqual(mesh, provider.mesh(values))
            self.assertIsInstance(provider.uses_skin_weights, bool)
        box = get_provider('box')
        self.assertFalse(box.supports_rig)
        self.assertFalse(box.supports_idle)
        self.assertFalse(box.uses_skin_weights)
        with self.assertRaisesRegex(ValueError, 'Unsupported'):
            get_provider('unknown')

    def test_experimental_human_is_opt_in_deforming_provider(self):
        provider = get_provider('human_experimental')
        values = {field.key: field.default for field in provider.parameters}
        mesh = provider.mesh(values)
        skeleton = provider.skeleton(values)
        weights = provider.skin_weights(mesh, values)
        self.assertEqual(provider.label, 'Human 1.0 (Experimental)')
        self.assertTrue(provider.supports_rig)
        self.assertFalse(provider.supports_idle)
        self.assertTrue(provider.uses_skin_weights)
        self.assertEqual(len(mesh.parts), 1)
        self.assertEqual(mesh.parts[0].name, 'human')
        self.assertTrue(all(bone.part_name is None for bone in skeleton.bones))
        self.assertEqual(tuple(weight.part_name for weight in weights), ('human',))
        self.assertEqual(len(weights[0].vertices), len(mesh.parts[0].vertices))

    def test_box_rejects_invalid_dimensions(self):
        for value in (0, float('nan'), True, '100'):
            with self.assertRaises((TypeError, ValueError)):
                get_provider('box').mesh(dict(width_cm=value, depth_cm=100, height_cm=100))

    def test_static_provider_does_not_need_rig_or_idle_methods(self):
        provider = SimpleNamespace(key='static_test', label='Static Test', parameters=(),
                                   supports_rig=False, supports_idle=False, uses_skin_weights=False,
                                   mesh=lambda values: get_provider('box').mesh(
                                       dict(width_cm=10, depth_cm=10, height_cm=10)))
        self.assertIs(validate_provider(provider), provider)
        with patch.dict(OBJECT_TYPES, {provider.key: provider}):
            self.assertIs(get_provider(provider.key), provider)

    def test_invalid_capabilities_fail_before_generation(self):
        baseline = dict(key='invalid', label='Invalid', parameters=(),
                        supports_rig=False, supports_idle=False, uses_skin_weights=False,
                        mesh=lambda values: None)
        cases = [dict(supports_rig='yes'), dict(supports_idle=True),
                 dict(uses_skin_weights='yes'), dict(uses_skin_weights=True),
                 dict(supports_rig=True),
                 dict(supports_rig=True, skeleton=lambda values: None, supports_idle=True),
                 dict(supports_rig=True, skeleton=lambda values: None, uses_skin_weights=True),
                 dict(mesh=None), dict(key=''), dict(label='')]
        for changes in cases:
            with self.subTest(changes=changes):
                provider = SimpleNamespace(**dict(baseline, **changes))
                with self.assertRaises((TypeError, ValueError)):
                    validate_provider(provider)

    def test_skin_weight_provider_contract_is_generic(self):
        provider = SimpleNamespace(key='deforming_test', label='Deforming Test', parameters=(),
                                   supports_rig=True, supports_idle=False, uses_skin_weights=True,
                                   mesh=lambda values: None, skeleton=lambda values: None,
                                   skin_weights=lambda mesh, values: ())
        self.assertIs(validate_provider(provider), provider)

    def test_registry_key_mismatch_is_rejected(self):
        with patch.dict(OBJECT_TYPES, {'wrong_key': get_provider('box')}):
            with self.assertRaisesRegex(ValueError, 'registry key'):
                get_provider('wrong_key')

    def test_duplicate_parameter_keys_are_rejected(self):
        from object_core.objects import Parameter
        field = Parameter('size', 'Size', 10, 1, 20)
        provider = SimpleNamespace(key='duplicate', label='Duplicate', parameters=(field, field),
                                   supports_rig=False, supports_idle=False, uses_skin_weights=False,
                                   mesh=lambda values: None)
        with self.assertRaisesRegex(ValueError, 'parameter'):
            validate_provider(provider)
