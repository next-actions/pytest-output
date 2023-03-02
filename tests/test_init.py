from __future__ import annotations

import pytest


def test_init(pytester: pytest.Pytester):
    """Make sure that the plugin is automatically loaded."""
    pytester.makeconftest("")
    pytester.makepyfile(
        """
        def test_loaded(request):
            assert request.config.pluginmanager.getplugin('pytest_output') is not None
        """
    )

    # run all tests with pytest
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)
