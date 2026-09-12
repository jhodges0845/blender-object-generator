# SPDX-License-Identifier: GPL-3.0-or-later
"""Provider-declared semantic targets for rich Modify operations."""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class SemanticTarget:
    """One provider-owned editable target exposed to external Modify tools.

    ``kind`` is intentionally generic (for example ``region`` or ``component``).
    ``operations`` names provider-understood operations such as ``shape`` or
    ``surface``. Shared Modify code validates these declarations but never
    interprets anatomy-specific meaning.
    """

    key: str
    label: str
    kind: str
    operations: Tuple[str, ...]
