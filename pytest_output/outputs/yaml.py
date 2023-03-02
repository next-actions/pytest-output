from __future__ import annotations

from collections import OrderedDict

import pytest
import yaml

from ..output import OutputData, OutputGenerator


class CustomYamlDumper(yaml.Dumper):
    """
    Custom yaml dumper used by :class:`YamlOutput` to register custom representers.
    """

    pass


class YamlOutput(OutputGenerator):
    """
    Output test cases and runs in an yaml format.
    """

    def __init__(self) -> None:
        super().__init__()

        self.path: str | None = None
        """Output file path."""

    def pytest_addoption(self, parser: pytest.Parser):
        parser.addoption("--output-yaml", action="store", help="Path to the output yaml file")

    def pytest_configure(self, config: pytest.Config):
        self.path = config.getoption("output_yaml")

    def generate(self, data: OutputData) -> None:
        if not self.path:
            return

        def multiline_string(dumper: yaml.Dumper, data: str):
            if data.count("\n") > 0:
                return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")

            return dumper.represent_scalar("tag:yaml.org,2002:str", data)

        def pytest_mark(dumper: yaml.Dumper, data: pytest.Mark):
            return dumper.represent_dict(
                {
                    "name": data.name,
                    "args": list(data.args),
                    "kwargs": data.kwargs,
                }
            )

        def ordered_dict(dumper: yaml.Dumper, data: OrderedDict):
            return dumper.represent_dict(data)

        CustomYamlDumper.add_representer(str, multiline_string)
        CustomYamlDumper.add_representer(pytest.Mark, pytest_mark)
        CustomYamlDumper.add_representer(OrderedDict, ordered_dict)

        dump = yaml.dump(data.to_dict(), sort_keys=False, Dumper=CustomYamlDumper)
        with open(self.path, "w") as f:
            f.write(dump)
