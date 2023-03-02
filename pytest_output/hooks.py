""" Custom pytest hooks. """

from __future__ import annotations

import pytest

from .output import OutputDataItem


def pytest_output_item_collected(config: pytest.Config, item: OutputDataItem) -> None:
    """
    Run when an item is collected.

    This hook can be used to add additional information to the item.

    :param config: Pytest config.
    :type config: pytest.Config
    :param item: Item data in intermediary well-defined class.
    :type item: OutputDataItem
    """
    pass
