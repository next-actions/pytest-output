pytest-output - output tests in various formats
###############################################

Gathers information about tests and test runs and stores it in a
well-defined intermediary data class which can then be transformed into
various output formats.

Added custom hook:

* pytest_output_item_collected - run when an item is collected, can be used
  to provide additional information

.. toctree::
   :maxdepth: 2

   outputs
   api
