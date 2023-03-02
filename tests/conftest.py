from __future__ import annotations

from pathlib import Path

import pytest

pytest_plugins = ["pytester"]


@pytest.fixture(scope="session")
def datadir(request: pytest.FixtureRequest) -> Path:
    """
    Data directory shared for all tests.

    :return: Path to the data directory ``(root-pytest-dir)/tests/data``.
    :rtype: Path
    """
    return Path(request.node.path / "tests/data")


@pytest.fixture(scope="module")
def moduledatadir(datadir: Path, request: pytest.FixtureRequest) -> Path:
    """
    Data directory shared for all tests within a single module.

    :return: Path to the data directory ``(root-pytest-dir)/tests/data/$module_name``.
    :rtype: Path
    """
    name = request.module.__name__.split(".")[1]
    return Path(datadir / name)


@pytest.fixture(scope="function")
def testdatadir(moduledatadir: Path, request: pytest.FixtureRequest) -> Path:
    """
    Data directory for current test.

    :return: Path to the data directory ``(root-pytest-dir)/tests/data/$module_name/$test_name``.
    :rtype: Path
    """
    if not isinstance(request.node, pytest.Function):
        raise TypeError(f"Excepted pytest.Function, got {type(request.node)}")

    name = request.node.originalname
    return Path(moduledatadir / name)
