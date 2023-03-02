from __future__ import annotations

import os
import re
import shutil
from pathlib import Path

from pytest import Pytester


def assert_filematch(real: Path, expected: Path) -> None:
    def _escape_contents(contents: str) -> str:
        out = re.sub(r"<((testsuite|testcase) [^>]* time=\")([^>\"]*)(\"[^>]*)>", r"<\1test-time\4>", contents)
        out = re.sub(r"/tmp/pytest-of-[^/]+/pytest-\d+/", r"/pytest/", out)

        return out

    with open(real, "r") as freal:
        with open(expected, "r") as fexpected:
            assert _escape_contents(freal.read()) == _escape_contents(fexpected.read())


def assert_testcase(tmp_path: Path, testdatadir: Path, name: str = "expected_testcase.xml") -> None:
    assert_filematch(real=tmp_path / "testcase.xml", expected=testdatadir / name)


def assert_testrun(tmp_path: Path, testdatadir: Path, name: str = "expected_testrun.xml") -> None:
    assert_filematch(real=tmp_path / "testrun.xml", expected=testdatadir / name)


def copy_results(tmp_path: Path, testdatadir: Path) -> None:
    if "PYTEST_POLARION_COPY_RESULTS" not in os.environ:
        return

    if not os.path.exists(testdatadir):
        os.mkdir(testdatadir)

    shutil.copyfile(tmp_path / "testrun.xml", testdatadir / "expected_testrun.xml")
    shutil.copyfile(tmp_path / "testcase.xml", testdatadir / "expected_testcase.xml")


def test_outputs_polarion__empty_config(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(".yaml", polarion="")
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            pass
        """
    )

    pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
    )
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__cli_project(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(".yaml", polarion="")
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            pass
        """
    )

    pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
        "--polarion-project=test-project",
    )
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__cli_project_span_ids(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(".yaml", polarion="")
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            pass
        """
    )

    pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
        "--polarion-project-span-ids=id1,id2",
    )
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__cli_user(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(".yaml", polarion="")
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            pass
        """
    )

    pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
        "--polarion-user=test-user",
    )
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__cli_tests_url(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(
        ".yaml",
        polarion="""
            testcase:
              optional:
                automation_script:
                  default: "{{ tests_url }}/{{ item.location.file }}#L{{ item.location.line }}"
        """,
    )
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            pass
        """
    )

    pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
        "--polarion-tests-url=http://tests.test",
    )
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__cli_dry_run(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(".yaml", polarion="")
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            pass
        """
    )

    pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
        "--polarion-dry-run",
    )
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__cli_create_defects(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(".yaml", polarion="")
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            pass
        """
    )

    pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
        "--polarion-create-defects",
    )
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__cli_include_skipped(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(".yaml", polarion="")
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            pass
        """
    )

    pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
        "--polarion-include-skipped",
    )
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__cli_lookup_method__id(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(".yaml", polarion="")
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            pass
        """
    )

    pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
        "--polarion-lookup-method=id",
    )
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__cli_lookup_method__custom(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(".yaml", polarion="")
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            pass
        """
    )

    pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
        "--polarion-lookup-method=custom",
        "--polarion-lookup-method-field-id=test-id",
    )
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__cli_testrun_group_id(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(".yaml", polarion="")
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            pass
        """
    )

    pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
        "--polarion-testrun-group-id=test-group-id",
    )
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__cli_testrun_template_id(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(".yaml", polarion="")
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            pass
        """
    )

    pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
        "--polarion-testrun-template-id=test-template-id",
    )
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__cli_testrun_title(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(".yaml", polarion="")
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            pass
        """
    )

    pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
        "--polarion-testrun-title=test-title",
    )
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__cli_testrun_type_id(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(".yaml", polarion="")
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            pass
        """
    )

    pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
        "--polarion-testrun-type-id=test-type-id",
    )
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__cli_testrun_property(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(".yaml", polarion="")
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            pass
        """
    )

    pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
        "--polarion-testrun-property=property1=value1",
        "--polarion-testrun-property=property2=value2",
    )
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__cli_testrun_property_json(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(".yaml", polarion="")
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            pass
        """
    )

    pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
        '--polarion-testrun-property-json={"property1":"value1","property2":"value2"}',
    )
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__field__value(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(
        ".yaml",
        polarion="""
            testcase:
              optional:
                test-field:
        """,
    )
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            '''
            :test-field: value
            '''
            pass
        """
    )

    pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
    )
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__field__meta(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(
        ".yaml",
        polarion="""
            testcase:
              optional:
                test-field:
                  meta: test-name
        """,
    )
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            '''
            :test-name: value
            '''
            pass
        """
    )

    pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
    )
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__field__validate(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(
        ".yaml",
        polarion="""
            testcase:
              optional:
                test-field:
                  validate: regex
        """,
    )
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            '''
            :test-field: value
            '''
            pass
        """
    )

    result = pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
    )
    result.stderr.fnmatch_lines(
        "ValueError: Field 'test-field' did not validate with 'regex' for 'test_polarion.py::test_polarion'"
    )


def test_outputs_polarion__field__transform__unless__true(
    pytester: Pytester, tmp_path: Path, testdatadir: Path
) -> None:
    pytester.makefile(
        ".yaml",
        polarion="""
            testcase:
              optional:
                test-field:
                  transform:
                    unless: value
                    pattern: .*
                    replace: test-replace
        """,
    )
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            '''
            :test-field: value
            '''
            pass
        """
    )

    pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
    )
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__field__transform__unless__false(
    pytester: Pytester, tmp_path: Path, testdatadir: Path
) -> None:
    pytester.makefile(
        ".yaml",
        polarion="""
            testcase:
              optional:
                test-field:
                  transform:
                    unless: notvalue
                    pattern: value
                    replace: test-replace
        """,
    )
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            '''
            :test-field: value
            '''
            pass
        """
    )

    pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
    )
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__field__transform__regex(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(
        ".yaml",
        polarion="""
            testcase:
              optional:
                test-field:
                  transform:
                    pattern: "^(.*)$"
                    replace: "Testcase: \\\\1"
        """,
    )
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            '''
            :test-field: value
            '''
            pass
        """
    )

    pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
    )
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__field__format__pre(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(
        ".yaml",
        polarion="""
            testcase:
              optional:
                test-field:
                  format: pre
        """,
    )
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            '''
            :test-field: value
            '''
            pass
        """
    )

    pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
    )
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__field__default__no_value(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(
        ".yaml",
        polarion="""
            testcase:
              optional:
                test-field:
                  default: default-value
        """,
    )
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            pass
        """
    )

    pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
    )
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__field__default__empty_value(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(
        ".yaml",
        polarion="""
            testcase:
              optional:
                test-field:
                  default: default-value
        """,
    )
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            '''
            :test-field:
            '''
            pass
        """
    )

    pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
    )
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__field__required__missing(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(
        ".yaml",
        polarion="""
            testcase:
              required:
                test-field:
        """,
    )
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            pass
        """
    )

    result = pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
    )
    result.stderr.fnmatch_lines(
        "ValueError: Required field 'test-field' is missing for 'test_polarion.py::test_polarion'"
    )


def test_outputs_polarion__config__testcase__properties(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(
        ".yaml",
        polarion="""
            testcase:
              properties:
                property1: value1
                property2: value2
        """,
    )
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            pass
        """
    )

    pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
    )
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__config__testrun__properties(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(
        ".yaml",
        polarion="""
            testrun:
              properties:
                property1: value1
                property2: value2
        """,
    )
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            pass
        """
    )

    pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
    )
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__config__project(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(
        ".yaml",
        polarion="""
            project: test-project
        """,
    )
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            pass
        """
    )

    pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
    )
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__config__user(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(
        ".yaml",
        polarion="""
            user: test-user
        """,
    )
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            pass
        """
    )

    pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
    )
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__config__tests_url(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(
        ".yaml",
        polarion="""
            tests_url: http://tests.test
            testcase:
              optional:
                automation_script:
                  default: "{{ tests_url }}/{{ item.location.file }}#L{{ item.location.line }}"
        """,
    )
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            pass
        """
    )

    pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
    )
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__real_test__success(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(
        ".yaml",
        polarion="""
            testcase:
              required:
                title:
                setup:
                  format: pre
                steps:
                expectedresults:
                requirement:
        """,
    )
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            '''
            :title: Test title.
            :setup:
              1. Setup 1
              2. Setup 2
            :steps:
              1. Step 1
              2. Step 2
            :expectedresults:
              1. Result 1
              2. Result 2
            :requirement: TEST-DOC
            '''
            pass
        """
    )

    result = pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
    )
    result.assert_outcomes(passed=1)
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__real_test__failure(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(
        ".yaml",
        polarion="""
            testcase:
              required:
                title:
                setup:
                  format: pre
                steps:
                expectedresults:
                requirement:
        """,
    )
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            '''
            :title: Test title.
            :setup:
              1. Setup 1
              2. Setup 2
            :steps:
              1. Step 1
              2. Step 2
            :expectedresults:
              1. Result 1
              2. Result 2
            :requirement: TEST-DOC
            '''
            assert False
        """
    )

    result = pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
    )
    result.assert_outcomes(failed=1)
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__real_test__error(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(
        ".yaml",
        polarion="""
            testcase:
              required:
                title:
                setup:
                  format: pre
                steps:
                expectedresults:
                requirement:
        """,
    )
    pytester.makepyfile(
        test_polarion="""
        import pytest

        @pytest.fixture
        def make_error():
            raise Exception("Error")

        def test_polarion(make_error):
            '''
            :title: Test title.
            :setup:
              1. Setup 1
              2. Setup 2
            :steps:
              1. Step 1
              2. Step 2
            :expectedresults:
              1. Result 1
              2. Result 2
            :requirement: TEST-DOC
            '''
            pass
        """
    )

    result = pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
    )
    result.assert_outcomes(errors=1)
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__real_test__skipped(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(
        ".yaml",
        polarion="""
            testcase:
              required:
                title:
                setup:
                  format: pre
                steps:
                expectedresults:
                requirement:
        """,
    )
    pytester.makepyfile(
        test_polarion="""
        import pytest

        @pytest.mark.skip
        def test_polarion():
            '''
            :title: Test title.
            :setup:
              1. Setup 1
              2. Setup 2
            :steps:
              1. Step 1
              2. Step 2
            :expectedresults:
              1. Result 1
              2. Result 2
            :requirement: TEST-DOC
            '''
            pass
        """
    )

    result = pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
    )
    result.assert_outcomes(skipped=1)
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__real_test__multiple(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(
        ".yaml",
        polarion="""
            testcase:
              required:
                title:
                setup:
                  format: pre
                steps:
                expectedresults:
                requirement:
        """,
    )
    pytester.makepyfile(
        test_polarion="""
        def test_polarion_1():
            '''
            :title: 1/Test title.
            :setup:
              1. 1/Setup 1
              2. 1/Setup 2
            :steps:
              1. 1/Step 1
              2. 1/Step 2
            :expectedresults:
              1. 1/Result 1
              2. 1/Result 2
            :requirement: 1/TEST-DOC
            '''
            pass


        def test_polarion_2():
            '''
            :title: 2/Test title.
            :setup:
              1. 2/Setup 1
              2. 2/Setup 2
            :steps:
              1. 2/Step 1
              2. 2/Step 2
            :expectedresults:
              1. 2/Result 1
              2. 2/Result 2
            :requirement: 2/TEST-DOC
            '''
            pass


        def test_polarion_3():
            '''
            :title: 3/Test title.
            :setup:
              1. 3/Setup 1
              2. 3/Setup 2
            :steps:
              1. 3/Step 1
              2. 3/Step 2
            :expectedresults:
              1. 3/Result 1
              2. 3/Result 2
            :requirement: 3/TEST-DOC
            '''
            pass
        """
    )

    result = pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
    )
    result.assert_outcomes(passed=3)
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__steps__mismatch(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(
        ".yaml",
        polarion="""
            testcase:
              required:
                steps:
                expectedresults:
        """,
    )
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            '''
            :steps:
              1. Step 1
              2. Step 2
            :expectedresults:
              2. Result 1
              1. Result 2
            '''
            pass
        """
    )

    result = pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
    )
    result.stderr.fnmatch_lines(
        "ValueError: Step index do not match expected result in test_polarion.py::test_polarion (1 != 2)"
    )


def test_outputs_polarion__steps__incomplete_1(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(
        ".yaml",
        polarion="""
            testcase:
              required:
                steps:
                expectedresults:
        """,
    )
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            '''
            :steps:
              1. Step 1
              2. Step 2
            :expectedresults:
              1. Result 1
            '''
            pass
        """
    )

    result = pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
    )
    result.stderr.fnmatch_lines(
        "ValueError: Number of steps and results do not match in test_polarion.py::test_polarion"
    )


def test_outputs_polarion__steps__incomplete_2(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(
        ".yaml",
        polarion="""
            testcase:
              required:
                steps:
                expectedresults:
        """,
    )
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            '''
            :steps:
              1. Step 1
            :expectedresults:
              1. Result 1
              2. Result 2
            '''
            pass
        """
    )

    result = pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
    )
    result.stderr.fnmatch_lines(
        "ValueError: Number of steps and results do not match in test_polarion.py::test_polarion"
    )


def test_outputs_polarion__steps__valid(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(
        ".yaml",
        polarion="""
            testcase:
              required:
                steps:
                expectedresults:
        """,
    )
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            '''
            :steps:
              1. Step 1
              2. Step 2
            :expectedresults:
              1. Result 1
              2. Result 2
            '''
            pass
        """
    )

    pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
    )
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__title__singleline(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(
        ".yaml",
        polarion="""
            testcase:
              required:
                title:
        """,
    )
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            '''
            :title: Single line title
            '''
            pass
        """
    )

    pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
    )
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)


def test_outputs_polarion__title__multiline(pytester: Pytester, tmp_path: Path, testdatadir: Path) -> None:
    pytester.makefile(
        ".yaml",
        polarion="""
            testcase:
              required:
                title:
        """,
    )
    pytester.makepyfile(
        test_polarion="""
        def test_polarion():
            '''
            :title: Multi line title
              Second line.
            '''
            pass
        """
    )

    pytester.runpytest(
        "--polarion-config=polarion.yaml",
        f"--output-polarion-testcase={tmp_path}/testcase.xml",
        f"--output-polarion-testrun={tmp_path}/testrun.xml",
        "--polarion-testrun-id=test-run-id",
    )
    copy_results(tmp_path, testdatadir)
    assert_testcase(tmp_path, testdatadir)
    assert_testrun(tmp_path, testdatadir)
