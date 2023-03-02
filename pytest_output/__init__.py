from __future__ import annotations

import pytest

from .output import OutputData, OutputDataItemResult, OutputGenerator, OutputModeType
from .outputs.polarion import PolarionOutput
from .outputs.yaml import YamlOutput


class OutputPlugin(object):
    def __init__(self, config: pytest.Config) -> None:
        self.config: pytest.Config = config
        self.data: OutputData | None = None
        self.outputs: list[OutputGenerator] = [
            YamlOutput(),
            PolarionOutput(),
        ]

    def pytest_addhooks(self, pluginmanager: pytest.PytestPluginManager):
        from . import hooks

        pluginmanager.add_hookspecs(hooks)

    def pytest_addoption(self, parser: pytest.Parser):
        for output in self.outputs:
            output.pytest_addoption(parser)

    def pytest_configure(self, config: pytest.Config):
        mode: OutputModeType = "collect" if config.getoption("collectonly") else "run"
        self.data = OutputData(mode)

        for output in self.outputs:
            output.pytest_configure(config)

    def pytest_collection_finish(self, session: pytest.Session):
        if self.data is None:
            raise ValueError("Data must not be None.")

        for item in session.items:
            output_item = self.data.add_item(item)
            self.config.hook.pytest_output_item_collected(config=self.config, item=output_item)

    @pytest.hookimpl(tryfirst=True, hookwrapper=True)
    def pytest_runtest_makereport(self, item: pytest.Item, call: pytest.CallInfo):
        if self.data is None:
            raise ValueError("Data must not be None.")

        outcome = yield
        result: pytest.TestReport = outcome.get_result()

        # Always set outcome for "call" phase. On other phases, only if the
        # phase failed or the test was skipped so we do not override the outcome
        # of the test itself.
        output_item = self.data.get_item(item)
        match result.when:
            case "setup":
                if result.failed or result.skipped:
                    output_item.result = OutputDataItemResult(result)
            case "call":
                output_item.result = OutputDataItemResult(result)
            case "teardown":
                if output_item.result is not None and result.failed:
                    output_item.result = OutputDataItemResult(result)

    def pytest_sessionfinish(self, session: pytest.Session):
        if self.data is None:
            raise ValueError("Data must not be None.")

        for output in self.outputs:
            output.generate(self.data)


def pytest_load_initial_conftests(early_config: pytest.Config, parser: pytest.Parser, args: list[str]):
    early_config.pluginmanager.register(OutputPlugin(early_config))
