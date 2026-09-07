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
        box = get_provider('box')
        self.assertFalse(box.supports_rig)
        self.assertFalse(box.supports_idle)
        with self.assertRaisesRegex(ValueError, 'Unsupported'):
            get_provider('unknown')

    def test_box_rejects_invalid_dimensions(self):
        for value in (0, float('nan'), True, '100'):
            with self.assertRaises((TypeError, ValueError)):
                get_provider('box').mesh(dict(width_cm=value, depth_cm=100, height_cm=100))

    def test_static_provider_does_not_need_rig_or_idle_methods(self):
        provider = SimpleNamespace(key='static_test', label='Static Test', parameters=(),
                                   supports_rig=False, supports_idle=False,
                                   mesh=lambda values: get_provider('box').mesh(
                                       dict(width_cm=10, depth_cm=10, height_cm=10)))
        self.assertIs(validate_provider(provider), provider)
        with patch.dict(OBJECT_TYPES, {provider.key: provider}):
            self.assertIs(get_provider(provider.key), provider)

    def test_invalid_capabilities_fail_before_generation(self):
        baseline = dict(key='invalid', label='Invalid', parameters=(),
                        supports_rig=False, supports_idle=False, mesh=lambda values: None)
        cases = [dict(supports_rig='yes'), dict(supports_idle=True),
                 dict(supports_rig=True),
                 dict(supports_rig=True, skeleton=lambda values: None, supports_idle=True),
                 dict(mesh=None), dict(key=''), dict(label='')]
        for changes in cases:
            with self.subTest(changes=changes):
                provider = SimpleNamespace(**dict(baseline, **changes))
                with self.assertRaises((TypeError, ValueError)):
                    validate_provider(provider)

    def test_registry_key_mismatch_is_rejected(self):
        with patch.dict(OBJECT_TYPES, {'wrong_key': get_provider('box')}):
            with self.assertRaisesRegex(ValueError, 'registry key'):
                get_provider('wrong_key')

    def test_duplicate_parameter_keys_are_rejected(self):
        from object_core.objects import Parameter
        field = Parameter('size', 'Size', 10, 1, 20)
        provider = SimpleNamespace(key='duplicate', label='Duplicate', parameters=(field, field),
                                   supports_rig=False, supports_idle=False, mesh=lambda values: None)
        with self.assertRaisesRegex(ValueError, 'parameter'):
            validate_provider(provider)
