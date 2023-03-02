""" Intermediary output format. """

from __future__ import annotations

import inspect
import re
import sys
import textwrap
from abc import ABC, abstractmethod
from collections import OrderedDict
from enum import Enum, auto
from typing import Any, Literal, TypeAlias

import pytest

OutputModeType: TypeAlias = Literal["run", "collect"]


class Outcome(Enum):
    """
    Test outcome.
    """

    PASSED = auto()
    FAILED = auto()
    SKIPPED = auto()
    ERROR = auto()


class OutputData(object):
    """
    Intermediary output format.

    Contains various information about test case and run.
    """

    def __init__(self, mode: OutputModeType) -> None:
        """
        :param mode: Pytest mode (collect or run)
        :type mode: OutputModeType
        """
        self.mode: OutputModeType = mode
        """Pytest mode (collect or run)"""

        self.items: OrderedDict[str, OutputDataItem] = OrderedDict()
        """Collected items."""

    def add_item(self, item: pytest.Item) -> OutputDataItem:
        """
        Add new item to the collection.

        :param item: Pytest item (``pytest.Function`` is expected).
        :type item: pytest.Item
        :raises ValueError: If unexpected type is given.
        :return: Item's intermediary output data.
        :rtype: OutputDataItem
        """
        if not isinstance(item, pytest.Function):
            raise ValueError(f"Unexpected item type: {type(item)}, expected pytest.Function")

        data = OutputDataItem(item)
        self.items[item.nodeid] = data

        return data

    def get_item(self, item: pytest.Item) -> OutputDataItem:
        """
        Get item's intermediary output data.

        :param item: ytest item (``pytest.Function`` is expected).
        :type item: pytest.Item
        :raises ValueError: If unexpected type is given.
        :return: Item's intermediary output data.
        :rtype: OutputDataItem
        """
        if not isinstance(item, pytest.Function):
            raise ValueError(f"Unexpected item type: {type(item)}, expected pytest.Function")

        return self.items[item.nodeid]

    def to_dict(self) -> dict[str, Any]:
        """
        Transform this class into a dictionary.

        :return: Representation of this class as a dictionary.
        :rtype: dict[str, Any]
        """
        return {
            "mode": self.mode,
            "items": OrderedDict({k: v.to_dict() for k, v in self.items.items()}),
        }


class OutputDataItem(object):
    """
    Pytest item intermediary data.
    """

    def __init__(self, item: pytest.Function) -> None:
        docs = self._get_all_docstrings(item)
        description = self._get_docstring(item.obj)

        self.item: pytest.Function = item
        """Pytest item."""

        self.id: str = item.nodeid
        """Item id."""

        self.name: str = item.name
        """Item name."""

        self.description: str = description if description is not None else ""
        """Item description for docstring."""

        self.package: str | None = item.module.__package__ if item.module.__package__ else None
        """Python package that contains this item."""

        self.module: str = item.module.__name__
        """Python module that contains this item."""

        self.cls: str | None = item.cls.__name__ if item.cls else None
        """Python class that contains this item."""

        self.location: OutputDataItemLocation = OutputDataItemLocation(*item.location)
        """Item location."""

        self.docstring: list[str] = docs
        """List of item's docstring (module, class, function)."""

        self.meta: dict[str, str] = self._get_meta(docs)
        """Item meta data (``:name: value`` strings in docstrings)"""

        self.markers: list[pytest.Mark] = list(item.iter_markers())
        """Markers associated with this item."""

        self.result: OutputDataItemResult | None = None
        """Item test result."""

        self.extra: dict[str, dict[str, str]] = {}
        """Extra information provided from other plugins."""

    def to_dict(self) -> dict[str, Any]:
        """
        Transform this class into a dictionary.

        :return: Representation of this class as a dictionary.
        :rtype: dict[str, Any]
        """
        return {
            "id": self.id,
            "name": self.name,
            "package": self.package,
            "module": self.module,
            "class": self.cls,
            "location": self.location.to_dict(),
            "docstring": self.docstring,
            "meta": self.meta,
            "markers": self.markers,
            "result": self.result.to_dict() if self.result is not None else None,
            "extra": self.extra,
        }

    def _get_all_docstrings(self, item: pytest.Function) -> list[str]:
        docs: list[str | None] = [self._get_docstring(item.obj)]

        # Append docstring from classes
        if item.cls is not None:
            for cls in inspect.getmro(item.cls):
                if cls == object:
                    continue

                docs.append(self._get_docstring(cls))

        # Append docstring from modules
        parts = item.module.__name__.split(".")
        modules = []
        for index, _ in enumerate(parts, start=1):
            modules.append(".".join(parts[:index]))

        for module in reversed(modules):
            docs.append(self._get_docstring(sys.modules[module]))

        return [x for x in reversed(docs) if x is not None]

    def _get_docstring(self, obj: Any) -> str | None:
        if obj.__doc__:
            return textwrap.dedent(obj.__doc__).strip()

        return None

    def _get_meta(self, docs: list[str]) -> dict[str, str]:
        meta = {}
        for doc in docs:
            matches = re.finditer(
                r"^:(?P<field>[^:]+):(?P<data>((?!(^:|\n\n)).)*)", doc, flags=re.MULTILINE | re.DOTALL
            )
            for m in matches:
                key = m.group("field").strip()
                value = textwrap.dedent(m.group("data")).strip()
                meta[key] = value

        return meta


class OutputDataItemResult(object):
    """
    Test result.
    """

    def __init__(self, result: pytest.TestReport) -> None:
        self._result: pytest.TestReport = result

        self.outcome: Outcome = self._outcome_to_enum(result.when, result.outcome)
        """Test outcome."""

        self.stdout: str = result.capstderr
        """Captured standard output."""

        self.stderr: str = result.capstderr
        """Captured standard error output."""

        self.logs: str = result.caplog
        """Captured logs."""

        self.duration: float = result.duration
        """Test run duration."""

        self.summary: str = self._get_summary(result)
        """Test run short summary (e.g. reason for failure or skip)."""

        self.message: str = self._get_message(result)
        """Test run long message (e.g. reason for failure or skip)."""

    def _outcome_to_enum(self, when: str | None, outcome: Literal["passed", "failed", "skipped"]) -> Outcome:
        if when != "call" and outcome == "failed":
            return Outcome.ERROR

        return Outcome[outcome.upper()]

    def _get_summary(self, result: pytest.TestReport):
        if result.longrepr is None:
            return result.longreprtext

        match result.outcome:
            case "failed":
                if (
                    hasattr(result.longrepr, "reprcrash")
                    and not isinstance(result.longrepr, tuple)
                    and result.longrepr.reprcrash is not None
                ):
                    if result.when != "call":
                        return f'failed on {result.when} with "{result.longrepr.reprcrash.message}"'
                    return result.longrepr.reprcrash.message
            case "skipped":
                if isinstance(result.longrepr, tuple):
                    return result.longrepr[2]
            case _:
                return ""

        return result.longreprtext

    def _get_message(self, result: pytest.TestReport):
        if result.outcome == "skipped" and isinstance(result.longrepr, tuple):
            return f"{result.longrepr[0]}:{result.longrepr[1]}: {result.longrepr[2]}"

        if result.longreprtext is not None:
            return result.longreprtext

        return ""

    def to_dict(self) -> dict[str, Any]:
        """
        Transform this class into a dictionary.

        :return: Representation of this class as a dictionary.
        :rtype: dict[str, Any]
        """
        return {
            "outcome": self.outcome.name.lower(),
            "stdout": self.stdout,
            "stderr": self.stderr,
            "logs": self.logs,
        }


class OutputDataItemLocation(object):
    """
    Pytest item location.
    """

    def __init__(self, file: str, line: int | None, name: str) -> None:
        self.file: str = file
        """File."""

        self.line: int | None = line
        """Line."""

        self.name: str = name
        """Name."""

    def to_dict(self) -> dict[str, Any]:
        """
        Transform this class into a dictionary.

        :return: Representation of this class as a dictionary.
        :rtype: dict[str, Any]
        """
        return {
            "file": self.file,
            "line": self.line,
            "name": self.name,
        }


class OutputGenerator(ABC):
    """
    Output generator abstract class.

    Inherit from this class to create a new generator.
    """

    def pytest_addoption(self, parser: pytest.Parser):
        """
        Add additional pytest command line options.

        :param parser: Parser object.
        :type parser: pytest.Parser
        """
        pass

    def pytest_configure(self, config: pytest.Config):
        """
        Configure the generator object.

        It is possible to read parsed command line option in this method.

        :param config: Pytest config.
        :type config: pytest.Config
        """
        pass

    @abstractmethod
    def generate(self, data: OutputData) -> None:
        """
        Generate pytest output from intermediary data format.

        :param data: Gathered test cases and results.
        :type data: OutputData
        """
        pass
