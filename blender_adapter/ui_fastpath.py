# SPDX-License-Identifier: GPL-3.0-or-later
"""Keep Blender UI redraws lightweight and apply small pre-registration UI policy."""


def install(ui):
    """Apply lightweight redraw behavior and the public generation-provider list."""

    # Keep the legacy ``humanoid`` provider available to load/operate on older
    # generated assets, but stop offering it for creation. Human is the
    # supported human path for new assets.
    visible_providers = tuple(
        provider for provider in ui.OBJECT_TYPES.values()
        if provider.key != 'humanoid'
    )
    ui.HUMANOID_PG_settings.__annotations__['object_type'] = ui.EnumProperty(
        name='Object Type',
        default='human_experimental',
        items=[
            (provider.key, provider.label, 'Generate ' + provider.label)
            for provider in visible_providers
        ],
    )

    @classmethod
    def export_poll(cls, context):
        if context.scene is None or context.mode != 'OBJECT' or ui._character(context) is None:
            return False
        return ui.is_ready(context.scene.humanoid_settings.validation_results)

    def needs_attention(context, stage):
        codes = {
            'MODEL': {'geometry', 'target_geometry', 'cura_solid', 'export_transform', 'export_units', 'export_modifier'},
            'RIGGING': {'rig', 'target_rig'},
            'ANIMATION': {'animation', 'target_animation', 'export_nla', 'fbx_animation_range', 'export_constraints'},
        }.get(stage)
        issues = context.scene.humanoid_settings.validation_results
        return any(issue.status in ('ERROR', 'WARN') and (codes is None or issue.code in codes)
                   for issue in issues)

    original_export_draw = ui.HUMANOID_PT_export.draw

    def export_draw(self, context):
        # Reuse the established panel layout while substituting the explicit
        # validation snapshot for redraw-time calls to the expensive inspector.
        original_export_issues = ui._export_issues
        ui._export_issues = lambda _context: _context.scene.humanoid_settings.validation_results
        try:
            return original_export_draw(self, context)
        finally:
            ui._export_issues = original_export_issues

    ui.HUMANOID_OT_export.poll = export_poll
    ui._needs_attention = needs_attention
    ui.HUMANOID_PT_export.draw = export_draw
