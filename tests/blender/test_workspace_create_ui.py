from blender_adapter import workspace_create_ui


class _Field:
    def __init__(self, name):
        self.name = name


class _Provider:
    label = "Human"
    parameters = tuple(_Field(name) for name in ("height", "weight", "body_type", "waist", "shoulders"))


class _UI:
    @staticmethod
    def get_provider(_key):
        return _Provider()

    @staticmethod
    def _field_name(_provider, field):
        return "field_" + field.name


class _Settings:
    object_type = "human_experimental"
    asset_assistant_create_advanced = False
    asset_assistant_workspace = "CREATE"
    asset_assistant_create_view = "GENERATE"
    target = None


class _Scene:
    humanoid_settings = _Settings()


class _Context:
    scene = _Scene()


class _Node:
    def __init__(self):
        self.scale_y = 1.0
        self.scale_x = 1.0
        self.children = []
        self.labels = []
        self.props = []
        self.enums = []
        self.operators = []

    def box(self):
        child = _Node()
        self.children.append(child)
        return child

    def row(self, align=False):
        child = _Node()
        self.children.append(child)
        return child

    def column(self, align=False):
        child = _Node()
        self.children.append(child)
        return child

    def label(self, **kwargs):
        self.labels.append(kwargs)

    def prop(self, _settings, prop, **kwargs):
        self.props.append((prop, kwargs))

    def prop_enum(self, _settings, prop, key, **kwargs):
        self.enums.append((prop, key, kwargs))

    def operator(self, op, **kwargs):
        self.operators.append((op, kwargs))

    def separator(self, **_kwargs):
        pass


class _Panel:
    def __init__(self):
        self.layout = _Node()


def _walk(node):
    yield node
    for child in node.children:
        yield from _walk(child)


def test_create_generate_uses_four_unified_asset_buttons_and_primary_action():
    panel = _Panel()
    workspace_create_ui._draw_generate(panel, _Context(), _UI(), working_asset_ui=object())

    nodes = list(_walk(panel.layout))
    asset_rows = [node for node in nodes if node.scale_y == 2.25 and node.enums]
    assert len(asset_rows) == 1
    assert asset_rows[0].enums == [
        ("object_type", "human_experimental", {"text": "Human", "icon": "USER"}),
        ("object_type", "quadruped", {"text": "Human", "icon": "ARMATURE_DATA"}),
        ("object_type", "avian", {"text": "Human", "icon": "OUTLINER_OB_MESH"}),
        ("object_type", "box", {"text": "Human", "icon": "CUBE"}),
    ]

    action_rows = [node for node in nodes if node.scale_y == 2.0 and node.operators]
    assert len(action_rows) == 1

    operators = [call for node in nodes for call in node.operators]
    assert ("humanoid.generate_blockout", {"text": "Generate Human", "icon": "ADD"}) in operators
    assert ("asset_assistant.open_editable_checkpoint", {"text": "Open Existing Asset", "icon": "FILE_FOLDER"}) in operators


def test_create_generate_keeps_first_three_parameters_visible_and_collapses_rest():
    panel = _Panel()
    workspace_create_ui._draw_generate(panel, _Context(), _UI(), working_asset_ui=None)

    props = [call[0] for node in _walk(panel.layout) for call in node.props]
    assert props[:3] == ["field_height", "field_weight", "field_body_type"]
    assert "field_waist" not in props
    assert "field_shoulders" not in props
    assert "asset_assistant_create_advanced" in props


def test_empty_generate_screen_hides_empty_current_asset_card():
    called = []
    original = workspace_create_ui._ORIGINAL_ASSET_SUMMARY
    try:
        workspace_create_ui._ORIGINAL_ASSET_SUMMARY = lambda layout, context: called.append((layout, context))
        workspace_create_ui._draw_contextual_asset_summary(_Node(), _Context())
        assert called == []

        _Context.scene.humanoid_settings.asset_assistant_create_view = "MODIFY"
        workspace_create_ui._draw_contextual_asset_summary(_Node(), _Context())
        assert len(called) == 1
    finally:
        _Context.scene.humanoid_settings.asset_assistant_create_view = "GENERATE"
        workspace_create_ui._ORIGINAL_ASSET_SUMMARY = original
