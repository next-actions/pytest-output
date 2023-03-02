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
    PASSED = (auto(),)
    FAILED = (auto(),)
    SKIPPED = (auto(),)
    ERROR = (auto(),)


class OutputData(object):
    def __init__(self, mode: OutputModeType) -> None:
        self.mode: OutputModeType = mode
        self.items: OrderedDict[str, OutputDataItem] = OrderedDict()

    def add_item(self, item: pytest.Item) -> OutputDataItem:
        if not isinstance(item, pytest.Function):
            raise ValueError(f"Unexpected item type: {type(item)}, expected pytest.Function")

        data = OutputDataItem(item)
        self.items[item.nodeid] = data

        return data

    def get_item(self, item: pytest.Item) -> OutputDataItem:
        if not isinstance(item, pytest.Function):
            raise ValueError(f"Unexpected item type: {type(item)}, expected pytest.Function")

        return self.items[item.nodeid]

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "items": OrderedDict({k: v.to_dict() for k, v in self.items.items()}),
        }


class OutputDataItem(object):
    def __init__(self, item: pytest.Function) -> None:
        docs = self._get_all_docstrings(item)
        description = self._get_docstring(item.obj)

        self.item: pytest.Function = item
        self.id: str = item.nodeid
        self.name: str = item.name
        self.description: str = description if description is not None else ""
        self.package: str | None = item.module.__package__ if item.module.__package__ else None
        self.module: str = item.module.__name__
        self.cls: str | None = item.cls.__name__ if item.cls else None
        self.location: OutputDataItemLocation = OutputDataItemLocation(*item.location)
        self.docstring: list[str] = docs
        self.meta: dict[str, str] = self._get_meta(docs)
        self.markers: list[pytest.Mark] = list(item.iter_markers())
        self.result: OutputDataItemResult | None = None
        self.extra: dict[str, dict[str, str]] = {}

    def to_dict(self) -> dict[str, Any]:
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
        for doc in reversed(docs):
            matches = re.finditer(
                r"^:(?P<field>[^:]+):(?P<data>((?!(^:|\n\n)).)*)", doc, flags=re.MULTILINE | re.DOTALL
            )
            for m in matches:
                key = m.group("field").strip()
                value = textwrap.dedent(m.group("data")).strip()
                meta[key] = value

        return meta


class OutputDataItemResult(object):
    def __init__(self, result: pytest.TestReport) -> None:
        self._result: pytest.TestReport = result

        self.outcome: Outcome = self._outcome_to_enum(result.when, result.outcome)
        self.stdout: str = result.capstderr
        self.stderr: str = result.capstderr
        self.logs: str = result.caplog
        self.duration: float = result.duration
        self.summary: str = self._get_summary(result)
        self.message: str = self._get_message(result)

    def _outcome_to_enum(self, when: str | None, outcome: Literal["passed", "failed", "skipped"]) -> Outcome:
        if when != "call" and outcome == "failed":
            return Outcome.ERROR

        return Outcome[outcome.upper()]

    def _get_summary(self, result: pytest.TestReport):
        if result.longrepr is None:
            return result.longreprtext

        match result.outcome:
            case "failed":
                if hasattr(result.longrepr, "reprcrash") and not isinstance(result.longrepr, tuple):
                    if result.when != "call":
                        return f'failed on {result.when} with "{result.longrepr.reprcrash.message}"'
                    return result.longrepr.reprcrash.message
            case "skipped":
                if isinstance(result.longrepr, tuple):
                    return result.longrepr[2]
            case _:
                return ""

        # This fallback and checks above are mostly to silent mypy.
        return result.longreprtext

    def _get_message(self, result: pytest.TestReport):
        if result.outcome == "skipped" and isinstance(result.longrepr, tuple):
            return f"{result.longrepr[0]}:{result.longrepr[1]}: {result.longrepr[2]}"

        if result.longreprtext is not None:
            return result.longreprtext

        return ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "outcome": self.outcome.name.lower(),
            "stdout": self.stdout,
            "stderr": self.stderr,
            "logs": self.logs,
        }


class OutputDataItemLocation(object):
    def __init__(self, file: str, line: int | None, name: str) -> None:
        self.file: str = file
        self.line: int | None = line
        self.name: str = name

    def to_dict(self) -> dict[str, Any]:
        return {
            "file": self.file,
            "line": self.line,
            "name": self.name,
        }


class OutputGenerator(ABC):
    def pytest_addoption(self, parser: pytest.Parser):
        pass

    def pytest_configure(self, config: pytest.Config):
        pass

    @abstractmethod
    def generate(self, data: OutputData) -> None:
        """
        Generate pytest output.

        :param data: Gathered test cases and results.
        :type data: dict[str, Any]
        """
        pass
