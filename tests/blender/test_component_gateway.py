# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from blender_adapter import core


class ComponentGatewayTests(unittest.TestCase):
    def test_component_contracts_are_exposed_through_blender_gateway(self):
        record = core.ComponentRecord(
            component_id="gateway-proof",
            kind=core.ComponentKind.ACCESSORY,
            provider_key="proof",
            attachment_target="asset_root",
            attachment_mode=core.AttachmentMode.RIGID,
        )

        restored = core.component_from_document(core.component_document(record))

        self.assertEqual(record, restored)


if __name__ == "__main__":
    unittest.main()
