from __future__ import annotations

import pytest
from pytest import FixtureRequest, Pytester

from pytest_output.output import OutputDataItem


def test_output_data_item__function(request: FixtureRequest, output_data_item: OutputDataItem) -> None:
    assert output_data_item.item == request.node
    assert output_data_item.id == request.node.nodeid
    assert output_data_item.name == request.node.name
    assert output_data_item.package == "tests"
    assert output_data_item.module == "tests.test_output_data_item"
    assert output_data_item.location.file == "tests/test_output_data_item.py"
    assert output_data_item.name == "test_output_data_item__function"

    assert output_data_item.cls is None
    assert output_data_item.result is None

    assert not output_data_item.description
    assert not output_data_item.docstring
    assert not output_data_item.meta
    assert not output_data_item.markers
    assert not output_data_item.extra


def test_output_data_item__docstring(request: FixtureRequest, output_data_item: OutputDataItem) -> None:
    """
    Test docstring.
    """
    assert output_data_item.description == request.node.obj.__doc__.strip()
    assert output_data_item.docstring == ["Test docstring."]


def test_output_data_item__meta(output_data_item: OutputDataItem) -> None:
    """
    Test docstring.

    :field1: Value 1.
    :field2: Value 2.
    :multiline1:
      1/Line 1.
      1/Line 2.
    :field3: Value 3.
    :multiline2:
      2/Line 1.
      2/Line 2.

    Note: side note

    :multiline3:
      3/Line 1.
      3/Line 2.
    """
    assert "field1" in output_data_item.meta
    assert output_data_item.meta["field1"] == "Value 1."
    assert "field2" in output_data_item.meta
    assert output_data_item.meta["field2"] == "Value 2."
    assert "field3" in output_data_item.meta
    assert output_data_item.meta["field3"] == "Value 3."
    assert "multiline1" in output_data_item.meta
    assert output_data_item.meta["multiline1"] == "1/Line 1.\n1/Line 2."
    assert "multiline2" in output_data_item.meta
    assert output_data_item.meta["multiline2"] == "2/Line 1.\n2/Line 2."
    assert "multiline3" in output_data_item.meta
    assert output_data_item.meta["multiline3"] == "3/Line 1.\n3/Line 2."


@pytest.mark.func1()
@pytest.mark.func2(1, 2, 3)
@pytest.mark.func3(kw1=1, kw2=2, kw3=3)
def test_output_data_item__markers(request: FixtureRequest, output_data_item: OutputDataItem) -> None:
    for m in request.node.iter_markers():
        assert m in output_data_item.markers

    assert len(output_data_item.markers) == len(list(request.node.iter_markers()))


class TestOutputDataItem:
    def test_output_data_item__class(self, request: FixtureRequest, output_data_item: OutputDataItem) -> None:
        assert output_data_item.item == request.node
        assert output_data_item.id == request.node.nodeid
        assert output_data_item.name == request.node.name
        assert output_data_item.package == "tests"
        assert output_data_item.module == "tests.test_output_data_item"
        assert output_data_item.location.file == "tests/test_output_data_item.py"
        assert output_data_item.name == "test_output_data_item__class"

        assert output_data_item.cls == "TestOutputDataItem"
        assert output_data_item.result is None

        assert not output_data_item.description
        assert not output_data_item.docstring
        assert not output_data_item.meta
        assert not output_data_item.markers
        assert not output_data_item.extra


class TestOutputDataItemDocstring:
    """
    Class docstring.
    """

    def test_output_data_item__class_docstring(
        self, request: FixtureRequest, output_data_item: OutputDataItem
    ) -> None:
        """
        Test docstring.
        """
        assert output_data_item.description == request.node.obj.__doc__.strip()
        assert output_data_item.docstring == ["Class docstring.", "Test docstring."]


class TestOutputDataItemMeta:
    """
    Class docstring.

    :field1: Class value 1.
    :class2: Class value 2.
    """

    def test_output_data_item__class_meta(self, output_data_item: OutputDataItem) -> None:
        """
        Test docstring.

        :field1: Value 1.
        :field2: Value 2.
        """
        assert "field1" in output_data_item.meta
        assert output_data_item.meta["field1"] == "Value 1."
        assert "field2" in output_data_item.meta
        assert output_data_item.meta["field2"] == "Value 2."
        assert "class2" in output_data_item.meta
        assert output_data_item.meta["class2"] == "Class value 2."


@pytest.mark.class1()
@pytest.mark.class2(1, 2, 3)
@pytest.mark.class3(kw1=1, kw2=2, kw3=3)
class TestOutputDataItemMarkers:
    @pytest.mark.func1()
    @pytest.mark.func2(1, 2, 3)
    @pytest.mark.func3(kw1=1, kw2=2, kw3=3)
    def test_output_data_item__class_markers(self, request: FixtureRequest, output_data_item: OutputDataItem) -> None:
        for m in request.node.iter_markers():
            assert m in output_data_item.markers

        assert len(output_data_item.markers) == len(list(request.node.iter_markers()))


def test_output_data_item__module_docstring(
    pytester: Pytester, request: FixtureRequest, output_data_item: OutputDataItem
) -> None:
    pytester.makepyfile(
        """
        '''
        Module docstring.
        '''

        def test_output_data_item__module_docstring(request, output_data_item) -> None:
            '''
            Test docstring.
            '''
            assert output_data_item.description == request.node.obj.__doc__.strip()
            assert output_data_item.docstring == ["Module docstring.", "Test docstring."]

        class TestClass:
            '''
            Class docstring.
            '''

            def test_output_data_item__module_class_docstring(self, request, output_data_item) -> None:
                '''
                Test docstring.
                '''
                assert output_data_item.description == request.node.obj.__doc__.strip()
                assert output_data_item.docstring == ["Module docstring.", "Class docstring.", "Test docstring."]
        """
    )

    result = pytester.runpytest()
    result.assert_outcomes(passed=2)


def test_output_data_item__package_docstring(
    pytester: Pytester, request: FixtureRequest, output_data_item: OutputDataItem
) -> None:
    pytester.makepyfile(
        __init__="""
        '''
        Package docstring.
        '''
    """
    )

    pytester.makepyfile(
        test_module="""
        '''
        Module docstring.
        '''

        def test_output_data_item__package_module_docstring(request, output_data_item) -> None:
            '''
            Test docstring.
            '''
            assert output_data_item.description == request.node.obj.__doc__.strip()
            assert output_data_item.docstring == ["Package docstring.", "Module docstring.", "Test docstring."]

        class TestClass:
            '''
            Class docstring.
            '''

            def test_output_data_item__package_module_class_docstring(self, request, output_data_item) -> None:
                '''
                Test docstring.
                '''
                assert output_data_item.description == request.node.obj.__doc__.strip()
                assert output_data_item.docstring == [
                    "Package docstring.",
                    "Module docstring.",
                    "Class docstring.",
                    "Test docstring.",
                ]
        """
    )

    pytester.makepyfile(
        """
        def test_output_data_item__package_docstring(request, output_data_item) -> None:
            '''
            Test docstring.
            '''
            assert output_data_item.description == request.node.obj.__doc__.strip()
            assert output_data_item.docstring == ["Package docstring.", "Test docstring."]

        class TestClass:
            '''
            Class docstring.
            '''

            def test_output_data_item__package_class_docstring(self, request, output_data_item) -> None:
                '''
                Test docstring.
                '''
                assert output_data_item.description == request.node.obj.__doc__.strip()
                assert output_data_item.docstring == ["Package docstring.", "Class docstring.", "Test docstring."]
        """
    )

    result = pytester.runpytest()
    result.assert_outcomes(passed=4)


def test_output_data_item__module_meta(
    pytester: Pytester, request: FixtureRequest, output_data_item: OutputDataItem
) -> None:
    pytester.makepyfile(
        """
        '''
        :module1: Module 1.
        :field1: Module field 1.
        '''

        def test_output_data_item__module_meta(output_data_item) -> None:
            '''
            :field1: Value 1.
            :field2: Value 2.
            '''
            assert "field1" in output_data_item.meta
            assert output_data_item.meta["field1"] == "Value 1."
            assert "field2" in output_data_item.meta
            assert output_data_item.meta["field2"] == "Value 2."
            assert "module1" in output_data_item.meta
            assert output_data_item.meta["module1"] == "Module 1."

        class TestClass:
            '''
            :module1: Class 1.
            '''

            def test_output_data_item__module_class_meta(self, request, output_data_item) -> None:
                '''
                :field1: Value 1.
                :field2: Value 2.
                '''
                assert "field1" in output_data_item.meta
                assert output_data_item.meta["field1"] == "Value 1."
                assert "field2" in output_data_item.meta
                assert output_data_item.meta["field2"] == "Value 2."
                assert "module1" in output_data_item.meta
                assert output_data_item.meta["module1"] == "Class 1."
        """
    )

    result = pytester.runpytest()
    result.assert_outcomes(passed=2)


def test_output_data_item__package_meta(
    pytester: Pytester, request: FixtureRequest, output_data_item: OutputDataItem
) -> None:
    pytester.makepyfile(
        __init__="""
        '''
        :package1: Package 1.
        :package2: Package 2.
        :field1: Package value 1.
        '''
    """
    )

    pytester.makepyfile(
        test_module="""
        '''
        :package1: Module package 1.
        :module1: Module 1.
        :field1: Module field 1.
        '''

        def test_output_data_item__package_module_meta(request, output_data_item) -> None:
            '''
            :field1: Value 1.
            :field2: Value 2.
            '''
            assert "field1" in output_data_item.meta
            assert output_data_item.meta["field1"] == "Value 1."
            assert "field2" in output_data_item.meta
            assert output_data_item.meta["field2"] == "Value 2."
            assert "module1" in output_data_item.meta
            assert output_data_item.meta["module1"] == "Module 1."
            assert "package1" in output_data_item.meta
            assert output_data_item.meta["package1"] == "Module package 1."
            assert "package2" in output_data_item.meta
            assert output_data_item.meta["package2"] == "Package 2."

        class TestClass:
            '''
            :module1: Class 1.
            '''

            def test_output_data_item__package_module_class_meta(self, request, output_data_item) -> None:
                '''
                :field1: Value 1.
                :field2: Value 2.
                '''
                assert "field1" in output_data_item.meta
                assert output_data_item.meta["field1"] == "Value 1."
                assert "field2" in output_data_item.meta
                assert output_data_item.meta["field2"] == "Value 2."
                assert "module1" in output_data_item.meta
                assert output_data_item.meta["module1"] == "Class 1."
                assert "package1" in output_data_item.meta
                assert output_data_item.meta["package1"] == "Module package 1."
                assert "package2" in output_data_item.meta
                assert output_data_item.meta["package2"] == "Package 2."
        """
    )

    result = pytester.runpytest()
    result.assert_outcomes(passed=2)
