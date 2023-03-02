from __future__ import annotations

import pytest

from .output import OutputDataItem


def pytest_output_item_collected(config: pytest.Config, item: OutputDataItem) -> None:
    pass
