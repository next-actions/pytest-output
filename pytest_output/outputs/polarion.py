from __future__ import annotations

import argparse
import re
import textwrap
import time
import xml.etree.ElementTree as ET
from abc import ABC, abstractproperty
from collections import Counter
from typing import Any, TypeAlias

import pytest
import yaml
from jinja2 import Environment

from ..actions import JSONAction, KeyValueAction
from ..output import Outcome, OutputData, OutputDataItem, OutputGenerator

PolarionConfigField: TypeAlias = dict[str, dict[str, Any]]


class PolarionConfig(object):
    """Polarion output configuration."""

    def __init__(self, pytest_config: pytest.Config, path: str) -> None:
        self._config: dict[str, Any] = self._load_configuration(path)
        self._pytest: pytest.Config = pytest_config

        self.create_defects: bool = self._pytest.getoption("polarion_create_defects")
        self.dry_run: bool = self._pytest.getoption("polarion_dry_run")
        self.include_skipped: bool = self._pytest.getoption("polarion_include_skipped")
        self.lookup_method_field_id: str = self._pytest.getoption("polarion_lookup_method_field_id")
        self.lookup_method: str = self._pytest.getoption("polarion_lookup_method")
        self.project_span_ids: str | None = self._pytest.getoption("polarion_project_span_ids")
        self.testrun_group_id: str | None = self._pytest.getoption("polarion_testrun_group_id")
        self.testrun_id: str = self._sanitize_testrun_id(self._pytest.getoption("polarion_testrun_id"))
        self.testrun_template_id: str | None = self._pytest.getoption("polarion_testrun_template_id")
        self.testrun_title: str | None = self._pytest.getoption("polarion_testrun_title")
        self.testrun_type_id: str | None = self._pytest.getoption("polarion_testrun_type_id")
        self.testrun_properties: dict[str, str] = {
            **self._pytest.getoption("polarion_testrun_property"),
            **self._pytest.getoption("polarion_testrun_property_json"),
        }

    def _load_configuration(self, path: str) -> dict[str, Any]:
        try:
            with open(path, "r") as f:
                data = yaml.safe_load(f)
                return data if data is not None else {}
        except Exception as e:
            raise IOError(f'Unable to open Polarion configuration "{path}": {str(e)}')

    def _sanitize_testrun_id(self, id: str) -> str:
        id = id.format(now=time.time())
        return re.sub(r'[\\/.:"<>|~!@#$?%^&\'*()+`,=]', "", id)

    @property
    def project(self) -> str:
        """
        Polarion project.
        """
        conf = self._pytest.getoption("polarion_project")
        if conf is None:
            return self._config.get("project", "not-set")

        return conf

    @property
    def user(self) -> str:
        """
        Polarion user.
        """
        conf = self._pytest.getoption("polarion_user")
        if conf is None:
            return self._config.get("user", "not-set")

        return conf

    @property
    def tests_url(self) -> str:
        """
        Test location URL.
        """
        conf = self._pytest.getoption("polarion_tests_url")
        if conf is None:
            return self._config.get("tests_url", "")

        return conf

    @property
    def testcase(self) -> dict[str, Any]:
        """
        Test case configuration.
        """
        return self._config.get("testcase", {})

    @property
    def testrun(self) -> dict[str, Any]:
        """
        Test run configuration.
        """
        return self._config.get("testrun", {})


class PolarionField(object):
    def __init__(self, config: PolarionConfig, name: str, opts: dict[str, Any], item: OutputDataItem) -> None:
        self.config: PolarionConfig = config
        self.item = item
        self.name: str = name
        self.meta: str = opts.get("meta", name)
        self.multiline: bool | None = opts.get("multiline", None)
        self.validate: str | None = opts.get("validate", None)
        self.transform_pattern: str | None = opts.get("transform", {}).get("pattern", None)
        self.transform_replacement: str = opts.get("transform", {}).get("replace", "")
        self.transform_unless: str | None = opts.get("transform", {}).get("unless", None)
        self.format: str | None = opts.get("format", None)
        self.defval: str | None = opts.get("default", None)

        if self.multiline is None:
            self.multiline = False if self.name in ["title"] else True

    @property
    def value(self) -> str | None:
        # Get value
        value: str | None = None
        if self.meta in self.item.meta:
            value = self.item.meta[self.meta]
        elif self.defval is not None:
            env = Environment()
            tpl = env.from_string(str(self.defval))
            value = tpl.render(item=self.item, tests_url=self.config.tests_url)

        # Convert to single line
        if value is not None and not self.multiline:
            value = " ".join([x.strip() for x in value.splitlines()])

        # Transform it
        if value is not None and self.transform_pattern:
            if self.transform_unless is None or not re.match(self.transform_unless, value):
                value = re.sub(self.transform_pattern, self.transform_replacement, value)

        # Validate
        if value is not None and self.validate:
            if not re.match(self.validate, value):
                raise ValueError(f"Field '{self.name}' did not validate with '{self.validate}' for '{self.item.id}'")

        if value is not None and value.lower() in ["false", "true"]:
            value = value.lower()

        if value is not None:
            match self.format:
                case "pre":
                    value = f"<pre>{value}</pre>"

        return value

    def dumpxml(self) -> ET.Element | None:
        if self.value is None:
            return None

        return ET.Element("custom-field", id=self.name, content=self.value)


class PolarionFields(dict[str, PolarionField]):
    def __init__(
        self,
        config: PolarionConfig,
        item: OutputDataItem,
        required: PolarionConfigField,
        optional: PolarionConfigField,
    ):
        fields = {}
        for name, opts in {**required, **optional}.items():
            if opts is None:
                opts = {}

            field = PolarionField(config, name, opts, item)
            if field.value is not None:
                fields[name] = field

        for name in required:
            if name not in fields:
                raise ValueError(f"Required field '{name}' is missing for '{item.id}'")

        super().__init__(fields)

    def dumpxml(self) -> ET.Element:
        root = ET.Element("custom-fields")
        for field in self.values():
            if field.name in ["id", "title", "steps", "expectedresults", "status", "requirement"]:
                continue

            fieldxml = field.dumpxml()
            if fieldxml is not None:
                root.append(fieldxml)

        return root


class PolarionProperty(object):
    def __init__(self, name: str, value: str) -> None:
        self.name: str = name
        self.value: str = self.stringify(value)

    def stringify(self, value: Any) -> str:
        if isinstance(value, bool):
            return str(value).lower()

        return str(value)

    def dumpxml(self) -> ET.Element:
        return ET.Element("property", name=self.name, value=self.value)


class PolarionProperties(list[PolarionProperty]):
    def __init__(self, properties: dict[str, Any]) -> None:
        super().__init__([PolarionProperty(k, v) for k, v in properties.items() if v is not None])

    def dumpxml(self) -> ET.Element:
        root = ET.Element("properties")
        for property in self:
            root.append(property.dumpxml())

        return root


class PolarionStep(object):
    def __init__(self, step: str, result: str) -> None:
        self.step: str = step
        self.result: str = result

    def dumpxml(self) -> ET.Element:
        root = ET.Element("test-step")

        step = ET.SubElement(root, "test-step-column", id="step")
        step.text = self.step

        result = ET.SubElement(root, "test-step-column", id="expectedResult")
        result.text = self.result

        return root


class PolarionSteps(list[PolarionStep]):
    def __init__(self, id: str, in_steps: PolarionField | None, in_results: PolarionField | None) -> None:
        steps = self.parse(in_steps)
        results = self.parse(in_results)

        combined: list[PolarionStep] = []
        if not steps and not results:
            combined = []
        elif not results:
            combined = [PolarionStep(x[1], "") for x in steps]
        elif not steps:
            combined = [PolarionStep("", x[1]) for x in results]
        else:
            if len(steps) != len(results):
                raise ValueError(f"Number of steps and results do not match in {id}")

            for (step_id, step_value), (result_id, result_value) in zip(steps, results):
                if step_id != result_id:
                    raise ValueError(f"Step index do not match expected result in {id} ({step_id} != {result_id})")

                combined.append(PolarionStep(step_value, result_value))

        super().__init__(combined)

    def parse(self, field: PolarionField | None) -> list[tuple[int, str]]:
        if field is None or field.value is None:
            return []

        matches = re.finditer(
            r"^(?P<index>\d+)\.(?P<data>((?!^\d+\.).)*)", field.value, flags=re.MULTILINE | re.DOTALL
        )
        out = []
        for m in matches:
            index = int(m.group("index").strip())
            value = textwrap.dedent(m.group("data")).strip()
            out.append((index, value))
        return out

    def dumpxml(self) -> ET.Element:
        root = ET.Element("test-steps")
        for step in self:
            root.append(step.dumpxml())

        return root


class PolarionWorkItem(object):
    def __init__(self, name: str) -> None:
        self.name: str = name

    def dumpxml(self) -> ET.Element:
        return ET.Element(
            "linked-work-item", {"lookup-method": "name", "role-id": "verifies", "workitem-id": self.name}
        )


class PolarionWorkItems(list[PolarionWorkItem]):
    def __init__(self, items: list[str]) -> None:
        super().__init__([PolarionWorkItem(x) for x in items if x is not None])

    def dumpxml(self) -> ET.Element:
        root = ET.Element("linked-work-items")
        for item in self:
            root.append(item.dumpxml())

        return root


class PolarionContainer(ABC):
    def __init__(self, config: PolarionConfig) -> None:
        self.config: PolarionConfig = config

    @abstractproperty
    @property
    def properties(self) -> PolarionProperties:
        pass


class PolarionTestCaseContainer(PolarionContainer):
    def __init__(self, config: PolarionConfig, data: OutputData) -> None:
        super().__init__(config)

        self.data: OutputData = data
        self.testcases: list[PolarionTestCase] = [PolarionTestCase(self.config, x) for x in data.items.values()]

    @property
    def properties(self) -> PolarionProperties:
        custom = self.config.testcase.get("properties", {})
        if custom is None:
            custom = {}

        lookup_method = {"lookup-method": self.config.lookup_method}
        if self.config.lookup_method == "custom":
            lookup_method["polarion-custom-lookup-method-field-id"] = self.config.lookup_method_field_id

        properties: dict[str, Any] = {
            "dry-run": self.config.dry_run,
            **lookup_method,
            **custom,
        }

        return PolarionProperties(dict(sorted(properties.items())))

    def dumpxml(self) -> ET.ElementTree:
        root = ET.Element("testcases", {"project-id": self.config.project})
        root.append(self.properties.dumpxml())

        for tc in self.testcases:
            root.append(tc.dumpxml())

        return ET.ElementTree(root)


class PolarionTestCase(object):
    def __init__(self, config: PolarionConfig, item: OutputDataItem) -> None:
        self.config: PolarionConfig = config
        self.item: OutputDataItem = item

        self.__fields: PolarionFields | None = None
        self.__steps: PolarionSteps | None = None
        self.__work_items: PolarionWorkItems | None = None

    @property
    def id(self) -> str:
        if "id" in self.fields and self.fields["id"].value is not None:
            return self.fields["id"].value

        return self.item.id

    @property
    def title(self) -> str:
        if "title" in self.fields and self.fields["title"].value is not None:
            return self.fields["title"].value

        return self.item.id

    @property
    def status(self) -> str:
        if "status" in self.fields and self.fields["status"].value is not None:
            return self.fields["status"].value

        return "approved"

    @property
    def description(self) -> str:
        extra: str = ""
        for data in self.item.extra.values():
            for key, value in data.items():
                extra += f"{key}: {value}"
                extra += "\n"

        if extra:
            extra += "\n"

        return f"{self._get_parametrization()}<pre>{extra}{str(self.item.description)}</pre>"

    @property
    def steps(self) -> PolarionSteps:
        if self.__steps is not None:
            return self.__steps

        steps = self.fields.get("steps", None)
        results = self.fields.get("expectedresults", None)

        self.__steps = PolarionSteps(self.id, steps, results)
        return self.__steps

    @property
    def work_items(self) -> PolarionWorkItems:
        if self.__work_items is not None:
            return self.__work_items

        items: list[str] = []
        requirement = self.fields.get("requirement", None)
        if requirement is not None and requirement.value is not None:
            items.append(requirement.value)

        self.__work_items = PolarionWorkItems(items)
        return self.__work_items

    @property
    def fields(self) -> PolarionFields:
        if self.__fields is not None:
            return self.__fields

        required = self.config.testcase.get("required", {})
        optional = self.config.testcase.get("optional", {})

        self.__fields = PolarionFields(self.config, self.item, required, optional)
        return self.__fields

    def _get_parametrization(self) -> str:
        if not hasattr(self.item.item, "callspec"):
            # The test was not parametrized with @pytest.mark.parametrize
            return ""

        out = "<div><strong>Parametrized arguments:</strong><ul>"
        for arg, value in self.item.item.callspec.params.items():
            out += f"<li><strong>{arg}</strong>: {str(value)}</li>"
        out += "</ul></div>"

        return out

    def dumpxml(self) -> ET.Element:
        root = ET.Element("testcase", {"id": self.id, "status-id": self.status})

        title = ET.SubElement(root, "title")
        title.text = str(self.title)

        description = ET.SubElement(root, "description")
        description.text = str(self.description)

        root.append(self.steps.dumpxml())
        root.append(self.fields.dumpxml())
        root.append(self.work_items.dumpxml())

        return root


class PolarionTestRunContainer(PolarionContainer):
    def __init__(self, config: PolarionConfig, data: OutputData) -> None:
        super().__init__(config)

        self.data: OutputData = data
        self.testruns: list[PolarionTestRun] = [PolarionTestRun(self.config, x) for x in data.items.values()]

    @property
    def properties(self) -> PolarionProperties:
        custom = self.config.testrun.get("properties", {})
        if custom is None:
            custom = {}

        lookup_method = {"polarion-lookup-method": self.config.lookup_method}
        if self.config.lookup_method == "custom":
            lookup_method["polarion-custom-lookup-method-field-id"] = self.config.lookup_method_field_id

        properties = {
            "polarion-create-defects": self.config.create_defects,
            "polarion-dry-run": self.config.dry_run,
            "polarion-group-id": self.config.testrun_group_id,
            "polarion-include-skipped": self.config.include_skipped,
            "polarion-project-id": self.config.project,
            "polarion-project-span-ids": self.config.project_span_ids,
            "polarion-testrun-id": self.config.testrun_id,
            "polarion-testrun-status-id": "finished",
            "polarion-testrun-template-id": self.config.testrun_template_id,
            "polarion-testrun-title": self.config.testrun_title,
            "polarion-testrun-type-id": self.config.testrun_type_id,
            "polarion-user-id": self.config.user,
            **lookup_method,
            **custom,
            **self.config.testrun_properties,
        }

        return PolarionProperties(dict(sorted(properties.items())))

    def dumpxml(self) -> ET.ElementTree:
        results = Counter([x.result.outcome for x in self.testruns])
        duration = sum([x.result.duration for x in self.testruns])

        root = ET.Element("testsuites")
        root.append(self.properties.dumpxml())

        suite = ET.SubElement(
            root,
            "testsuite",
            errors=str(results[Outcome.ERROR]),
            failures=str(results[Outcome.FAILED]),
            skipped=str(results[Outcome.SKIPPED]),
            tests=str(len(self.testruns)),
            time=str(duration),
        )
        for tr in self.testruns:
            suite.append(tr.dumpxml())

        return ET.ElementTree(root)


class PolarionTestRun(object):
    def __init__(self, config: PolarionConfig, item: OutputDataItem) -> None:
        if item.result is None:
            raise ValueError(f"Result is not available for {item.id}!")

        self.config: PolarionConfig = config
        self.item = item
        self.result = item.result
        self.testcase = PolarionTestCase(config, item)

    def dumpxml(self) -> ET.Element:
        if self.item.result is None:
            raise ValueError(f"Result is not available for {self.item.id}!")

        attrs = {
            "file": self.item.location.file,
            "line": str(self.item.location.line),
            "name": self.item.name,
            "time": str(self.item.result.duration),
        }

        if self.item.cls is not None:
            attrs["classname"] = self.item.cls

        root = ET.Element("testcase", attrs)

        if self.result.stdout:
            stdout = ET.SubElement(root, "system-out")
            stdout.text = str(self.result.stdout)

        if self.result.stderr:
            stderr = ET.SubElement(root, "system-err")
            stderr.text = str(self.result.stderr)

        match self.result.outcome:
            case Outcome.SKIPPED:
                el = ET.SubElement(root, "skipped", message=self.result.summary)
                el.text = self.result.message
            case Outcome.FAILED:
                el = ET.SubElement(root, "failure", message=self.result.summary)
                el.text = self.result.message
            case Outcome.ERROR:
                el = ET.SubElement(root, "error", message=self.result.summary)
                el.text = self.result.message

        properties = PolarionProperties({"polarion-testcase-id": self.testcase.id})
        root.append(properties.dumpxml())

        return root


class PolarionOutput(OutputGenerator):
    """
    Output test run and test case XMLs ready to import in Polarion.

    This generator is based on Betelgeuse project.
    """

    def __init__(self) -> None:
        super().__init__()
        self.config: PolarionConfig | None = None
        self.testcase_path: str | None = None
        self.testrun_path: str | None = None

    def pytest_addoption(self, parser: pytest.Parser):
        parser.addoption("--polarion-config", action="store", help="Path to the Polarion configuration file")
        parser.addoption(
            "--output-polarion-testcase", action="store", help="Path to the output Polarion testcase file"
        )
        parser.addoption("--output-polarion-testrun", action="store", help="Path to the output Polarion testrun file")

        parser.addoption("--polarion-project", help="Polarion project ID", default=None)
        parser.addoption("--polarion-user", help="Polarion user", default=None)
        parser.addoption("--polarion-tests-url", help="Tests URL", default=None)
        parser.addoption(
            "--polarion-create-defects",
            action=argparse.BooleanOptionalAction,
            help="Make the importer create defects for failed tests (False)",
            default=False,
        )
        parser.addoption(
            "--polarion-dry-run",
            action=argparse.BooleanOptionalAction,
            help="Indicate to the importer to not make any change (False)",
            default=False,
        )
        parser.addoption(
            "--polarion-include-skipped",
            action=argparse.BooleanOptionalAction,
            help="The importer will include skipped tests (True)",
            default=True,
        )
        parser.addoption(
            "--polarion-lookup-method",
            choices=["id", "custom"],
            help="Indicate to the importer which lookup method to use. 'id' for "
            + "work 'item id or 'custom' for custom id (default)",
            default="custom",
        )
        parser.addoption(
            "--polarion-lookup-method-field-id",
            help="Indicates to the importer which field ID to use when using "
            + "the 'custom' id lookup method (testCaseID)",
            default="testCaseID",
        )
        parser.addoption("--polarion-testrun-id", help="Polarion test run ID", default="test-run-{now}")
        parser.addoption("--polarion-testrun-group-id", help="Polarion test run group ID", default=None)
        parser.addoption("--polarion-testrun-template-id", help="Polarion test run template ID", default=None)
        parser.addoption("--polarion-testrun-title", help="Polarion test run title", default=None)
        parser.addoption("--polarion-testrun-type-id", help="Polarion test run type ID", default=None)
        parser.addoption(
            "--polarion-project-span-ids",
            help="A comma-separated list of project IDs used to set the project span field on the test run",
            default=None,
        )
        parser.addoption(
            "--polarion-testrun-property",
            action=KeyValueAction,
            nargs="*",
            help="Custom testrun property in key=value format",
            default={},
        )
        parser.addoption(
            "--polarion-testrun-property-json",
            action=JSONAction,
            nargs="*",
            help='Custom testrun property in JSON format {"key": "value", ...}',
            default={},
        )

    def pytest_configure(self, pytest_config: pytest.Config):
        # Read output paths
        self.testcase_path = pytest_config.getoption("output_polarion_testcase")
        self.testrun_path = pytest_config.getoption("output_polarion_testrun")

        # Read configuration
        config_path = pytest_config.getoption("polarion_config")
        if config_path is None:
            if any([self.testcase_path, self.testrun_path]):
                raise ValueError(
                    "Polarion output was requested but no configuration file was given. "
                    "Please use --polarion-config=config-path."
                )
            return

        self.config = PolarionConfig(pytest_config, config_path)

    def write_xml(self, path: str, tree: ET.ElementTree) -> None:
        if not tree.getroot():
            return

        ET.indent(tree, space="  ")
        tree.write(path, encoding="utf-8", xml_declaration=True)

    def generate(self, data: OutputData) -> None:
        if self.config is None:
            return

        if self.testcase_path:
            testcase = PolarionTestCaseContainer(self.config, data)
            self.write_xml(self.testcase_path, testcase.dumpxml())

        if self.testrun_path and data.mode == "run":
            testrun = PolarionTestRunContainer(self.config, data)
            self.write_xml(self.testrun_path, testrun.dumpxml())
