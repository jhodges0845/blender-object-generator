# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from object_core.objects import (
    AvianProvider as RegistryAvianProvider,
    BoxProvider as RegistryBoxProvider,
    HumanExperimentalProvider as RegistryHumanExperimentalProvider,
    HumanoidProvider as RegistryHumanoidProvider,
    Parameter as RegistryParameter,
    QuadrupedProvider as RegistryQuadrupedProvider,
    get_provider,
)
from object_core.providers import (
    AvianProvider,
    BoxProvider,
    HumanExperimentalProvider,
    HumanoidProvider,
    Parameter,
    QuadrupedProvider,
)


class ProviderBoundaryTests(unittest.TestCase):
    def test_registry_reexports_existing_provider_symbols(self):
        self.assertIs(RegistryParameter, Parameter)
        self.assertIs(RegistryAvianProvider, AvianProvider)
        self.assertIs(RegistryBoxProvider, BoxProvider)
        self.assertIs(RegistryHumanoidProvider, HumanoidProvider)
        self.assertIs(RegistryHumanExperimentalProvider, HumanExperimentalProvider)
        self.assertIs(RegistryQuadrupedProvider, QuadrupedProvider)

    def test_registry_resolves_extracted_provider_implementations(self):
        self.assertIsInstance(get_provider("avian"), AvianProvider)
        self.assertIsInstance(get_provider("box"), BoxProvider)
        self.assertIsInstance(get_provider("humanoid"), HumanoidProvider)
        self.assertIsInstance(get_provider("human_experimental"), HumanExperimentalProvider)
        self.assertIsInstance(get_provider("quadruped"), QuadrupedProvider)


if __name__ == "__main__":
    unittest.main()
